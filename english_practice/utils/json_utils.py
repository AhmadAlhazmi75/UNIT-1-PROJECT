import json
import os

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}

def save_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
