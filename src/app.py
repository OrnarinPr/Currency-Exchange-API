from flask import Flask, jsonify, request
import mysql.connector
import redis
import requests
import json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import logging
from celery import Celery
from datetime import datetime

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)

# Load environment variables
ENV = os.getenv('FLASK_ENV', 'development')
if ENV == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

# Celery setup
celery = Celery(__name__, broker=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'))
celery.conf.result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

# Rate Limiting setup
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour"])

# Redis client setup
redis_host = os.getenv('REDIS_HOST', 'redis')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Database connection
def get_mysql_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'mysql'),
        user=os.getenv('MYSQL_USER', 'app_user'),
        password=os.getenv('MYSQL_PASSWORD', 'app_password'),
        database=os.getenv('MYSQL_DATABASE', 'currency_exchange')
    )

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fetch exchange rates from Thai banks
@celery.task(bind=True, max_retries=3)
def fetch_exchange_rates(self):
    try:
        banks = {
            "SCB": "https://api.scb.co.th/exchange-rates",
            "KBANK": "https://api.kbank.co.th/exchange-rates",
            "BOT": "https://api.bot.or.th/exchange-rates",
            "BBL": "https://api.bbl.co.th/exchange-rates",
            "TMB": "https://api.tmbbank.com/exchange-rates"
        }

        connection = get_mysql_connection()
        cursor = connection.cursor()

        for bank, url in banks.items():
            response = requests.get(url)
            if response.status_code == 200:
                rates = response.json().get("rates", {})
                for currency, rate in rates.items():
                    # Insert into historical_rates
                    cursor.execute(
                        "INSERT INTO historical_rates (base_currency, currency, rate, date) VALUES (%s, %s, %s, %s)",
                        ("THB", currency, rate, datetime.now().date())
                    )

                    # Update exchange_rates
                    cursor.execute(
                        "REPLACE INTO exchange_rates (base_currency, currency, rate, updated_at) VALUES (%s, %s, %s, NOW())",
                        ("THB", currency, rate)
                    )

        connection.commit()
        connection.close()
        logger.info("Exchange rates updated successfully from all banks.")

    except Exception as e:
        logger.error(f"Error fetching exchange rates: {e}")
        self.retry(exc=e, countdown=60)

# Authenticate API Key and User Role
def authenticate_request(required_role=None):
    api_key = request.headers.get('X-API-KEY')
    if not api_key:
        return jsonify({"error": "API Key is required", "status_code": 401}), 401

    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT user_role FROM api_keys WHERE key_value = %s", (api_key,))
    result = cursor.fetchone()
    connection.close()

    if not result:
        return jsonify({"error": "Invalid API Key", "status_code": 403}), 403

    user_role = result['user_role']
    if required_role and user_role != required_role:
        return jsonify({"error": f"Access denied for role: {user_role}", "status_code": 403}), 403

    return None  # Authentication passed

# Error Handlers
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify({"error": "Resource not found", "status_code": 404}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Internal server error", "status_code": 500}), 500

# Home route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to Currency Exchange API"})

# Real-time exchange rates
@app.route('/exchange-rates', methods=['GET'])
@limiter.limit("100 per hour")
def get_exchange_rates():
    base_currency = request.args.get('base', 'USD')

    # Check Cache
    cache_key = f"exchange_rates:{base_currency}"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return jsonify(json.loads(cached_data))  # Return from Cache

    # Fetch from external API
    url = f"https://open.er-api.com/v6/latest/{base_currency}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        rates = data.get("rates", {})

        # Cache the data with a TTL of 30 days
        redis_client.setex(cache_key, 2592000, json.dumps(rates))  # 30 days = 2592000 seconds

        return jsonify(rates)
    else:
        return jsonify({"error": "Failed to fetch exchange rates", "status_code": response.status_code}), 500

# Currency conversion
@app.route('/convert', methods=['POST'])
@limiter.limit("100 per hour")
def convert_currency():
    auth_error = authenticate_request(required_role="User")
    if auth_error:
        return auth_error

    data = request.json
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')
    amount = data.get('amount')

    if not from_currency or not to_currency or not amount:
        return jsonify({"error": "Missing required fields", "status_code": 400}), 400

    # Get real-time exchange rates
    url = f"https://open.er-api.com/v6/latest/{from_currency}"
    response = requests.get(url)

    if response.status_code == 200:
        rates = response.json().get("rates", {})
        conversion_rate = rates.get(to_currency)

        if conversion_rate:
            converted_amount = amount * conversion_rate
            return jsonify({"converted_amount": converted_amount})
        else:
            return jsonify({"error": f"Currency {to_currency} not supported", "status_code": 400}), 400

    return jsonify({"error": "Failed to fetch exchange rates", "status_code": response.status_code}), 500

# Supported banks and currencies
@app.route('/supported-currencies', methods=['GET'])
@limiter.limit("100 per hour")
def supported_currencies():
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM supported_currencies")
    result = cursor.fetchall()
    connection.close()

    return jsonify(result)

# Historical exchange rates
@app.route('/historical-rates', methods=['GET'])
@limiter.limit("100 per hour")
def historical_rates():
    base_currency = request.args.get('base', 'USD')
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM historical_rates WHERE base_currency = %s ORDER BY date DESC LIMIT 30",
        (base_currency,)
    )
    result = cursor.fetchall()
    connection.close()

    return jsonify(result)

# Admin: Manage banks and currencies
@app.route('/admin/update-rates', methods=['POST'])
@limiter.limit("50 per hour")
def update_rates():
    auth_error = authenticate_request(required_role="Admin")
    if auth_error:
        return auth_error

    data = request.json
    base_currency = data.get('base_currency')
    rates = data.get('rates')

    if not base_currency or not rates:
        return jsonify({"error": "Missing required fields", "status_code": 400}), 400

    connection = get_mysql_connection()
    cursor = connection.cursor()
    for currency, rate in rates.items():
        cursor.execute(
            "REPLACE INTO exchange_rates (base_currency, currency, rate, updated_at) VALUES (%s, %s, %s, NOW())",
            (base_currency, currency, rate)
        )
    connection.commit()
    connection.close()

    return jsonify({"message": "Exchange rates updated successfully"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
