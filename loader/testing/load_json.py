import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from loader import load_json

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "./knowledgebase/syntax_basic.json"
    data = load_json(Path(file_path))
    print(json.dumps(data, indent=2, ensure_ascii=False))