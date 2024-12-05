// src/components/charts/TechnicalIndicatorSelector.tsx
import React, { useState } from "react";

const TechnicalIndicatorSelector: React.FC = () => {
  const [selectedIndicators, setSelectedIndicators] = useState<string[]>([]);

  const toggleIndicator = (indicator: string) => {
    setSelectedIndicators((prev) =>
      prev.includes(indicator)
        ? prev.filter((ind) => ind !== indicator)
        : [...prev, indicator]
    );
  };

  return (
    <div className="mt-4">
      <h2 className="text-lg font-bold">Technical Indicators</h2>
      <div className="mt-2 flex gap-2">
        {["RSI", "MACD", "Bollinger Bands", "Moving Average"].map((indicator) => (
          <button
            key={indicator}
            onClick={() => toggleIndicator(indicator)}
            className={`px-4 py-2 border rounded ${
              selectedIndicators.includes(indicator)
                ? "bg-blue-500 text-white"
                : "bg-gray-100"
            }`}
          >
            {indicator}
          </button>
        ))}
      </div>
    </div>
  );
};

export default TechnicalIndicatorSelector;
