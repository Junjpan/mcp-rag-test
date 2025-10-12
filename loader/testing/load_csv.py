import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from loader import load_csv

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "./knowledgebase/systax_collections.csv"
    data = load_csv(Path(file_path))
    print(json.dumps(data, indent=2, ensure_ascii=False))