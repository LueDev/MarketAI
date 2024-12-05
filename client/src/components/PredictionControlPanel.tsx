import React, { useState } from "react";

const PredictionControlPanel: React.FC = () => {
  const [rollingDays, setRollingDays] = useState<number>(7);
  const [noiseLevel, setNoiseLevel] = useState<number>(5);

  const handlePredict = () => {
    alert(`Predicting with Rolling Days: ${rollingDays}, Noise: ${noiseLevel}%`);
    // Implement prediction logic here
  };

  return (
    <div className="prediction-control-panel p-4 bg-white shadow rounded">
      <h3 className="font-bold mb-2">Prediction Controls</h3>
      <div className="mb-2">
        <label>Rolling Days:</label>
        <input
          type="number"
          value={rollingDays}
          onChange={(e) => setRollingDays(Number(e.target.value))}
          className="border p-1 rounded ml-2"
        />
      </div>
      <div className="mb-2">
        <label>Noise Level (%):</label>
        <input
          type="number"
          value={noiseLevel}
          onChange={(e) => setNoiseLevel(Number(e.target.value))}
          className="border p-1 rounded ml-2"
        />
      </div>
      <button onClick={handlePredict} className="bg-blue-500 text-white px-4 py-2 rounded">
        Predict
      </button>
    </div>
  );
};

export default PredictionControlPanel;
