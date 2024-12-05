import os
import numpy as np
from sklearn.model_selection import train_test_split, LeaveOneOut, KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
import joblib
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def augment_data(X, min_samples=5):
    """
    Augments data to ensure the minimum number of samples by interpolating between existing rows.
    """
    while X.shape[0] < min_samples:
        interpolated = (X[:-1] + X[1:]) / 2
        X = np.vstack((X, interpolated[:min_samples - X.shape[0]]))
    return X


def load_meta_data(meta_data_dir):
    """
    Loads meta-model inputs (X_meta) and ensures consistency in data formatting.
    Handles missing values and standardizes features.
    """
    X_meta_files = [f for f in os.listdir(meta_data_dir) if f.startswith("X_meta_")]
    meta_data = []

    for x_file in X_meta_files:
        dataset_name = x_file.replace("X_meta_", "").replace(".npy", "")
        try:
            X_meta = np.load(os.path.join(meta_data_dir, x_file))

            # In load_meta_data function
            if X_meta.shape[0] < 5:
                logging.warning(f"Dataset {dataset_name} has {X_meta.shape[0]} samples. Augmenting to reach minimum required samples.")
                X_meta = augment_data(X_meta, min_samples=5)


            # Handle missing values
            imputer = SimpleImputer(strategy="mean", add_indicator=True)  # Add indicator for imputed features
            X_meta = imputer.fit_transform(X_meta)

            # Standardize features
            scaler = StandardScaler()
            X_meta = scaler.fit_transform(X_meta)

            meta_data.append({
                "dataset": dataset_name,
                "X_meta": X_meta,
            })
        except Exception as e:
            logging.error(f"Error loading dataset {dataset_name}: {e}")

    return meta_data

def generate_targets(X_meta):
    """
    Generates synthetic target values for the meta-model.
    Ensures that targets have the same number of samples as X_meta.
    """
    y = np.random.rand(X_meta.shape[0])  # Replace with actual target loading if available
    return y

def train_meta_model(X, y, dataset_name, output_dir="trained_meta_model"):
    """
    Trains an XGBoost meta-model using the provided data.
    Handles small datasets with flexible cross-validation or LOOCV.
    """
    os.makedirs(output_dir, exist_ok=True)

    if X.shape[0] < 5:
        logging.warning(f"Skipping training for {dataset_name} due to insufficient samples.")
        return None

    if X.shape[0] <= 10:  # Use flexible k-fold cross-validation for small datasets
        k = min(3, X.shape[0])  # Adjust k based on available samples
        kf = KFold(n_splits=k, shuffle=True, random_state=42)
        y_preds = []

        for train_idx, test_idx in kf.split(X):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            model = XGBRegressor(
                objective="reg:squarederror",
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
            )
            model.fit(X_train, y_train)
            y_preds.append(model.predict(X_test)[0])

        # Adjust y to match the length of predictions
        y = y[:len(y_preds)]
        mse = mean_squared_error(y, y_preds)
        mae = mean_absolute_error(y, y_preds)
        logging.info(f"Flexible K-Fold Evaluation for {dataset_name} - MSE: {mse}, MAE: {mae}")
    else:
        # Train/Test Split for larger datasets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = XGBRegressor(
            objective="reg:squarederror",
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
        )
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        logging.info(f"Evaluation for {dataset_name} - MSE: {mse}, MAE: {mae}")

    # Save the model
    model_path = os.path.join(output_dir, f"xgboost_meta_model_{dataset_name}.joblib")
    joblib.dump(model, model_path)
    logging.info(f"Trained meta-model for {dataset_name} saved to {model_path}")
    return model

def main():
    meta_data_dir = "prepared_meta_data"
    meta_data = load_meta_data(meta_data_dir)

    for data in meta_data:
        dataset_name = data["dataset"]
        X_meta = data["X_meta"]
        
        # Generate or load targets dynamically
        y = generate_targets(X_meta)

        logging.info(f"Training meta-model for dataset: {dataset_name}")
        train_meta_model(X_meta, y, dataset_name)

if __name__ == "__main__":
    main()
