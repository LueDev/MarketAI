import React from "react";
import StockTable from "./StockTable";

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white p-4 rounded shadow">
        <h2 className="text-xl font-bold">Top Performing Stocks</h2>
        <StockTable />
      </div>
      <div className="bg-white p-4 rounded shadow">
        <h2 className="text-xl font-bold">Sector Overview</h2>
        <p>Placeholder for sector-based insights.</p>
      </div>
    </div>
  );
};

export default Dashboard;
