import React, { useState } from "react";
import { useAppContext } from "../../context/AppContext";

const subplotMapping: Record<string, string[]> = {
  "Show All": [
    "candlestick",
    "vwap",
    "ma10",
    "ma50",
    "ema10",
    "ema50",
    "bollingerUpper",
    "bollingerMiddle",
    "bollingerLower",
    "RSI",
    "MACD",
    "MACDSignal",
    "stochastic",
    "Williams_R",
    "pivot",
    "support1",
    "resistance1",
    "volatility",
    "volume",
  ],
  "Price Indicators": ["candlestick", "vwap", "ma10", "ma50", "ema10", "ema50", "bollingerUpper", "bollingerMiddle", "bollingerLower", "pivot", "support1", "resistance1"],
  "Momentum (MACD)": ["MACD", "MACDSignal"],
  Oscillators: ["RSI", "stochastic", "Williams_R"],
  "Volume/Volatility": ["volume", "volatility"],
};

const StockChartSidebar: React.FC = () => {
  const { enabledIndicators, setEnabledIndicators, visibleSubplots, setVisibleSubplots } =
    useAppContext();

  const [noiseLevel, setNoiseLevel] = useState(0.000000000000000016)

  const handleToggleIndicator = (indicator: string) => {
    setEnabledIndicators((prevState) => ({
      ...prevState,
      [indicator]: !prevState[indicator],
    }));
  };

  const handleSubplotChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value;
    setVisibleSubplots(value);

    // Automatically toggle relevant indicators in the sidebar
    const relatedIndicators = subplotMapping[value] || [];
    setEnabledIndicators((prevState) => {
      const updatedState = { ...prevState };
      Object.keys(updatedState).forEach((key) => {
        updatedState[key] = relatedIndicators.includes(key);
      });
      return updatedState;
    });
  };

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col p-4">
      <h2 className="text-lg font-bold mb-4">Prediction Insights</h2>
      <div className="mb-6">
        <label className="block mb-2">Timeframe:</label>
        <select className="w-full p-2 bg-gray-800 text-white rounded">
          <option>1 Day</option>
          <option>5 Days</option>
          <option>15 Days</option>
          <option>30 Days</option>
          <option>45 Days</option>
          <option>60 Days</option>
          <option>90 Days</option>
          <option>180 Days</option>
        </select>
      </div>
      <div className="mb-6">
        <label className="block mb-2">Noise Level:</label>
        <input
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={noiseLevel}
            onChange={(e) => setNoiseLevel(parseFloat(e.target.value))}
            className="w-full p-2 bg-gray-800 text-white rounded"
        />
      </div>
      <button className="w-full bg-blue-500 p-2 rounded text-white mb-6">
        Generate Predictions
      </button>

      <h2 className="text-lg font-bold mb-4">Chart Customization</h2>
      <div className="mb-6">
        <label className="block mb-2">Subplots:</label>
        <select
          value={visibleSubplots}
          onChange={handleSubplotChange}
          className="w-full p-2 bg-gray-800 text-white rounded"
        >
          {Object.keys(subplotMapping).map((subplot) => (
            <option key={subplot} value={subplot}>
              {subplot}
            </option>
          ))}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-2">
        {Object.keys(enabledIndicators).map((indicator) => (
          <label key={indicator} className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={enabledIndicators[indicator]}
              onChange={() => handleToggleIndicator(indicator)}
              className="form-checkbox text-blue-500"
            />
            <span className="capitalize text-sm">{indicator.replace(/([A-Z])/g, " $1")}</span>
          </label>
        ))}
      </div>
    </div>
  );
};

export default StockChartSidebar;
