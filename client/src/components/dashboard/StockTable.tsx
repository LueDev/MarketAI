import React from "react";
import { useNavigate } from "react-router-dom";

interface StockTableProps {
  stocks: any[];
}

const StockTable: React.FC<StockTableProps> = ({ stocks }) => {
  const navigate = useNavigate();

  return (
    <table className="table-auto w-full bg-white rounded-lg shadow">
      <thead className="bg-gray-200">
        <tr>
          <th className="px-4 py-2">Stock Name</th>
          <th className="px-4 py-2">Symbol</th>
          <th className="px-4 py-2">Price</th>
          <th className="px-4 py-2">Volatility</th>
          <th className="px-4 py-2">RSI</th>
          <th className="px-4 py-2">MACD</th>
        </tr>
      </thead>
      <tbody>
        {stocks.map((stock) => (
          <tr
            key={stock.symbol}
            onClick={() => navigate(`/stock/${stock.symbol}`)}
            className="cursor-pointer hover:bg-gray-100"
          >
            <td className="px-4 py-2">{stock.name}</td>
            <td className="px-4 py-2">{stock.symbol}</td>
            <td className="px-4 py-2">${stock.price}</td>
            <td className="px-4 py-2">{stock.volatility}</td>
            <td className="px-4 py-2">{stock.rsi}</td>
            <td className="px-4 py-2">{stock.macd}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default StockTable;
