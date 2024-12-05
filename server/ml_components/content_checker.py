import numpy as np

lstm_preds = np.load('prepared_top_25/LSTM_final_enhanced_finance_historical.npy')
print("LSTM Predictions Shape:", lstm_preds.shape)

rf_preds = np.load('prepared_top_25/RandomForest_final_enhanced_finance_historical.csv.npy')
print("Random Forest Predictions Shape:", rf_preds.shape)
