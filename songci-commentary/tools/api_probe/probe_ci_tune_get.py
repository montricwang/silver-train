import json
from pathlib import Path

import requests

BASE_URL = "https://open.cnkgraph.com"
OUT_DIR = Path("tools/api_probe/sample_response")
OUT_DIR.mkdir(parents=True, exist_ok=True)

response = requests.get(
    url=f"{BASE_URL}/api/ciTune/128",
    headers={
        "Accept": "application/json",
        "Accept-Language": "zh-hans",
        "User-Agent": "songci-commentary-api-probe/0.0.1",
    },
    timeout=10,
)

response.raise_for_status()

path = OUT_DIR / "ci_tune_128.json"
path.write_text(
    json.dumps(response.json(), ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print("saved:", path)
