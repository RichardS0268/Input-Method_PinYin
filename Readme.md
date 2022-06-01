# ⌨Input Method -- PinYin

## Files Structure

+ To run `IM_shell.py` and `IM.ipynb`, make sure the files ended with ♦ exist.
+ To run `IM_test.py`, make sure the files ended with ♠ exist.

```latex
-- bin
---- IM_shell.py
---- IM_test.py
---- IM.ipynb
-- data # for IM_test.py
---- input.txt ♠
---- my_output.txt ♠
---- std_output.txt ♠
-- src
---- MPDH # for multiply processing data
-------- 0_data
------------ 0_all.csv ♦
-------- 0_Process
------------ log/
------------ 0_run.txt
------------ 00_template.txt
-------- 1_data
------------ 1_all.csv ♦
-------- 1_Process
------------ log/
------------ 1_run.txt
------------ 1_template.txt
-------- run_0.py
-------- run_0.py
-------- run.ipynb
---- 拼音汉字表.txt ♦
---- 一二级汉字表.txt ♦
---- 语料库.zip
---- data_handler.ipynb
---- pinyin_normal.txt
---- sentences_normal.txt ♦
---- sentences_raw.txt
---- sentences.txt
```

## Pre-processed Data

Located in folder `./src`, you can download the pre-processed data together with raw data with

```sh
wget https://cloud.tsinghua.edu.cn/f/1f6e33ed073e42cbb758/?dl=1 -O files.zip
unzip files.zip
```

Then you will have files following 

```
-- 拼音汉字表.txt ♦
-- 一二级汉字表.txt ♦
-- pinyin_normal.txt
-- sentences_normal.txt ♦
-- sentences_raw.txt
-- sentences.txt
```

With command

```
wget https://cloud.tsinghua.edu.cn/f/ad2a884a89204c1eaa15/?dl=1 -O 语料库.zip
unzip 语料库.zip
```

you can get 

```
-- 语料库
---- sina_news_gbk
-------- 2016-02.txt
-------- ...
-------- 2016-11.txt
```

You can use the ♦ files directly and run `IM_shell.py` and `IM.ipynb`. Or you can run `data_handler.ipynb` to generate these files manually.

## Inference

run `IM_shell.py` or `IM.ipynb` when necessary files are ready.

```sh
python IM_shell.py
```

<img src="https://github.com/RichardS0268/Input-Method_PinYin/blob/main/docx/Inference1.png" style="zoom:60%;" />



run  `IM.ipynb`

 <img src="https://github.com/RichardS0268/Input-Method_PinYin/blob/main/docx/Inference2.png" style="zoom:60%;" />
