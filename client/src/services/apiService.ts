// src/services/apiService.ts

import { Stock } from "../types"; // Assuming Stock type is already defined
import { CandlestickEntry } from "../types";

export const fetchStocks = async (): Promise<Stock[]> => {
    const response = await fetch("http://127.0.0.1:10000/stocks");
    if (!response.ok) {
        throw new Error("Failed to fetch stocks");
    }

    const data = await response.json();

    // Transform the API response to match the frontend's expectations
    return data.map((stock: any) => ({
        id: stock.id,
        symbol: stock.symbol,
        name: stock.name,
        sector: stock.sector?.name || "Unknown", // Use sector name or fallback
        currentPrice: stock.analyses.find((analysis: any) => analysis.attribute === "Price")?.value || 0, // Add Price if needed
        volatility: stock.analyses.find((analysis: any) => analysis.attribute === "Volatility")?.value || 0, // Extract volatility
    }));
};


export const fetchStockBySymbol = async (symbol: string) => {
    const response = await fetch(`http://127.0.0.1:10000/stocks/symbol/${symbol}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch stock data for symbol: ${symbol}`);
    }
    return await response.json();
};

export const fetchStocksBySector = async (sectorName: string) => {
    const response = await fetch(`http://127.0.0.1:10000/sectors/${sectorName}/stocks`);
    if (!response.ok) {
        throw new Error(`Failed to fetch stocks for sector: ${sectorName}`);
    }
    return await response.json();
};

export const fetchSectors = async () => {
    const response = await fetch("http://127.0.0.1:10000/sectors");
    if (!response.ok) {
        throw new Error("Failed to fetch sectors");
    }
    return await response.json();
};

export const fetchAnalysisPrediction = async (symbol: string) => {
    const response = await fetch(`http://127.0.0.1:10000/analysis/predict`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ symbol }),
    });
    if (!response.ok) {
        throw new Error(`Failed to fetch prediction for symbol: ${symbol}`);
    }
    return await response.json();
};

export const fetchHistoricalData = async (sector: string, timeframe: string) => {
    const response = await fetch(`http://127.0.0.1:10000/data/historical/${sector}/${timeframe}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch historical data for sector: ${sector} and timeframe: ${timeframe}`);
    }
    return await response.json();
};

export const fetchCandlestickData = async (symbol: string): Promise<CandlestickEntry[]> => {
    const response = await fetch(`http://127.0.0.1:10000/stocks/fetch/${symbol}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch candlestick data for ${symbol}`);
    }
    const json = await response.json();
    return json.data; // Ensure only the 'data' array is returned
};


export const downloadFile = async (url: string, fileName: string) => {
    const response = await fetch(url);
    const blob = await response.blob();
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};
