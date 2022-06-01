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
with open(process0_path + "00_template.txt") as f:
    template = f.read()
for i in range(Process_number):
    with open(process0_path + f"0_Process{i}.txt", "w") as f:
        rank = i
        file = re.sub("X_NUM_X", str(i), template)
        file = re.sub("Y__SIZE__Y", str(int(line_nunmber/Process_number)), file)
        f.write(file)
    
with open(process0_path + "0_run.txt", "w") as ff:
    for i in range(Process_number):
        ff.write("nohup python " + process0_path+ f"0_Process{i}.txt >> " + process0_path + f"log/P{i}.log 2>&1 &" + '\n')

os.system("sh " + process0_path + "0_run.txt")

# 合并各进程结果
while True:
    filelist  = listdir(data0_path)
    if len(filelist) == Process_number:
        dff = pd.read_csv(data0_path + "Process::0.csv")
        for i in tqdm(range(1, Process_number), desc="reading"):
            dff2 = pd.read_csv(data0_path+ f"Process::{i}.csv")
            dff = dff + dff2
        head_sum = sum(list(dff.iloc[:, -1]))
        dff.iloc[:, -1] = dff.iloc[:, -1]/head_sum
        for i in tqdm(range(6763), desc="merging"):
            row_sum = sum(dff.iloc[i, :-1])
            dff.iloc[i, :-1] = dff.iloc[i, :-1]/row_sum
        dff = dff.fillna(0)
        dff.to_csv(data0_path+ "0_all_try.csv", index=0)
        os.system("rm " + process0_path + "log/*.log") # 删除日志文件
        os.system("rm " + data0_path + "Process::{0.." + str(Process_number) + "}.csv") # 删除中间文件
        
        break