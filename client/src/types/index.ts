// src/types/index.ts

export interface Indicator {
    id: number;
    name: string;
    influence_score: number; // Influence of the indicator on stock performance
    weight: number; // Weight of the indicator
    description?: string; // Optional description of the indicator
}

export interface Stock {
    id: number;
    name: string;
    symbol: string; // Keeping "symbol" for stock ticker consistency
    sector: string; // Sector name (e.g., "tech", "finance")
    currentPrice: number; // Current price of the stock
    predicted_score?: number; // Optional: Predicted score for the stock
    confidence?: number; // Optional: Confidence score for predictions
    loss?: number; // Optional: Model loss for the stock
    indicators?: Indicator[]; // Optional list of indicators
    volatility?: number; // Optional volatility (e.g., from API "analyses")
}

export interface Sector {
    id: number;
    name: string; // Sector name
    description?: string; // Optional description
    stocks: Stock[]; // List of stocks in the sector
}

export interface User {
    id: number;
    username: string;
    email: string;
    stocks: Stock[]; // Stocks associated with the user
}

export interface CandlestickEntry {
    Date: number;
    Open: number;
    High: number;
    Low: number;
    Close: number;
    Volume: number;
    Dividends: number;
    StockSplits: number;
    VWAP: number;
    MA_10: number | null;
    MA_50: number | null;
    EMA_10: number | null;
    EMA_50: number | null;
    RSI: number | null;
    BB_Lower: number | null;
    BB_Middle: number | null;
    BB_Upper: number | null;
    MACD: number | null;
    MACD_Signal: number | null;
    MACD_Hist: number | null;
    Stochastic: number | null;
    Williams_R: number | null;
    Parabolic_SAR: number | null;
    OBV: number | null;
    Pivot: number | null;
    R1: number | null;
    S1: number | null;
    Volatility: number | null;
  }
  
  export interface CandlestickResponse {
    symbol: string;
    data: CandlestickEntry[];
  }
  