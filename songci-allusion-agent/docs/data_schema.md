##### 作品表 works.csv

```
work_id        作品唯一标识（全局唯一，建议用哈希或稳定拼接生成）
author         作者
dynasty        朝代
genre          体裁，建议 poem / ci，以后可扩成 qu 等
title          标题；若无则为空
part           组诗/组词内部标识，如“其一”“其二”；没有则为空
rhythmic       词牌；仅词使用，诗为空
source         语料来源，如 poetry / chinese-poetry / manual
full_text      整首作品全文
```

##### 句子表 sentences.csv

```
sentence_id    句子唯一标识（建议由 work_id + line_idx + sentence_norm 哈希生成）
work_id        对应作品 id，用来回查 works.csv
line_idx       该句在作品中的顺序，从 0 开始
sentence       句子文本
punc           结尾标点，可选；如 ， 。 ？ ！ ；
is_last_line   是否为作品最后一句，0/1
```

