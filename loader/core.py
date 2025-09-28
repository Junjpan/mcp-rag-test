import csv
import json
import yaml
from pathlib import Path
from typing import List, Dict
from .helper.normalize import normalize

def load_csv(file_path: str) -> List[Dict]:
    entries = []
    fileName = file_path.split('/')[-1]
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            text = f"{row['topic'].capitalize()}:\nExample:{row['example']}\nDescription:{row['description']}"
            entries.append(normalize({"content": text}, source=fileName))
    return entries

def load_json(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    fileName = path.split('/')[-1]
    entries = []
    for item in data:
        entries.append(normalize(item, source=fileName))
    return entries

def load_yaml(path: Path) -> List[Dict]:
    content = path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    entries = []
    if isinstance(data, list):
        for entry in data:
            entries.append(normalize(entry, path.name))
    elif isinstance(data, dict):
        entries.append(normalize(data, path.name))
    return entries

def load_markdown(path: Path) -> List[Dict]:
    content = path.read_text(encoding="utf-8")
    return [normalize({"content": content}, path.name)]

def load_text(path: Path) -> List[Dict]:
    content = path.read_text(encoding="utf-8")
    
    return [normalize({"content": content}, path.name)]
