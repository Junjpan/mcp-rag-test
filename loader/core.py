import csv
import json
import yaml
from pathlib import Path
from typing import List, Dict
from . import normalize, chucky

def load_csv(file_path: Path) -> List[Dict]:
    entries = []
    fileName =file_path.name
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            text = f"{row['topic'].capitalize()}:\nExample:{row['example']}\nDescription:{row['description']}"
            entries.append(normalize({"content": text}, source=fileName))
    return entries

def load_json(path: Path) -> List[Dict]:
    fileName = path.name
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
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
    chunks = chucky(content)
    if chunks:
        return [normalize({"content": chunk}, f"{path.name}#part{index}") for index, chunk in enumerate(chunks)]
    return [normalize({"content": content}, path.name)]

def load_text(path: Path) -> List[Dict]:
    content = path.read_text(encoding="utf-8")
    chunks = chucky(content)
    if chunks:
        return [normalize({"content": chunk}, f"{path.name}#part{index}") for index, chunk in enumerate(chunks)]
    return [normalize({"content": content}, path.name)]


def load_allFiles(directory: str) -> List[Dict]:
    all_entries = []
    supported_extensions = {".csv", ".json", ".yaml", ".yml", ".md", ".txt"}
    # Iterate through all files in the directory and its subdirectories
    for path in Path(directory).rglob("*"):
        if path.suffix.lower() not in supported_extensions:
            continue
            
        match path.suffix.lower():
            case ".csv":
                all_entries.extend(load_csv(path))
            case ".json":
                all_entries.extend(load_json(path))
            case ".yaml" | ".yml":
                all_entries.extend(load_yaml(path))
            case ".md":
                all_entries.extend(load_markdown(path))
            case ".txt":
                all_entries.extend(load_text(path))    
    
    print(f"Total entries loaded: {len(all_entries)} and saved to all_entries.json...")
    json.dump(all_entries, open("all_entries.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    return all_entries

# used for testing
load_allFiles("./knowledgebase")