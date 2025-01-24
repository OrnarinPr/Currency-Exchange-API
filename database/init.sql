CREATE DATABASE IF NOT EXISTS currency_exchange;
USE currency_exchange;

-- Set root password (if not already set)
ALTER USER 'root'@'%' IDENTIFIED BY 'root_password';
FLUSH PRIVILEGES;

-- Table for storing API keys and user roles
CREATE TABLE IF NOT EXISTS api_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    key_value VARCHAR(255) NOT NULL UNIQUE,
    user_role ENUM('Admin', 'User') NOT NULL
);

-- Table for supported currencies
CREATE TABLE IF NOT EXISTS supported_currencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    currency_code VARCHAR(10) NOT NULL UNIQUE,
    currency_name VARCHAR(255) NOT NULL
);

-- Table for historical exchange rates
CREATE TABLE IF NOT EXISTS historical_rates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    base_currency VARCHAR(10) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    rate DECIMAL(15, 6) NOT NULL,
    date DATE NOT NULL,
    UNIQUE KEY unique_rate (base_currency, currency, date)
);

-- Table for real-time exchange rates
CREATE TABLE IF NOT EXISTS exchange_rates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    base_currency VARCHAR(10) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    rate DECIMAL(15, 6) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_realtime_rate (base_currency, currency)
);

-- Insert default supported currencies
INSERT IGNORE INTO supported_currencies (currency_code, currency_name) VALUES
('USD', 'United States Dollar'),
('THB', 'Thai Baht'),
('EUR', 'Euro'),
('JPY', 'Japanese Yen');

-- Insert default API keys for testing
INSERT IGNORE INTO api_keys (key_value, user_role) VALUES
('test_admin_key', 'Admin'),
('test_user_key', 'User');
