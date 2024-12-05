import React, { createContext, useState, useContext } from "react";

interface AppContextProps {
  enabledIndicators: Record<string, boolean>;
  setEnabledIndicators: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
  visibleSubplots: string;
  setVisibleSubplots: React.Dispatch<React.SetStateAction<string>>;
}

const AppContext = createContext<AppContextProps | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [enabledIndicators, setEnabledIndicators] = useState<Record<string, boolean>>({
    candlestick: true,
    vwap: true,
    ma10: true,
    ma50: true,
    ema10: true,
    ema50: true,
    bollingerUpper: true,
    bollingerMiddle: true,
    bollingerLower: true,
    RSI: true,
    MACD: true,
    MACDSignal: true,
    stochastic: true,
    Williams_R: true,
    pivot: true,
    support1: true,
    resistance1: true,
    volatility: true,
    volume: true,
  });

  const [visibleSubplots, setVisibleSubplots] = useState<string>("Show All");

  return (
    <AppContext.Provider
      value={{
        enabledIndicators,
        setEnabledIndicators,
        visibleSubplots,
        setVisibleSubplots,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = (): AppContextProps => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useAppContext must be used within an AppProvider");
  }
  return context;
};
