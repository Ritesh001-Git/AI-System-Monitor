from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import psutil
import time
import threading
import joblib
import numpy as np
import pandas as pd
import os
import csv
import io
import logging

app = Flask(__name__, static_folder='static', template_folder='templates')
socketio = SocketIO(app, cors_allowed_origins="*")

# Model paths
model_paths = {
    'cpu_model': 'models/cpu_model.pkl',
    'memory_model': 'models/memory_model.pkl',
    'disk_model': 'models/disk_model.pkl'
}

models = {}
for model_name, path in model_paths.items():
    if os.path.exists(path):
        try:
            models[model_name] = joblib.load(path)
            print(f"{model_name} loaded successfully.")
        except Exception as e:
            print(f"Error loading {model_name}: {e}")
            models[model_name] = None
    else:
        print(f"Error: {model_name} not found at '{path}'.")
        models[model_name] = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_system_usage():
    while True:
        try:
            # Collect system data
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/')
            used_space = round(disk.used / (1024 ** 3), 2)
            free_space = round(disk.free / (1024 ** 3), 2)

            # Predictions
            cpu_pred = models['cpu_model'].predict(np.array([[cpu]]))[0] if models.get('cpu_model') else -1
            memory_pred = models['memory_model'].predict(np.array([[memory]]))[0] if models.get('memory_model') else -1
            disk_pred = models['disk_model'].predict(pd.DataFrame([[cpu, memory]], columns=["cpu", "memory"]))[0] if models.get('disk_model') else -1

            # Emit data
            socketio.emit('update_data', {
                'cpu': cpu,
                'memory': memory,
                'used_space': used_space,
                'free_space': free_space,
                'cpu_pred': cpu_pred if isinstance(cpu_pred, (int, float)) else -1,
                'memory_pred': memory_pred if isinstance(memory_pred, (int, float)) else -1,
                'disk_pred': disk_pred if isinstance(disk_pred, (int, float)) else -1
            })

            # Log data
            logger.info(f"CPU: {cpu}%, Memory: {memory}%, CPU Pred: {cpu_pred}, Memory Pred: {memory_pred}")

        except Exception as e:
            logger.error(f"Error: {e}")

        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download')
def download():
    try:
        # Generate CSV data
        data = [["CPU (%)", "Memory (%)", "CPU Pred (%)", "Memory Pred (%)", "Disk Pred (%)"]]
        for _ in range(10):
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            cpu_pred = models['cpu_model'].predict(np.array([[cpu]]))[0] if models.get('cpu_model') else -1
            memory_pred = models['memory_model'].predict(np.array([[memory]]))[0] if models.get('memory_model') else -1
            disk_pred = models['disk_model'].predict(pd.DataFrame([[cpu, memory]], columns=["cpu", "memory"]))[0] if models.get('disk_model') else -1
            data.append([cpu, memory, cpu_pred, memory_pred, disk_pred])

        # Create CSV response
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(data)
        output.seek(0)

        return Response(
            output,
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment;filename=system_logs.csv"}
        )
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    monitoring_thread = threading.Thread(target=get_system_usage)
    monitoring_thread.daemon = True
    monitoring_thread.start()
    socketio.run(app, debug=True)