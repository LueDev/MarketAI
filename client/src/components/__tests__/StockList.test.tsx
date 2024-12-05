// client/src/components/__tests__/StockList.test.tsx

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import StockList from '../StockList';
import { AppProvider } from '../../context/AppContext';
import { fetchStocks } from '../../services/apiService';

// Mock API service
jest.mock('../../services/apiService', () => ({
    fetchStocks: jest.fn(),
}));

describe('StockList Component', () => {
    test('renders stock list', async () => {
        // Mock data
        const mockStocks = [
            { id: 1, name: 'Apple', ticker: 'AAPL', predicted_score: 85, confidence: 0.95, loss: 0.03, indicators: [] },
        ];

        (fetchStocks as jest.Mock).mockResolvedValue(mockStocks);

        render(
            <AppProvider>
                <StockList />
            </AppProvider>
        );

        expect(screen.getByText(/Stock List/i)).toBeInTheDocument();

        await waitFor(() => {
            expect(screen.getByText(/Apple/i)).toBeInTheDocument();
        });
    });
});
