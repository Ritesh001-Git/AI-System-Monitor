import psutil
import time
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os

# Create the models directory if it doesn't exist
os.makedirs("models", exist_ok=True)

# Train Disk model
data = {"cpu": [], "memory": [], "disk_used": []}
print("Training Disk model... (Collecting data for 10 seconds)")
try:
    while len(data["cpu"]) < 10:
        data["cpu"].append(psutil.cpu_percent())
        data["memory"].append(psutil.virtual_memory().percent)
        data["disk_used"].append(psutil.disk_usage('/').percent)
        time.sleep(1)
except KeyboardInterrupt:
    pass

df = pd.DataFrame(data)
model = LinearRegression()
model.fit(df[["cpu", "memory"]], df["disk_used"])
joblib.dump(model, "models/disk_model.pkl")
print("Disk model trained and saved!")