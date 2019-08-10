# IMDB文本分类下载，抽取train, dev, test

本repo包含将IMDB自动下载IMDB并将其处理为train.txt, dev.txt和test.txt的脚本。

### Step 0: clone代码到本地

### Step 1: cd到本目录下
```
python imdb.py -h
usage: imdb.py [-h] -o OUTPUT [-s SEED] [-r DEV_RATIO] [-k]

Download IMDB data, and generate train.txt, test.txt. dev.txt.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Folder to save train.txt, dev.txt, test.txt
  -s SEED, --seed SEED  Seed to shuffle data.
  -r DEV_RATIO, --dev-ratio DEV_RATIO
                        How many data to split from train to be as dev.
  -k, --keep            Keep raw data.

```
运行
```
python imdb.py -o outputs
```
将在当前目录下新建一个outputs文件夹，程序运行结束之后内含train.txt, dev.txt, test.txt。原始的imdb数据中共有25000个训练样本，25000
个测试样本，训练样本中有一半是positive一半是negative，测试样本也是。由于原始数据是没有dev集，这里生成的dev集是从train中随机选择的，由
参数dev-ratio指定使用多少数据作为dev(默认0.1)。

生成的样本有类似以下的内容，使用制表符隔开label和sentence，label只有'neg', 'pos'两种。sentence内部是空格隔开两个词语。
```
label1   sentence1
label2   sentence2
...
```