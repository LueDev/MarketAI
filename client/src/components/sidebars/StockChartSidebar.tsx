import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { useAppContext } from "../../context/AppContext";
import { fetchAnalysisPrediction } from "../../services/apiService";

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
  "Price Indicators": [
    "candlestick",
    "vwap",
    "ma10",
    "ma50",
    "ema10",
    "ema50",
    "bollingerUpper",
    "bollingerMiddle",
    "bollingerLower",
    "pivot",
    "support1",
    "resistance1",
  ],
  "Momentum (MACD)": ["MACD", "MACDSignal"],
  Oscillators: ["RSI", "stochastic", "Williams_R"],
  "Volume/Volatility": ["volume", "volatility"],
};

const StockChartSidebar: React.FC = () => {
  const { enabledIndicators, setEnabledIndicators, visibleSubplots, setVisibleSubplots } =
    useAppContext();

  const location = useLocation();

  // Extract symbol from URL
  const symbol = location.pathname.split("/").pop();

  console.log("Extracted symbol (location.pathname):", symbol);

  const [noiseLevel, setNoiseLevel] = useState(0.016);
  const [timeframe, setTimeframe] = useState(90);
  const [isLoading, setIsLoading] = useState(false);

  const handleGeneratePredictions = async () => {
    if (!symbol) {
      alert("Stock symbol is missing!");
      return;
    }

    try {
      setIsLoading(true);
      const predictions = await fetchAnalysisPrediction(symbol, timeframe, noiseLevel);
      console.log("Predictions:", predictions); // Replace with logic to handle/display predictions
    } catch (error) {
      console.error("Error generating predictions:", error);
      alert("Failed to generate predictions. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleIndicator = (indicator: string) => {
    setEnabledIndicators((prevState) => ({
      ...prevState,
      [indicator]: !prevState[indicator],
    }));
  };

  const handleSubplotChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value;
    setVisibleSubplots(value);

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
        <select
          value={timeframe}
          onChange={(e) => setTimeframe(Number(e.target.value))}
          className="w-full p-2 bg-gray-800 text-white rounded"
        >
          <option value={1}>1 Day</option>
          <option value={5}>5 Days</option>
          <option value={15}>15 Days</option>
          <option value={30}>30 Days</option>
          <option value={45}>45 Days</option>
          <option value={60}>60 Days</option>
          <option value={90}>90 Days</option>
          <option value={180}>180 Days</option>
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
      <button
        onClick={handleGeneratePredictions}
        className={`w-full p-2 rounded text-white mb-6 ${isLoading ? "bg-gray-500" : "bg-blue-500"}`}
        disabled={isLoading}
      >
        {isLoading ? "Loading..." : "Generate Predictions"}
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
