
![Screenshot 2024-12-06 at 4 18 44 PM](https://github.com/user-attachments/assets/00d0c3b9-cf8f-4b82-8755-2cc15cd8a02a)


# 📈 MarketAI: Your Stock Market Prediction Assistant

MarketAI is a cutting-edge stock market prediction platform that empowers users with actionable insights, predictive analytics, and personalized alerts. Built with Flask, SQLAlchemy, and Redis, it integrates machine learning models to forecast stock prices and technical indicators for informed decision-making.

---

## 🚀 Features
- **Stock Predictions**: Forecast future stock prices using **Random Forest** and **LSTM** models.
- **Custom Alerts**: Set personalized alerts based on stock conditions and price movements.
- **Watchlist Management**: Track your favorite stocks and receive real-time updates.
- **Derived Indicators**: Analyze data with calculated features like MA, RSI, MACD, and Bollinger Bands.
- **Efficient Backend**: Redis-powered caching for fast data retrieval and user notifications.

---

## 🛠️ Tech Stack
### Backend
- **Flask**: RESTful API framework for managing data and endpoints.
- **SQLAlchemy**: ORM for database modeling and relational data.
- **Redis**: In-memory caching for high-speed operations and notifications.

### Machine Learning
- **Random Forest**: Robust, interpretable model for historical stock predictions.
- **LSTM**: Sequential model for capturing trends in stock prices.

### Data Sources
- **Yahoo Finance (yFinance)**: Historical and live stock market data.

---

## 📊 Technical Indicators
MarketAI integrates a variety of indicators for enhanced analysis:
- **Moving Averages (MA_10, MA_50)**: Identify trends.
- **Volatility**: Measure price fluctuations.
- **Relative Strength Index (RSI)**: Gauge momentum.
- **MACD**: Signal bullish or bearish trends.
- **Bollinger Bands**: Track price volatility and potential breakouts.
- **Williams %R**: Highlight overbought/oversold conditions.
- **Pivot Points**: Predict support and resistance levels.

---

## 🔧 API Endpoints

### **Authentication**
- **POST /login**: Authenticate users and return a token.

### **User Management**
- **GET /users**: List all users.
- **POST /users**: Create a new user.

### **Stocks**
- **GET /stocks**: Retrieve stock information.
- **POST /stocks**: Add a new stock.

### **Watchlist**
- **GET /watchlist**: Retrieve a user's watchlist.
- **POST /watchlist**: Add a stock to the watchlist.
- **DELETE /watchlist**: Remove a stock from the watchlist.

### **Predictions**
- Predict future stock trends based on historical and recent data.

---

## 📅 Future Enhancements

- **Frontend**: Build an intuitive interface with React.
- **Sentiment Analysis**: Integrate NLP models to gauge market sentiment.
- **Real-Time Data**: Incorporate WebSocket support for live stock updates.
- **Advanced Notifications**: Expand channels to include email and SMS.

---

## 📄 Acknowledgments

- **[Yahoo Finance](https://finance.yahoo.com)** for stock data.
- **[Scikit-Learn](https://scikit-learn.org)** and **[Joblib](https://joblib.readthedocs.io)** for ML tools.
- **Flask** and **SQLAlchemy** communities for their incredible support and resources.
