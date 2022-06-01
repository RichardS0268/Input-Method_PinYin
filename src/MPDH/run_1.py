from os import listdir
import pandas as pd
from tqdm import tqdm
import re
import os

# file_path
hanzi_table = "../一二级汉字表.txt"
pinyin_table = "../拼音汉字表.txt"
yuliao_data = "../sentences_normal.txt" # 预处理后的语料库路径
pinyin_data = "../pinyin_normal.txt"
process0_path = "./0_Process/"
data0_path = "./0_data/"
process1_path = "./1_Process/"
data1_path = "./1_data/"

hanzi_map = {}
duyin_map = {}
Process_number = 100 # no more than 100 !!!
line_nunmber = 4700000

with open(hanzi_table, 'r', encoding='utf-8') as f_read1:
    data1 = f_read1.read()
    for i in range(len(data1)):
        hanzi_map[i] = data1[i]
    
with open(pinyin_table, "r", encoding="utf-8") as f_read2:
    lines = f_read2.readlines()
    for i in range(len(lines)):
        line = lines[i].split()
        duyin_map[i] = line[0]

# 根据模板文件，多进程操作
with open(process1_path + "1_template.txt") as f:
    template = f.read()
for i in range(Process_number):
    with open(process1_path + f"1_Process{i}.txt", "w") as f:
        rank = i
        file = re.sub("X_NUM_X", str(i), template)
        file = re.sub("Y__SIZE__Y", str(int(line_nunmber/Process_number)), file)
        f.write(file)
    
with open(process1_path+ "1_run.txt", "w") as ff:
    for i in range(Process_number):
        ff.write("nohup python " + process1_path+ f"1_Process{i}.txt >> " + process1_path + f"log/P{i}.log 2>&1 &" + '\n')

os.system("sh " + process1_path + "1_run.txt")

# 合并各进程结果
while True:
    filelist  = listdir(data1_path)
    if len(filelist) == Process_number:
        dff_1 = pd.read_csv(data1_path +"Process_0.csv")
        for i in tqdm(range(1, Process_number), desc="reading"):
            dff2_1 = pd.read_csv(data1_path + f"Process_{i}.csv")
            dff_1 = dff_1 + dff2_1

        for i in tqdm(range(406), desc="merging"):
            row_sum = sum(dff_1.iloc[i, :])
            dff_1.iloc[i, :] = dff_1.iloc[i, :]/row_sum
        dff_1.to_csv(data1_path + "1_all_try.csv", index=0)
        os.system("rm " + process1_path + "log/*.log") # 删除日志文件
        os.system("rm " + data0_path + "Process::{0.." + str(Process_number) + "}.csv") # 删除中间文件

        break