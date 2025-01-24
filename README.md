# Currency Exchange API

## Overview
This is a Currency Exchange API that provides real-time exchange rates, currency conversion, and historical exchange rate data. It includes automation for daily exchange rate updates using Celery and RabbitMQ, as well as Redis for caching to improve performance.

---

## Features
- **Real-Time Exchange Rates**: Fetch live exchange rates.
- **Supported Currencies**: View supported currencies.
- **Currency Conversion**: Convert amounts between currencies.
- **Historical Exchange Rates**: Access historical data for the past 30 days.
- **Daily Updates**: Automated daily updates from 5 Thai banks (SCB, KBANK, BOT, BBL, TMB).
- **Authentication**: API key-based authentication with two roles (Admin and User).
- **Rate Limiting**: Prevent abuse with 100 requests per hour per user.
- **Caching**: Use Redis to reduce API calls.

---

## Tech Stack
- **Backend**: Flask
- **Task Scheduling**: Celery
- **Message Broker**: RabbitMQ
- **Database**: MySQL
- **Caching**: Redis
- **Containerization**: Docker

---

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed.

### Steps to Run
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd currency-exchange-api
   ```

2. Create a `.env` file at the root level with the following content:
   ```env
   FLASK_ENV=production
   MYSQL_HOST=mysql
   MYSQL_DATABASE=currency_exchange
   MYSQL_USER=app_user
   MYSQL_PASSWORD=app_password
   MYSQL_ROOT_PASSWORD=root_password
   REDIS_HOST=redis
   REDIS_PORT=6379
   CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
   CELERY_RESULT_BACKEND=redis://redis:6379/0
   ```

3. Build and run the application:
   ```bash
   docker-compose up --build
   ```

4. Access the API at `http://localhost:5000`.

5. Access RabbitMQ Management UI at `http://localhost:15672` (default credentials: `guest`/`guest`).

---

## API Endpoints

### 1. **Real-Time Exchange Rates**
**GET** `/exchange-rates`
- **Query Parameters**: `base` (optional, default: `USD`)
- **Response**:
  ```json
  {
    "THB": 35.02,
    "EUR": 0.93,
    "JPY": 120.45
  }
  ```

### 2. **Currency Conversion**
**POST** `/convert`
- **Headers**: `X-API-KEY` (required)
- **Body**:
  ```json
  {
    "from_currency": "USD",
    "to_currency": "THB",
    "amount": 100
  }
  ```
- **Response**:
  ```json
  {
    "converted_amount": 3502
  }
  ```

### 3. **Supported Currencies**
**GET** `/supported-currencies`
- **Response**:
  ```json
  [
    {"id": 1, "currency_code": "USD", "currency_name": "United States Dollar"},
    {"id": 2, "currency_code": "THB", "currency_name": "Thai Baht"}
  ]
  ```

### 4. **Historical Exchange Rates**
**GET** `/historical-rates`
- **Query Parameters**: `base` (e.g., `USD`)
- **Response**:
  ```json
  [
    {"id": 1, "base_currency": "USD", "currency": "THB", "rate": 35.02, "date": "2025-01-23"}
  ]
  ```

### 5. **Admin: Update Rates**
**POST** `/admin/update-rates`
- **Headers**: `X-API-KEY` (Admin required)
- **Body**:
  ```json
  {
    "base_currency": "USD",
    "rates": {
      "THB": 35.50,
      "EUR": 0.95
    }
  }
  ```
- **Response**:
  ```json
  {
    "message": "Exchange rates updated successfully"
  }
  ```

---

## Automation
1. **Daily Updates**:
   - Celery Worker fetches exchange rates daily at midnight using RabbitMQ as the message broker.
   - Logs errors and retries up to 3 times if a failure occurs.

2. **Caching**:
   - Exchange rates are cached in Redis for 30 days to improve performance.

---

## Testing the API
1. Use **Postman** or **cURL** to test the endpoints.
2. Example `cURL` command:
   ```bash
   curl -X GET "http://localhost:5000/exchange-rates?base=USD"
   ```

---

## Troubleshooting
1. **Docker not starting**:
   - Ensure Docker Desktop is running.

2. **Celery Worker not processing tasks**:
   - Check RabbitMQ logs: `docker logs currency_rabbitmq`.

3. **Database connection issues**:
   - Verify `.env` file for correct MySQL credentials.

---

## Authors
- **Ornarin Pridiphetpong**
- **Contact**: pr.ornarin@email.com
