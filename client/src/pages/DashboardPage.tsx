// src/pages/DashboardPage.tsx
import React, { useEffect, useState } from "react";
import StockList from "../components/StockList";
import { fetchStocks } from "../services/apiService";
import { Stock } from "../types"; // Import the Stock type

const DashboardPage: React.FC = () => {
  const [stocks, setStocks] = useState<Stock[]>([]); // Define the state with Stock type
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadStocks = async () => {
      try {
        const data = await fetchStocks();
        setStocks(data); // Assuming the API returns an array of Stock objects
      } catch (err) {
        setError("Failed to load stocks. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    loadStocks();
  }, []);

  if (loading) return <p>Loading stocks...</p>;
  if (error) return <p>{error}</p>;
  if (stocks.length === 0) return <p>No stocks available.</p>;

  return (
    <div className="dashboard-page">
      <h1 className="text-2xl font-bold mb-4">Stock Dashboard</h1>
      <StockList stocks={stocks} />
    </div>
  );
};

export default DashboardPage;
