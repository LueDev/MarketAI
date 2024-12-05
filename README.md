# WallStreetX

WallStreetX is a full-stack stock trading platform that allows users to explore stocks, view historical data, and execute trades seamlessly. This project leverages a Python backend with Flask, SQLAlchemy, and RapidAPI integration for fetching real-time financial data. The frontend is built with React, providing users with an intuitive interface to monitor their portfolio, execute trades, and visualize stock trends using lightweight charts.

---

## Table of Contents
1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Setup Instructions](#setup-instructions)
4. [Backend API Endpoints](#backend-api-endpoints)
5. [Environment Variables](#environment-variables)
6. [Usage](#usage)
7. [Project Structure](#project-structure)
8. [Future Improvements](#future-improvements)
9. [License](#license)
10. [Contributors](#contributors)

---

## Features

- **User Authentication**: Register, login, and logout securely using JWT tokens.
- **Stock Search & Viewing**: Explore stocks and view real-time market data.
- **Historical Data Visualization**: Visualize stock trends over time with candlestick charts.
- **Portfolio Management**: Manage your portfolio by tracking stock holdings.
- **Trade Execution**: Buy or sell stocks, with detailed trade tracking.
- **Secure Data Handling**: Integrates JWT and CORS for secure API interaction.
- **Real-Time Data**: Uses RapidAPI's Yahoo Finance API to fetch market data.

---

## Tech Stack

### Frontend
- **React.js** (with hooks)
- **Axios** (for API requests)
- **Lightweight-charts** library (for stock visualization)

### Backend
- **Python**  
- **Flask** (with Flask-RESTful)  
- **SQLAlchemy** (ORM)  
- **Flask-Bcrypt** (for password hashing)  
- **JWT** (for authentication)  
- **SQLite** (as the database)  
- **Requests** (for API integration)  

---

## Setup Instructions

### Prerequisites
- **Python 3.x** installed  
- **Node.js** & **npm** installed  
- **SQLite** installed (optional)  
- **Git** installed  

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LueDev/WallStreetX.git
   cd WallStreetX
   ```

2. **Create a virtual environment and install dependencies:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```
3. **Create a .env file in the root directory:**
   ```bash
   touch .env
   ```
4. **Add the following environment variables:**
   ```bash
   SECRET_KEY=your-secret-key
   RAPIDAPI_KEY=your-rapidapi-key
   RAPIDAPI_HOST=apidojo-yahoo-finance-v1.p.rapidapi.com
   ```
5. **Initialize the database:**
  ```bash
  flask db upgrade
  ```
6. **Start the Flask server:**
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Navigate to the client directory:**
   ```bash
   cd client
   ```
2. **Install dependencies:**
   ```bash
   npm install
   ```
3. **Start the React development server:**
   ```bash
   npm start
   ```

### Backend API Endpoints
- POST /register: Register a new user
- POST /login: Login and retrieve a JWT token
- POST /logout: Logout and clear session
- GET /api/stocks: Fetch list of available stocks
- GET /api/historical/: Fetch historical data for a stock
- POST /api/trades: Execute a stock trade
- GET /api/portfolio: View the user's portfolio


### Usage
# Register and Login:
Use the /register and /login endpoints to create a user and retrieve a JWT token.

# Fetch Stocks and Historical Data:
Select a stock from the dropdown to view its real-time and historical performance.

# Execute Trades:
Use the trade form to execute buy or sell trades and track them in your portfolio.

# Secure Authentication:
Include the JWT token in the header of each request to protected routes:

```json
{
  "x-access-token": "your-jwt-token"
}
```

### License
This project is licensed under the MIT License - see the LICENSE file for details.

### Contributions 
Luis Jorge - https://github.com/LueDev
