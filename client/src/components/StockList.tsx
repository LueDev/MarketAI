// src/components/StockList.tsx
import React from "react";
import { Link } from "react-router-dom";
import { Stock } from "../types"; // Import the type here

interface StockListProps {
  stocks: Stock[]; // Use the Stock type for props
}

const StockList: React.FC<StockListProps> = ({ stocks }) => {
  return (
    <div className="stock-list">
      <table className="table-auto w-full text-left border-collapse">
        <thead>
          <tr>
            <th className="px-4 py-2 border">Name</th>
            <th className="px-4 py-2 border">Symbol</th>
            <th className="px-4 py-2 border">Sector</th>
            <th className="px-4 py-2 border">Price</th>
            <th className="px-4 py-2 border">Details</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock) => (
            <tr key={stock.id}>
              <td className="px-4 py-2 border">{stock.name}</td>
              <td className="px-4 py-2 border">{stock.symbol}</td>
              <td className="px-4 py-2 border">{stock.sector}</td>
              <td className="px-4 py-2 border">${stock.currentPrice.toFixed(2)}</td>
              <td className="px-4 py-2 border">
                <Link to={`/stock/${stock.symbol}`} className="text-blue-500 underline">
                  View
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StockList;
