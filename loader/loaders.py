from .core import load_json, load_yaml, load_markdown, load_text, load_csv

LOADERS = {
    ".json": load_json,
    ".yaml": load_yaml,
    ".yml": load_yaml,
    ".md": load_markdown,
    ".txt": load_text,
    ".csv": load_csv,  
}
