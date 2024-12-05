// src/pages/StockDetailsPage.tsx
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchStockBySymbol, fetchCandlestickData } from "../services/apiService";
import StockChart from "../components/charts/StockChart";
import TechnicalIndicatorSelector from "../components/charts/TechnicalIndicatorSelector";
import { CandlestickEntry } from "../types";

interface StockChartProps {
    symbol: string;
    data: CandlestickEntry[];
}

const StockDetailsPage: React.FC = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const [stock, setStock] = useState<any>(null);
  const [candlestickData, setCandlestickData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStockDetails = async () => {
      try {
        const stockData = await fetchStockBySymbol(symbol!);
        const candleData = await fetchCandlestickData(symbol!);
        setStock(stockData);
        setCandlestickData(candleData);
      } catch (error) {
        console.error("Failed to fetch stock details:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStockDetails();
  }, [symbol]);

  if (loading) return <div>Loading stock details...</div>;
  if (!stock || !candlestickData) return <div>Stock data not found.</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">
        {stock.name} ({stock.symbol})
      </h1>
      <div className="mt-4">
        <StockChart symbol={symbol!} data={candlestickData} />
      </div>
    </div>
  );
};

export default StockDetailsPage;
