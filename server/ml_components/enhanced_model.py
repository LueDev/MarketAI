from enhanced_data_preparation import load_and_prepare_enhanced_data
from enhanced_data_transformer import transform_enhanced_data
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier  # Replace with your model of choice
import numpy as np

def load_data_for_model(sector, timeframe):
    # Load and prepare enhanced data
    df_prepared = load_and_prepare_enhanced_data(sector, timeframe)
    
    # Transform data for model input
    df_features, scaler = transform_enhanced_data(df_prepared)

    # Define target (assuming a classification or regression target exists in the data)
    # Example: Predicting 'Price_Direction' as target; replace with the actual target column
    X = df_features
    y = df_prepared['Price_Direction'] if 'Price_Direction' in df_prepared else np.zeros(len(df_features))

    return X, y, scaler

def train_model(sector, timeframe):
    # Load data
    X, y, scaler = load_data_for_model(sector, timeframe)
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and train model (example model: RandomForest)
    model = RandomForestClassifier()  # Replace with your model
    model.fit(X_train, y_train)
    
    # Evaluate model performance
    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy:.2f}")
    
    # Return the trained model and scaler for later use
    return model, scaler

def predict(sector, timeframe, model, scaler):
    # Load and transform new data for prediction
    X, _, _ = load_data_for_model(sector, timeframe)
    
    # Predict with the trained model
    predictions = model.predict(X)
    return predictions

# Example usage
if __name__ == "__main__":
    sector = "finance"
    timeframe = "historical"

    # Train the model
    model, scaler = train_model(sector, timeframe)
    
    # Predict on new data (using the same sector and timeframe as example)
    predictions = predict(sector, timeframe, model, scaler)
    print(predictions)
