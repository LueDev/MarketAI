import React from "react";
import MetricsCard from "./MetricsCard";

const MetricsSection: React.FC = () => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
      <MetricsCard
        title="RMSE"
        value="Loading..."
        description="Root Mean Squared Error - measures average prediction error"
      />
      <MetricsCard
        title="MAE"
        value="Loading..."
        description="Mean Absolute Error - average magnitude of errors"
      />
      <MetricsCard
        title="Loss"
        value="Loading..."
        description="Overall model error during training"
      />
    </div>
  );
};

export default MetricsSection;
