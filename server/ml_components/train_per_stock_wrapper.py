import os
import pandas as pd
import subprocess
import re

# Configuration
data_dir = "./data"
output_dir = "./models/tech_top25"
random_forest_script = "random_forrest_model.py"
lstm_script = "LSTM_model.py"

# Ensure output directories exist
os.makedirs(output_dir, exist_ok=True)

def log_to_file(file_path, content):
    """
    Append content to a log file.
    """
    with open(file_path, "a") as f:
        f.write(content + "\n")

def parse_metrics(output, metric_names):
    """
    Extract specified metrics (e.g., MSE, MAE) from the model output.
    """
    metrics = {name: "N/A" for name in metric_names}
    for line in output.split("\n"):
        for name in metric_names:
            if name in line:
                match = re.search(r"[-+]?\d*\.\d+|\d+", line)
                if match:
                    metrics[name] = match.group()
    return metrics

def train_per_stock(data_file):
    """
    Train Random Forest and LSTM models for each stock in the dataset.
    """
    # Load dataset
    df = pd.read_csv(data_file)

    # Group by ticker
    tickers = df['Ticker'].unique()
    print(f"Found {len(tickers)} tickers: {tickers}")

    for ticker in tickers:
        print(f"\nProcessing Ticker: {ticker}")

        # Filter data for the current stock
        stock_df = df[df['Ticker'] == ticker]

        # Save filtered data to a temporary file
        temp_file = f"temp_{ticker}.csv"
        stock_df.to_csv(temp_file, index=False)

        # Set up logging file for the ticker
        ticker_log_file = os.path.join(output_dir, ticker, "model_training_data.txt")
        os.makedirs(os.path.join(output_dir, ticker), exist_ok=True)
        with open(ticker_log_file, "w") as f:
            f.write("Ticker,Model,MSE,MAE,Notes\n")

        # Train Random Forest Model
        rf_output_dir = os.path.join(output_dir, ticker, "random_forest")
        os.makedirs(rf_output_dir, exist_ok=True)
        rf_process = subprocess.run(
            [
                "python", random_forest_script,
                "--data_file", temp_file,
                "--output_dir", rf_output_dir
            ],
            capture_output=True,
            text=True
        )

        # Parse and log Random Forest metrics
        if rf_process.returncode == 0:
            rf_metrics = parse_metrics(rf_process.stdout, ["Mean Squared Error", "Mean Absolute Error"])
            log_to_file(ticker_log_file, f"{ticker},Random Forest,{rf_metrics['Mean Squared Error']},{rf_metrics['Mean Absolute Error']},Successfully trained.")
            print(f"Random Forest model trained and saved for {ticker}. MSE: {rf_metrics['Mean Squared Error']}, MAE: {rf_metrics['Mean Absolute Error']}")
        else:
            log_to_file(ticker_log_file, f"{ticker},Random Forest,N/A,N/A,Training failed. Details:\n{rf_process.stderr}")
            print(f"Random Forest training failed for {ticker}.")

        # Train LSTM Model
        lstm_output_dir = os.path.join(output_dir, ticker, "lstm")
        os.makedirs(lstm_output_dir, exist_ok=True)
        lstm_process = subprocess.Popen(
            [
                "python", lstm_script,
                "--data_file", temp_file,
                "--output_dir", lstm_output_dir
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Log LSTM progress
        with open(ticker_log_file, "a") as log_file:
            for line in lstm_process.stdout:
                print(line.strip())  # Output to terminal
                log_file.write(line)  # Log detailed training progress

        lstm_process.wait()

        if lstm_process.returncode == 0:
            # Parse final validation metrics
            final_metrics = {"val_loss": "N/A", "val_mean_absolute_error": "N/A"}
            with open(ticker_log_file, "r") as log_file:
                for line in log_file:
                    if "val_loss" in line:
                        match_loss = re.search(r"val_loss:\s*([\d\.]+)", line)
                        match_mae = re.search(r"val_mean_absolute_error:\s*([\d\.]+)", line)
                        if match_loss:
                            final_metrics["val_loss"] = match_loss.group(1)
                        if match_mae:
                            final_metrics["val_mean_absolute_error"] = match_mae.group(1)

            log_to_file(ticker_log_file, f"{ticker},LSTM,{final_metrics['val_loss']},{final_metrics['val_mean_absolute_error']},Successfully trained.")
            print(f"LSTM model trained and saved for {ticker}. val_loss: {final_metrics['val_loss']}, val_mean_absolute_error: {final_metrics['val_mean_absolute_error']}")
        else:
            log_to_file(ticker_log_file, f"{ticker},LSTM,N/A,N/A,Training failed.")
            print(f"LSTM training failed for {ticker}.")

        # Clean up temporary file
        os.remove(temp_file)

if __name__ == "__main__":
    # Example dataset
    data_file = os.path.join(data_dir, "final_enhanced_top25_tech_historical.csv")
    train_per_stock(data_file)
