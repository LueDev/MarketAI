from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import numpy as np

def prepare_sequences(data, sequence_length=30):
    X, y = [], []
    for i in range(len(data) - sequence_length):
        X.append(data.iloc[i:i+sequence_length].values)
        y.append(data['Price_Direction'].iloc[i+sequence_length])
    return np.array(X), np.array(y)

X_seq, y_seq = prepare_sequences(X)
model = Sequential([
    LSTM(50, activation='relu', input_shape=(X_seq.shape[1], X_seq.shape[2])),
    Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy')
model.fit(X_seq, y_seq, epochs=10, batch_size=32)
