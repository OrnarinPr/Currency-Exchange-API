# README: Deployment Guide for Currency Exchange API

## Access the Application

To access the Currency Exchange API, use the following Public IPv4 address:

- **API URL:** [http://18.141.12.29](http://18.141.12.29)

## Available Endpoints

### 1. Home Page

- **URL**: [http://18.141.12.29/](http://18.141.12.29/)
- **Method**: `GET`
- **Description**: Displays a welcome message for the API.

### 2. Real-Time Exchange Rates

- **URL**: [http://18.141.12.29/exchange-rates](http://18.141.12.29/exchange-rates)
- **Method**: `GET`
- **Query Parameters**:
  - `base` (optional): Base currency (default: `USD`)
- **Description**: Returns real-time exchange rates.

### 3. Currency Conversion

- **URL**: [http://18.141.12.29/convert](http://18.141.12.29/convert)
- **Method**: `POST`
- **Headers**:
  - `X-API-KEY`: API key for authentication.
- **Payload**:
  ```json
  {
    "from_currency": "THB",
    "to_currency": "USD",
    "amount": 100
  }
  ```
- **Description**: Converts an amount from one currency to another.

### 4. Supported Currencies

- **URL**: [http://18.141.12.29/supported-currencies](http://18.141.12.29/supported-currencies)
- **Method**: `GET`
- **Description**: Returns a list of supported currencies.

### 5. Historical Exchange Rates

- **URL**: [http://18.141.12.29/historical-rates](http://18.141.12.29/historical-rates)
- **Method**: `GET`
- **Query Parameters**:
  - `base` (optional): Base currency (default: `USD`)
- **Description**: Returns historical exchange rates for the last 30 days.

### 6. Admin: Update Rates

- **URL**: [http://18.141.12.29/admin/update-rates](http://18.141.12.29/admin/update-rates)
- **Method**: `POST`
- **Headers**:
  - `X-API-KEY`: Admin API key for authentication.
- **Payload**:
  ```json
  {
    "base_currency": "THB",
    "rates": {
      "USD": 0.029,
      "EUR": 0.025
    }
  }
  ```
- **Description**: Updates exchange rates (Admin only).

## Notes

Ensure you have the correct access credentials or API keys (if required) to interact with the endpoints.
