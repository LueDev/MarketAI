// src/components/CompareStocks.tsx
import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import TradingViewChart from './TradingViewChart';

interface HistoricalData {
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
}

interface StockData {
    symbol: string;
    name: string;
    historicalData: HistoricalData[];
}

const CompareStocks: React.FC = () => {
    const location = useLocation();
    const [stocksData, setStocksData] = useState<StockData[]>([]);
    const queryParams = new URLSearchParams(location.search);
    const stockSymbols = queryParams.get('stocks')?.split(',') || [];

    useEffect(() => {
        const mockStockData = [
            {
                symbol: "AAPL",
                name: "Apple Inc.",
                historicalData: [
                    { date: "2023-10-01", open: 149, high: 151, low: 148, close: 150, volume: 5000000 },
                    { date: "2023-09-30", open: 150, high: 152, low: 149, close: 149, volume: 4500000 },
                ],
            },
            {
                symbol: "JPM",
                name: "JPMorgan Chase",
                historicalData: [
                    { date: "2023-10-01", open: 139, high: 141, low: 138, close: 140, volume: 3000000 },
                    { date: "2023-09-30", open: 140, high: 142, low: 139, close: 139, volume: 3200000 },
                ],
            },
        ];

        // Filter selected stocks and sort historical data by ascending date
        const selectedStockData = mockStockData
            .filter(stock => stockSymbols.includes(stock.symbol))
            .map(stock => ({
                ...stock,
                historicalData: stock.historicalData
                    .slice() // Create a shallow copy
                    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()), // Sort by date
            }));

        setStocksData(selectedStockData);
    }, [stockSymbols]);

    return (
        <div>
            <h1>Compare Stocks</h1>
            <div style={{ display: 'flex', gap: '20px' }}>
                {stocksData.map(stock => (
                    <div key={stock.symbol} style={{ width: '45%' }}>
                        <h2>{stock.name} ({stock.symbol})</h2>
                        <TradingViewChart
                            symbol={stock.symbol}
                            data={stock.historicalData.map(entry => ({
                                time: entry.date,
                                open: entry.open,
                                high: entry.high,
                                low: entry.low,
                                close: entry.close,
                            }))}
                        />
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CompareStocks;
