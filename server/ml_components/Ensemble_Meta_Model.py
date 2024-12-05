# ensemble_meta_model.py
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error

class EnsembleMetaModel:
    def __init__(self):
        self.model = None  # Placeholder for the XGBoost model

    def load_predictions(self, lstm_preds_file, rf_preds_file, targets_file):
        """
        Load predictions from LSTM and Random Forest models along with true targets.
        """
        self.lstm_preds = np.load(lstm_preds_file)  # LSTM predictions
        self.rf_preds = np.load(rf_preds_file)      # Random Forest predictions
        self.targets = np.load(targets_file)        # True target values

        # Combine predictions into a feature set
        self.X = np.column_stack((self.lstm_preds, self.rf_preds))
        self.y = self.targets

    def train_model(self, params=None):
        """
        Train the XGBoost model on the combined predictions.
        """
        # Use default parameters if none are provided
        if params is None:
            params = {
                "objective": "reg:squarederror",
                "eval_metric": "rmse",
                "learning_rate": 0.1,
                "max_depth": 4,
                "n_estimators": 100,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
            }

        # Initialize and train the XGBoost model
        self.model = xgb.XGBRegressor(**params)
        self.model.fit(self.X, self.y)

    def evaluate_model(self):
        """
        Evaluate the model on the training data (or separate validation data).
        """
        preds = self.model.predict(self.X)
        mse = mean_squared_error(self.y, preds)
        mae = mean_absolute_error(self.y, preds)

        print(f"Mean Squared Error (MSE): {mse}")
        print(f"Mean Absolute Error (MAE): {mae}")
        return mse, mae

    def save_model(self, filename):
        """
        Save the trained XGBoost model to a file.
        """
        self.model.save_model(filename)
        print(f"Model saved to {filename}")

    def load_model(self, filename):
        """
        Load a trained XGBoost model from a file.
        """
        self.model = xgb.XGBRegressor()
        self.model.load_model(filename)
        print(f"Model loaded from {filename}")

    def predict(self, lstm_preds, rf_preds):
        """
        Make predictions using the trained meta-model.
        """
        X = np.column_stack((lstm_preds, rf_preds))
        return self.model.predict(X)

# Example usage:
if __name__ == "__main__":
    meta_model = EnsembleMetaModel()
    
    # Provide paths to your prediction files and targets
    meta_model.load_predictions(
        lstm_preds_file="./prepared_data/lstm_preds.npy",
        rf_preds_file="./prepared_data/rf_preds.npy",
        targets_file="./prepared_data/targets.npy"
    )
    meta_model.train_model()
    meta_model.evaluate_model()
    meta_model.save_model("./models/meta_model.xgb")
