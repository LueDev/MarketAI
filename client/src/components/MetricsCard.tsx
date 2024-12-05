import React from "react";

interface MetricsCardProps {
  title: string;
  value: string | number;
  description: string;
}

const MetricsCard: React.FC<MetricsCardProps> = ({ title, value, description }) => {
  return (
    <div className="bg-white rounded shadow p-4">
      <h3 className="text-lg font-bold">{title}</h3>
      <p className="text-2xl font-bold text-green-500">{value}</p>
      <p className="text-gray-600">{description}</p>
    </div>
  );
};

export default MetricsCard;
