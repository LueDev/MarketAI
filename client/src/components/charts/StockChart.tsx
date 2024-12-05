import Plot from "react-plotly.js";
import { useState, useEffect } from "react";
import { useAppContext } from "../../context/AppContext";
import { CandlestickEntry } from "../../types";

interface StockChartProps {
  symbol: string;
  data: CandlestickEntry[];
}

const StockChart: React.FC<StockChartProps> = ({ symbol, data }) => {
  const { enabledIndicators, visibleSubplots, predictions } = useAppContext();

  const formattedDates = data.map((entry) =>
    new Date(entry.Date).toISOString().split("T")[0]
  );

  const [chartDimensions, setChartDimensions] = useState({
    width: window.innerWidth * 0.7,
    height: window.innerHeight * 0.7,
  });

  // Adjust chart size dynamically on window resize
  useEffect(() => {
    const handleResize = () => {
      setChartDimensions({
        width: window.innerWidth * 0.8,
        height: window.innerHeight * 0.7,
      });
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Determine visibility for each subplot
  const getVisibility = (indicator: string, subplot: string) => {
    if (visibleSubplots === "Show All") return enabledIndicators[indicator];
    return visibleSubplots === subplot && enabledIndicators[indicator];
  };

    // Safely add the prediction trace if predictions exist and match the current symbol
    const predictionTrace =
    predictions && predictions.symbol === symbol
    ? {
        x: predictions.dates,
        y: predictions.data,
        type: "scatter",
        mode: "lines",
        name: "Prediction",
        line: { color: "red", width: 4 },
        xaxis: "x",
        yaxis: "y",
        visible: true, // Always show predictions
        }
    : null;


  return (
    <div>
      <Plot
        data={[
          // Price Indicators
          {
            x: formattedDates,
            open: data.map((entry) => entry.Open),
            high: data.map((entry) => entry.High),
            low: data.map((entry) => entry.Low),
            close: data.map((entry) => entry.Close),
            type: "candlestick",
            name: "Candlestick",
            xaxis: "x",
            yaxis: "y",
            visible: getVisibility("candlestick", "Price Indicators"),
          },
          {
            x: formattedDates,
            y: data.map((entry) => entry.VWAP ?? null),
            type: "scatter",
            mode: "lines",
            name: "VWAP",
            line: { color: "blue" },
            xaxis: "x",
            yaxis: "y",
            visible: getVisibility("vwap", "Price Indicators"),
          },
          predictionTrace, // Add prediction trace conditionally
          {
            x: formattedDates,
            y: data.map((entry) => entry.MA_10 ?? null),
            type: "scatter",
            mode: "lines",
            name: "10-Day MA",
            line: { color: "light green" },
            xaxis: "x",
            yaxis: "y",
            visible: getVisibility("ma10", "Price Indicators"),
          },
          {
            x: formattedDates,
            y: data.map((entry) => entry.MA_50 ?? null),
            type: "scatter",
            mode: "lines",
            name: "50-Day MA",
            line: { color: "dark green" },
            xaxis: "x",
            yaxis: "y",
            visible: getVisibility("ma50", "Price Indicators"),
          },
          {
            x: formattedDates,
            y: data.map((entry) => entry.MA_10 ?? null),
            type: "scatter",
            mode: "lines",
            name: "10-Day MA",
            line: { color: "light green" },
            xaxis: "x",
            yaxis: "y",
            visible: getVisibility("ma10", "Price Indicators"),
          },
          {
            x: formattedDates,
            y: data.map((entry) => entry.MA_50 ?? null),
            type: "scatter",
            mode: "lines",
            name: "50-Day MA",
            line: { color: "dark green" },
            xaxis: "x",
            yaxis: "y",
            visible: getVisibility("ma50", "Price Indicators"),
          },
          {
            x: formattedDates,
            y: data.map((entry) => entry.EMA_10 ?? null),
            type: "scatter",
            mode: "lines",
            name: "10-Day EMA",
            line: { color: "gold" },
            xaxis: "x",
            yaxis: "y",
            visible: getVisibility("ema10", "Price Indicators"),
          },
          {
            x: formattedDates,
            y: data.map((entry) => entry.EMA_50 ?? null),
            type: "scatter",
            mode: "lines",
            name: "50-Day EMA",
            line: { color: "violet" },
            xaxis: "x",
            yaxis: "y",
            visible: getVisibility("ema50", "Price Indicators"),
          },
          {
            x: formattedDates,
            y: data.map((entry) => entry.Pivot ?? null),
            type: "scatter",
            mode: "lines",
            name: "Pivot",
            line: { color: "fuschia" },
            xaxis: "x",
            yaxis: "y",
            visible: getVisibility("pivot", "Price Indicators"),
          },
          {
            x: formattedDates,
            y: data.map((entry) => entry.R1 ?? null),
            type: "scatter",
            mode: "lines",
            name: "Resistance 1",
            line: { color: "light red" },
            xaxis: "x",
            yaxis: "y",
            visible: getVisibility("resistance1", "Price Indicators"),
          },
          {
            x: formattedDates,
            y: data.map((entry) => entry.S1 ?? null),
            type: "scatter",
            mode: "lines",
            name: "Support 1",
            line: { color: "olive green" },
            xaxis: "x",
            yaxis: "y",
            visible: getVisibility("support1", "Price Indicators"),
          },
          {
                x: formattedDates,
                y: data.map((entry) => entry.BB_Upper),
                type: "scatter",
                mode: "lines",
                name: "Bollinger Band (Upper)",
                line: { color: "red", dash: "solid" },
                visible: getVisibility("bollingerUpper", "Price Indicators"),
            },
            {
                x: formattedDates,
                y: data.map((entry) => entry.BB_Middle),
                type: "scatter",
                mode: "lines",
                name: "Bollinger Band (Middle)",
                line: { color: "purple", dash: "dot" },
                visible: getVisibility("bollingerMiddle", "Price Indicators"),
            },
            {
                x: formattedDates,
                y: data.map((entry) => entry.BB_Lower),
                type: "scatter",
                mode: "lines",
                name: "Bollinger Band (Lower)",
                line: { color: "green", dash: "solid" },
                visible: getVisibility("bollingerLower", "Price Indicators"),
          },
          // Momentum Indicators
          {
            x: formattedDates,
            y: data.map((entry) => entry.MACD ?? null),
            type: "scatter",
            mode: "lines",
            name: "MACD",
            line: { color: "brown" },
            xaxis: "x",
            yaxis: "y2",
            visible: getVisibility("MACD", "Momentum (MACD)"),
          },
          {
            x: formattedDates,
            y: data.map((entry) => entry.MACD_Signal ?? null),
            type: "scatter",
            mode: "lines",
            name: "MACD Signal",
            line: { color: "pink" },
            xaxis: "x",
            yaxis: "y2",
            visible: getVisibility("MACDSignal", "Momentum (MACD)"),
          },
          // Oscillators
          {
            x: formattedDates,
            y: data.map((entry) => entry.RSI ?? null),
            type: "scatter",
            mode: "lines",
            name: "RSI",
            line: { color: "magenta" },
            xaxis: "x",
            yaxis: "y3",
            visible: getVisibility("RSI", "Oscillators"),
          },
          {
            x: formattedDates,
            y: data.map((entry) => entry.Stochastic ?? null),
            type: "scatter",
            mode: "lines",
            name: "Stochastic",
            line: { color: "cyan" },
            xaxis: "x",
            yaxis: "y3",
            visible: getVisibility("stochastic", "Oscillators"),
          },
          // Volume/Volatility
          {
            x: formattedDates,
            y: data.map((entry) => entry.Volume ?? null),
            type: "bar",
            name: "Volume",
            xaxis: "x",
            yaxis: "y4",
            visible: getVisibility("Volume", "Volume/Volatility"),
          },
        ].filter(Boolean)} // Filter out null traces
        layout={{
          grid: {
            rows: 4,
            columns: 1,
            subplots: [["xy"], ["xy2"], ["xy3"], ["xy4"]],
          },
          title: `${symbol} Stock Price Candlestick`,
          xaxis: { title: "Date", domain: [0, 1] },
          yaxis: { title: "Price", domain: [0.75, 1] },
          yaxis2: { title: "MACD", domain: [0.5, 0.75] },
          yaxis3: { title: "Oscillators", domain: [0.25, 0.5] },
          yaxis4: { title: "Volume/Volatility", domain: [0, 0.25] },
          showlegend: true,
          legend: { orientation: "h", x: 0.5, xanchor: "center", y: -0.4 },
          margin: { t: 50, b: 80, l: 50, r: 50 },
          width: chartDimensions.width,
          height: chartDimensions.height,
        }}
        config={{
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: ["lasso2d", "select2d"],
        }}
      />
    </div>
  );
};

export default StockChart;




