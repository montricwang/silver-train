BERT-CCP​​oem
介绍
BERT-CCP​​oem 是清华大学计算人文社会科学自然语言处理研究中心开发的基于 BERT 的专门针对中国古典诗歌的预训练模型。

BERT-CCP​​oem 基于几乎完整的中国古典诗歌集 CCPC-Full v1.0 进行训练，该诗歌集包含 926,024 首古典诗歌，共计 8,933,162 句。因此，它可以提供任何中国古典诗歌中任意句子的向量（嵌入）表示，从而可用于各种下游应用，包括智能诗歌检索、推荐和情感分析。

一个典型的应用是，你可以使用从 BERT-CCP​​oem 导出的向量表示，根据相关的余弦值，找到与给定句子语义最相似的句子。例如，给定一个诗句“一行白鹭上青天”，BERT-CCP​​oem 给出的前 10 个最可能的句子如下：

秩	诗句	余弦相似度	秩	诗句	余弦相似度
1	白鹭一行登碧霄	0.9331	6	一行白鸟掠清波	0.9024
2	一片青天白鹭前	0.9185	7	时向青空飞白鹭	0.9023
3	飞却青天白鹭鸶	0.9155	8	一行飞鸟来青天	0.9005
4	一双白鹭上云飞	0.9118	9	一行白鹭下汀洲	0.8994
5	白鹭一行飞绿野	0.9065	10	一行飞鹭下汀洲	0.8962
以下是字符串匹配算法给出的最有可能出现的 10 个句子，供比较：

秩	诗句	秩	诗句
1	数行白鹭横青湖	6	一行白鹭渺秋烟
2	一片青天白鹭前	7	一行白鹭引舟行
3	一行飞鸟来青天	8	一行白鹭过前山
4	一行白鹭下汀洲	9	一行白雁遥天暮
5	一行白鹭云间绕	10	一行白雁天边字
模型详情
我们使用开源项目 Transformers 中的“BertModel”类来训练模型。BERT-CCP​​oem 完全基于 CCPC-Full v1.0，并以汉字为基本单元。出现频率低于 3 的汉字被视为 [UNK]，最终得到包含 11,809 个字符的词汇表。

BERT-CCP​​oem 的参数如下：

model	版本	参数	词汇量	模型尺寸	下载链接
BERT-CCP​​oem	v1.0	8层，512个隐藏部件，8个头部	11809	162MB	下载
如何使用
下载 Bert-CCPoem v1.0：
wget https://thunlp.oss-cn-qingdao.aliyuncs.com/BERT_CCPoem_v1.zip
unzip BERT_CCPoem_v1.zip
然后，使用指定路径加载 BERT-CCP​​oem v1.0。例如，生成句子“一行白鹭上青天”的向量表示：
from transformers import BertModel, BertTokenizer
import torch
tokenizer = BertTokenizer.from_pretrained('./BERT_CCPoem_v1') 
model = BertModel.from_pretrained('./BERT_CCPoem_v1')
input_ids = torch.tensor(tokenizer.encode("一行白鹭上青天")).unsqueeze(0) 
outputs, _ = model(input_ids)
sen_emb = torch.mean(outputs, 1)[0] # This is the vector representation of "一行白鹭上青天"
注意： 您可以查看我们提供的示例程序 gen_vec_rep.py 。

要求.txt
torch>=1.2.0
transformers==4.3.3
致谢并引用 BERT-CCP​​oem
我们免费提供 BERT-CCP​​oem 供研究使用，但前提是必须使用适当的引用方式进行正确引用。

当撰写论文或开发基于 BERT-CCP​​oem 的软件应用程序、工具或界面时，必须正确注明使用 BERT-CCP​​oem 的方式为 “我们使用 BERT-CCP​​oem，一个由清华大学计算人文社会科学自然语言处理研究中心开发的中国古典诗歌预训练模型，用于……” ，并引用 GitHub 网站“ https://github.com/THUNLP-AIPoet/BERT-CCP ​​oem”。

贡献者
教授： 孙茂松

学生： 郭志芃、胡锦毅

联系我们
如果您有任何问题、建议或错误报告，请随时发送电子邮件至 hujy369@gmail.com 或 gzp9595@gmail.com 。

