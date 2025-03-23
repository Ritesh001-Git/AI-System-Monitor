#Trained ML models for CPU & memory predictions
import psutil
import time
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os

# Create the models directory if it doesn't exist
os.makedirs("models", exist_ok=True)

# Train CPU model
def train_cpu_model():
    data = {"cpu": [], "cpu_next": []}
    print("Training CPU model... (Collecting data for 10 seconds)")
    try:
        while len(data["cpu"]) < 10:  # 5 minutes of data
            current_cpu = psutil.cpu_percent()
            time.sleep(1)
            next_cpu = psutil.cpu_percent()
            data["cpu"].append(current_cpu)
            data["cpu_next"].append(next_cpu)
    except KeyboardInterrupt:
        pass

    df = pd.DataFrame(data)
    model = LinearRegression()
    model.fit(df[["cpu"]], df["cpu_next"])
    joblib.dump(model, "models/cpu_model.pkl")
    print("CPU model trained and saved!")

# Train Memory model
def train_memory_model():
    data = {"memory": [], "memory_next": []}
    print("Training Memory model... (Collecting data for 10 seconds)")
    try:
        while len(data["memory"]) < 10:
            current_mem = psutil.virtual_memory().percent
            time.sleep(1)
            next_mem = psutil.virtual_memory().percent
            data["memory"].append(current_mem)
            data["memory_next"].append(next_mem)
    except KeyboardInterrupt:
        pass

    df = pd.DataFrame(data)
    model = LinearRegression()
    model.fit(df[["memory"]], df["memory_next"])
    joblib.dump(model, "models/memory_model.pkl")
    print("Memory model trained and saved!")

if __name__ == '__main__':
    train_cpu_model()
    train_memory_model()