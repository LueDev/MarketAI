# evaluate_interpret.py

import os
import torch
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import json
from ml_components.data_loader import create_dataloader
from ml_components.model import initialize_model, interpret_model

FACTOR_NAMES = [
    "Open", "High", "Low", "Close", "Volume", "Moving Average 10", "Moving Average 50", "Volatility"
]

def evaluate_model(model, dataloader):
    predictions, targets = [], []
    with torch.no_grad():
        for sequences, labels in dataloader:
            outputs = model(sequences)
            predictions.extend(outputs.squeeze().tolist() if outputs.numel() > 1 else [outputs.item()])
            targets.extend(labels.tolist())
    mae = mean_absolute_error(targets, predictions)
    rmse = np.sqrt(mean_squared_error(targets, predictions))
    return mae, rmse

def main():
    sectors = ['finance', 'tech', 'health']
    timeframes = ['historical', 'recent']
    sequence_length = 100

    # Adjust the data directory path to be relative to the server/ml_components/data folder
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)

    for sector in sectors:
        for timeframe in timeframes:
            print(f"Evaluating and interpreting {sector} model for {timeframe} data...")

            input_size = 8
            hidden_size = 300
            output_size = 1
            num_layers = 3
            dropout = 0.1

            # Adjust model path to account for ml_components directory
            model_path = os.path.join(os.path.dirname(__file__), 'models', sector, f"{timeframe}_model.pth")
            model = initialize_model(input_size, hidden_size, output_size, num_layers, dropout)
            try:
                model.load_state_dict(torch.load(model_path))
                print(f"Loaded model for {sector} {timeframe} successfully.")
            except Exception as e:
                print(f"Failed to load model for {sector} {timeframe}: {str(e)}")
                continue
            model.eval()

            dataloader = create_dataloader(sector, timeframe, batch_size=1, sequence_length=sequence_length)

            # Evaluate model and get metrics
            mae, rmse = evaluate_model(model, dataloader)
            print(f"{sector} {timeframe} - MAE: {mae:.4f}, RMSE: {rmse:.4f}")

            # Save MAE and RMSE to a JSON file
            metrics = {"MAE": mae, "RMSE": rmse}
            metrics_file = os.path.join(data_dir, f"{sector}_{timeframe}_metrics.json")
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f)
            print(f"Metrics saved to {metrics_file}")

            # Run interpretability for feature attributions
            sample_sequence, _ = next(iter(dataloader))
            sample_sequence = sample_sequence.squeeze(0)
            if sample_sequence.dim() == 2:
                sample_sequence = sample_sequence.unsqueeze(0)

            attributions = interpret_model(model, sample_sequence)

            # Ensure attributions is a tensor for mean calculation
            if not isinstance(attributions, torch.Tensor):
                attributions = torch.tensor(attributions)

            # Prepare structured data for JSON output with factor names
            attribution_data = [
                {"factor": FACTOR_NAMES[i], "impact": float(attribution)}
                for i, attribution in enumerate(attributions.mean(0).tolist())
            ]

            attribution_file = os.path.join(data_dir, f"{sector}_{timeframe}_attributions.json")
            with open(attribution_file, 'w') as f:
                json.dump(attribution_data, f)
            print(f"Feature attributions saved to {attribution_file}")

if __name__ == "__main__":
    main()
