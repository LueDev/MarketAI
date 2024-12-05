import sys
import os
import torch
import torch.nn as nn
from .data_loader import create_dataloader
from captum.attr import IntegratedGradients
import json

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define the LSTM model with enhanced settings
class StockPredictorLSTM(nn.Module):
    def __init__(self, input_size, hidden_size=300, output_size=1, num_layers=3, dropout=0.1):
        super(StockPredictorLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, dropout=dropout, batch_first=True)
        self.layer_norm = nn.LayerNorm(hidden_size)  # Layer normalization
        self.fc = nn.Linear(hidden_size, output_size)
        self._init_weights()

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).requires_grad_()
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).requires_grad_()
        out, _ = self.lstm(x, (h0.detach(), c0.detach()))
        out = self.layer_norm(out)  # Apply layer normalization
        out = self.fc(out[:, -1, :])
        return out

    def _init_weights(self):
        nn.init.xavier_uniform_(self.fc.weight)
        nn.init.constant_(self.fc.bias, 0)

# Initialize model with enhanced parameters
def initialize_model(input_size=8, hidden_size=300, output_size=1, num_layers=3, dropout=0.1):
    model = StockPredictorLSTM(input_size, hidden_size, output_size, num_layers, dropout)
    return model

# Train model with additional enhancements for loss reduction
def train_and_save_model(sector, timeframe, num_epochs=50, learning_rate=0.005, batch_size=32, sequence_length=100, target_loss_threshold=500):
    model = initialize_model(input_size=8, hidden_size=300, output_size=1, num_layers=3, dropout=0.1)
    dataloader = create_dataloader(sector, timeframe, batch_size=batch_size, sequence_length=sequence_length)

    criterion = nn.SmoothL1Loss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)

    for epoch in range(num_epochs):
        epoch_loss = 0
        for sequences, labels in dataloader:
            optimizer.zero_grad()
            outputs = model(sequences)
            loss = criterion(outputs.squeeze(), labels)
            loss.backward()

            # Gradient clipping to stabilize training
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            epoch_loss += loss.item()

        average_loss = epoch_loss / len(dataloader)
        scheduler.step(average_loss)  # Use scheduler based on plateau

        print(f"Sector: {sector}, Timeframe: {timeframe}, Epoch [{epoch+1}/{num_epochs}], Loss: {average_loss:.4f}, Learning Rate: {scheduler.optimizer.param_groups[0]['lr']:.6f}")

        # Early stopping if target loss threshold is reached
        if average_loss < target_loss_threshold:
            print("Early stopping as loss has reached the target threshold.")
            break

    model_dir = f"models/{sector}"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"{timeframe}_model.pth")
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to {model_path}")

# Interpret model using Integrated Gradients
def interpret_model(model, input_sequence):
    ig = IntegratedGradients(model)
    if input_sequence.dim() == 4:
        input_sequence = input_sequence.squeeze(0)
    elif input_sequence.dim() == 2:
        input_sequence = input_sequence.unsqueeze(0)
    attributions, delta = ig.attribute(input_sequence, target=0, return_convergence_delta=True)
    return attributions.squeeze().detach().numpy()

def save_attributions_to_json(attributions, filename='attributions.json'):
    with open(filename, 'w') as f:
        json.dump(attributions.tolist(), f)
    print(f"Attributions saved to {filename}")

# Main function to train and interpret models for each sector and timeframe
if __name__ == "__main__":
    sectors = ['finance', 'tech', 'health']
    timeframes = ['historical', 'recent']

    for sector in sectors:
        for timeframe in timeframes:
            print(f"Training {sector} model for {timeframe} data...")
            train_and_save_model(sector, timeframe)

    for sector in sectors:
        for timeframe in timeframes:
            print(f"Interpreting {sector} model for {timeframe} data...")
            model_path = f"models/{sector}/{timeframe}_model.pth"
            model = initialize_model(input_size=8, hidden_size=300, output_size=1, num_layers=3, dropout=0.1)
            model.load_state_dict(torch.load(model_path))
            model.eval()
            dataloader = create_dataloader(sector, timeframe, batch_size=1, sequence_length=100)
            sample_sequence, _ = next(iter(dataloader))
            attributions = interpret_model(model, sample_sequence[0])
            attribution_filename = f"data/{sector}_{timeframe}_attributions.json"
            save_attributions_to_json(attributions, filename=attribution_filename)
            print(f"Attributions for {sector} ({timeframe}) saved to {attribution_filename}")
