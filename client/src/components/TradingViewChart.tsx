// src/components/TradingViewChart.tsx

import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

interface CandlestickData {
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
}

const TradingViewChart: React.FC<{ symbol: string; data: CandlestickData[] }> = ({ symbol, data }) => {
    const chartContainerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (chartContainerRef.current && data.length > 0) {
            const chart = createChart(chartContainerRef.current, { width: 500, height: 300 });
            const candlestickSeries = chart.addCandlestickSeries();
            candlestickSeries.setData(data);

            return () => chart.remove();
        }
    }, [data]);

    return <div ref={chartContainerRef} />;
};

export default TradingViewChart;
