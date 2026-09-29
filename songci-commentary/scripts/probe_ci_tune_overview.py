import json
import requests
from pathlib import Path


BASE_URL = "https://open.cnkgraph.com"
OUTPUT_DIR = Path("outputs/api_probe")


def main():
    url = f"{BASE_URL}/api/ciTune"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / "ci_tune_overview.json"
    output_path.write_text(
        data=json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"请求成功，结果已保存到：{output_path}")
    print(f"返回数据类型：{type(data)}")

    if isinstance(data, list):
        print(f"返回列表长度：{len(data)}")
        print("前 3 条：")
        for item in data[:3]:
            print(item)


if __name__ == "__main__":
    main()
