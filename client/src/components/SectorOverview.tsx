// src/components/SectorOverview.tsx

import React, { useState, useEffect } from 'react';
import FactorImpactChart from './FactorImpactChart';
import { downloadFile } from '../services/apiService';

const sectors = ["Finance", "Health", "Tech"];

const SectorOverview: React.FC = () => {
    const [selectedSector, setSelectedSector] = useState("Finance");
    const [dataType, setDataType] = useState("historical");
    const [metrics, setMetrics] = useState<{ RMSE: number; MAE: number; Loss: number } | null>(null);

    const handleSectorChange = (sector: string) => {
        setSelectedSector(sector);
    };

    const handleDataTypeToggle = () => {
        setDataType(dataType === "historical" ? "recent" : "historical");
    };

    const handleDownload = (sector: string, dataType: string, fileType: string) => {
        const baseUrl = `http://127.0.0.1:10000/api/data`;
        
        if (fileType === 'csv') {
            const fileUrl = `${baseUrl}/download/${sector.toLowerCase()}/${dataType}`;
            downloadFile(fileUrl, `${sector}_${dataType}.csv`);
        } else if (fileType === 'json') {
            const fileUrl = `${baseUrl}/attributions/${sector.toLowerCase()}/${dataType}`;
            downloadFile(fileUrl, `${sector}_${dataType}_attributions.json`);
        }
    };

    useEffect(() => {
        // Fetch metrics for the selected sector and data type
        const fetchMetrics = async () => {
            const response = await fetch(`/ml_components/data/${selectedSector.toLowerCase()}_${dataType}_metrics.json`);
            if (response.ok) {
                const data = await response.json();
                setMetrics(data);
            }
        };
        fetchMetrics();
    }, [selectedSector, dataType]);

    return (
        <div>
            <h1>Sector Overview</h1>
            <p>Explore the predictions and data for different sectors and their models.</p>

            <div>
                <h2>Select Sector:</h2>
                {sectors.map(sector => (
                    <button key={sector} onClick={() => handleSectorChange(sector)}>
                        {sector}
                    </button>
                ))}
            </div>

            <div>
                <h2>Data Type:</h2>
                <button onClick={handleDataTypeToggle}>
                    {dataType === "historical" ? "Switch to Recent" : "Switch to Historical"}
                </button>
            </div>

            <div>
                <h3>Model Details for {selectedSector} ({dataType})</h3>
                <p>Model Type: LSTM</p>
                <p><strong>RMSE</strong>: {metrics ? metrics.RMSE : "Loading..."} (Root Mean Squared Error - measures average prediction error)</p>
                <p><strong>MAE</strong>: {metrics ? metrics.MAE : "Loading..."} (Mean Absolute Error - average magnitude of errors)</p>
                <p><strong>Loss</strong>: {metrics ? metrics.Loss : "Loading..."} (Overall model error during training)</p>

                <h4>Download Data:</h4>
                <button onClick={() => handleDownload(selectedSector, dataType, 'csv')}>
                    Download CSV Data
                </button>
                <button onClick={() => handleDownload(selectedSector, dataType, 'json')}>
                    Download Attributions
                </button>

                <h4>Factor Impact Visualization</h4>
                <FactorImpactChart sector={selectedSector} dataType={dataType} />
            </div>
        </div>
    );
};

export default SectorOverview;
