import json
from pathlib import Path

import requests

BASE_URL = "https://open.cnkgraph.com"
OUT_DIR = Path("tools/api_probe/sample_response")
OUT_DIR.mkdir(parents=True, exist_ok=True)

payload = {
    "pattern": "柳丝无力风凝重，平明初起停清梦、日暖照秾芳，严妆迎晓光。红颜无所取，争把金心许。月冷碧衫寒，未眠夜欲阑。"
}

resp = requests.post(
    url=f"{BASE_URL}/api/ciTune/pattern",
    json=payload,
    headers={
        "Accept": "application/json",
        "Accept-Language": "zh-hant",
        "User-Agent": "songci-commentary-api-probe/0.0.1",
    },
    timeout=10,
)

print("status:", resp.status_code)
print(resp.text[:1000])

resp.raise_for_status()

path = OUT_DIR / "ci_tune_pattern.json"
path.write_text(
    json.dumps(resp.json(), ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("saved:", path)
