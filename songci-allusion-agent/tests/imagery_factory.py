import pandas as pd
import jieba.posseg as pseg
from collections import Counter
import json

TOP_N = 10000


def build_imagery_library(csv_path, top_n=TOP_N):
    print("🚀 正在加载语料库...")
    df = pd.read_csv(csv_path)

    # 1. 预定义黑名单：过滤非意象的高频名词
    stop_imagery = {}

    # 2. 统计容器
    imagery_counter = Counter()

    print(f"📊 正在从 {len(df)} 篇作品中提取意象...")

    # 为了速度，我们先取作品内容
    contents = df["content"].fillna("").astype(str).tolist()

    for i, text in enumerate(contents):
        # 使用 jieba 进行词性标注分词
        # n: 普通名词, nr: 人名, nz: 其他专名
        words = pseg.cut(text)
        for word, flag in words:
            # 过滤逻辑：
            # - 长度大于1（避开“之、乎、者、也”或单字干扰）
            # - 词性为名词相关
            # - 不在黑名单内
            if len(word) > 1 and flag.startswith("n") and word not in stop_imagery:
                imagery_counter[word] += 1

        if i % 100 == 0:
            print(f"已处理 {i} 篇...")

    # 3. 提取 Top N
    top_imagery = imagery_counter.most_common(top_n)

    # 4. 保存结果
    with open("top_1000_imagery.json", "w", encoding="utf-8") as f:
        json.dump(top_imagery, f, ensure_ascii=False, indent=4)

    print(f"✅ 搞定！1000个高频意象已存入 top_{TOP_N}_imagery.json")
    return top_imagery


# 使用示例
build_imagery_library(r"D:\Documents\Code\songci-allusion-agent\data\unified_works.csv")
