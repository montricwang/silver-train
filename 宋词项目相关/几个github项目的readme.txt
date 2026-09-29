几个github项目的readme
Poetry
非常全的古诗词数据，收录了从先秦到现代的共计 85 万余首古诗词。

统计信息
朝代	诗词数	作者数
宋	287114	9446
明	236957	4439
清	90089	8872
唐	49195	2736
元	37375	1209
近现代	28419	790
当代	28219	177
明末清初	17700	176
元末明初	15736	79
清末民国初	15367	99
清末近现代初	12464	48
宋末元初	12058	41
南北朝	4586	434
近现代末当代初	3426	23
魏晋	3020	251
金末元初	3019	17
金	2741	253
民国末当代初	1948	9
隋	1170	84
唐末宋初	1118	44
先秦	570	8
隋末唐初	472	40
汉	363	83
宋末金初	234	9
辽	22	7
秦	2	2
魏晋末南北朝初	1	1
总和	853385	29377
数据说明
古诗词数据按朝代存储在多个 CSV 文件中，以避免单个文件过大。有 题目、朝代、作者 和 内容 四个字段。

古诗词中有一些生僻字，属于 utf8mb4 字符，在许多设备中无法显示，使用 ? 替代。

导入数据库
为方便导入，将多个 CSV 文件合并成一个。这通过执行如下命令实现：

python scripts/merge.py
该命令将在当前目录下生成 poetry.csv 文件。

MySQL 8
创建数据库：

CREATE DATABASE poetry CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
创建数据表：

use poetry;
CREATE TABLE `poetry` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` char(200) DEFAULT NULL,
  `dynasty` char(50) DEFAULT NULL,
  `author` char(100) DEFAULT NULL,
  `content` text,
  PRIMARY KEY (`id`)
);
查看 secure_file_priv 设置：

SHOW variables like '%secure_file_priv%';
结果类似于：

+------------------+------------------------------------------------+
| Variable_name    | Value                                          |
+------------------+------------------------------------------------+
| secure_file_priv | C:\ProgramData\MySQL\MySQL Server 8.0\Uploads\ |
+------------------+------------------------------------------------+
1 row in set, 1 warning (0.0014 sec)
该目录可能因环境不同而不同。若 secure_file_priv 的 Value 为空，请自行搜索如何设置。

把 poetry.csv 文件复制到 secure_file_priv 目录中，Windows 用户可参考如下命令：

copy poetry.csv "C:\ProgramData\MySQL\MySQL Server 8.0\Uploads"
从 CSV 文件中导入数据：

LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\poetry.csv'
INTO TABLE `poetry`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n' (title, dynasty, author, content);
License
MIT 许可证。

---

Allusion_detection
中文说明（待完善）：
已发表论文工作：End-to-End Multi-task Learning for Allusion Detection in Ancient Chinese Poems

项目各目录功能说明：
Corpus：典故语料，
AER_corpus：典故提取任务（Allusion Entity Recognition task）的数据集

典故辞典	数据集文件名称	诗词例句数量	典故规模
《全唐诗典故辞典》	train_quantangshi.data	26,447	14,187
《全宋词典故辞典》	train_quansongci.data	21,734	7,303
《古诗词典故辞典》	train_gushici.data	18,337	1,295
《全元曲典故辞典》	train_yuanqu.data	4,200	2,114
​

AEC_corpus：典故分类任务（Allusion Entity Classification）的数据集

文件名	描述
sentence_with_single_class.csv	以诗句作为输入来对典故进行单类别分类
sentence_with_milti_class.csv	以诗句作为输入来对典故进行多标签分类
allu_source_with_single_class.csv	以典源作为输入来对典故进行单类别分类
allu_source_with_milti_class.csv	以典源作为输入来对典故进行多标签分类
各类别的详细样本统计信息:

典故类别	诗句-单标签	诗句-多标签	典源-单标签	典源-多标签
九流部	92	259	32	75
人事部	634	1483	248	485
人体部	107	287	32	91
人物部	375	974	109	295
伦类部	125	326	45	99
动物部	241	584	80	195
器用部	493	1127	119	353
地理部	134	365	32	103
天文部	94	249	29	74
政事部	125	333	59	111
文明部	221	498	94	164
植物部	107	297	32	91
武备部	91	205	38	65
总计	2839	6987	949	2201
ASI_corpus：典故溯源任务（Allusion Source Identification）的文本对数据集

文件名	描述
pair_sample_data.csv	诗句-典源文本对正负例
PR_corpus：诗词可读性（Poetry Readability）的难易度数据集

文件名	描述
APRD.csv	三级难易度标签
APRD+.csv	六级难易度标签
raw_poem_text.csv	诗词文档原文
AHMTL_model：AHMTL模型实现
模型架构图 



程序文件基本功能说明

[kashgari]: https://github.com/BrikerMan/Kashgari ：模型实现所借鉴的开源NLP框架，我们在1.x的基础上进行修改，使用TensorFlow2.0对该框架进行复现，并在此基础上实现了AHMTL模型，在此向该框架的原作者致谢。

embeddings：加载BERT embeding 如poetry-BERT 或者 BERT-Base

[keras_transformer]: github.com/kpot/keras-transformer ：是基于Keras的Transformer框架的开源代码实现。

layers：各类中间层的自定义实现，如CRF、Attention层等

models：各个模型的具体实现，包括单个模型如序列标注模型(labeling)/文本匹配模型(pair_match)等，以及多任务模型AHMTL。

processors：用于处理各类型的任务的输入数据的处理器，包括分类模型的处理器、序列标注模型的处理器。

task：任务实例的实现，负责各个任务的初始化、数据加载等工作，比如典故分类任务（allu_class_task）、典故溯源任务（allu_source_task）、典故提取任务（ner_task，由于典故提取模型实现采用了类似于NER任务的建模方式，因此实现模型框架初期使用了ner三个字母代表典故提取任务，在此简单说明）、诗词可读性任务（readability_task）。

trainer：异构多任务学习的训练器，负责随机抽样任务，输入对应任务的当前数据batch等工作。

model_results：存放了记录训练中间过程以及模型结果的jupyter文件。

补充：
古汉语BERT模型：poetry-BERT将 上传至百度云，详细链接后续更新。
更多借鉴与引用的工作在此不一一列出，详细请参考论文，但都在此进行致谢，感谢您们的分享，感谢你们的帮助。
下一步工作打算：
优化模型，考虑在典故提取模型中加入典源信息，以作为判定一个短语是典故词语还是非典词语的依据。
优化poetry-BERT预训练模型，将所有的典故所涉及的共7.3诗词例句作为预训练语料，在随机mask一个词语改为仅mask典故词语，然后进行预训练。
实现典故自动提取、溯源、分类应用系统。
实现人工纠正系统来对当前大部分通过正则表达式自动抽取的典故序列数据进行人工纠正。
English Introduction(To Be Continued)

---

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

