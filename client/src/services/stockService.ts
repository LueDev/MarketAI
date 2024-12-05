// src/services/stockService.ts

export const getStockData = async (symbol: string) => {
    const response = await fetch(`http://127.0.0.1:10000/stocks/symbol/${symbol}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch stock data for symbol: ${symbol}`);
    }
    return await response.json();
};

export const getStocksBySector = async (sectorName: string) => {
    const response = await fetch(`http://127.0.0.1:10000/sectors/${sectorName}/stocks`);
    if (!response.ok) {
        throw new Error(`Failed to fetch stocks for sector: ${sectorName}`);
    }
    return await response.json();
};

// Mock data for testing
export const getMockStockData = () => {
    return [
        {
            symbol: "AAPL",
            name: "Apple Inc.",
            currentPrice: 150,
            historicalData: [
                { date: "2023-10-01", open: 149, high: 151, low: 148, close: 150, volume: 5000000 },
                { date: "2023-10-02", open: 150, high: 152, low: 149, close: 151, volume: 4500000 },
                { date: "2023-10-03", open: 151, high: 153, low: 150, close: 152, volume: 4700000 },
            ],
        },
        {
            symbol: "MSFT",
            name: "Microsoft Corporation",
            currentPrice: 280,
            historicalData: [
                { date: "2023-10-01", open: 279, high: 281, low: 278, close: 280, volume: 6000000 },
                { date: "2023-10-02", open: 280, high: 282, low: 279, close: 281, volume: 5800000 },
                { date: "2023-10-03", open: 281, high: 283, low: 280, close: 282, volume: 5900000 },
            ],
        },
    ];
};
