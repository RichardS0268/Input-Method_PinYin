import numpy as np
import pandas as pd
from tqdm import tqdm
import sys

# file_path
hanzi_table = "../src/一二级汉字表.txt"
yuliao_data = "../src/sentences_normal.txt" # 预处理后的语料库路径
pinyin_table = "../src/拼音汉字表.txt"
transfer_matrix_path = "../src/MPDH/0_data/0_all.csv"
emit_marix_path = "../src/MPDH/1_data/1_all.csv"
std_out_file = "../data/std_output.txt"

# 制作拼音表, 格式：{'a': ['啊', '嗄', '腌', '吖', '阿', '锕'], ... }
pinyin_biao2 = {}
with open(pinyin_table, "r", encoding = 'utf-8') as f_read:
    lines = f_read.readlines()
    for line in lines:
        line = line.split()
        pinyin_biao2[line[0]] = line[1:]

# 制作拼音表，所有合法的输入
pinyin_biao = []
with open(hanzi_table, "r", encoding="utf-8") as f1:
    with open(pinyin_table, "r", encoding="utf-8") as f_read:
        data = f1.read()
        lines = f_read.readlines()
        for i in range(len(lines)):
            line = lines[i].split()
            pinyin_biao.append(line[0])

with open(hanzi_table, "r", encoding="utf-8") as f1:
    hanzi_set = f1.read()

# 定义HMM model
class HMM:
    def __init__(self, mid = "01", ir = 0.5, hanzi_num=6763):
        self.MID = mid # 模型标号，如果是load已有模型的话，MID变为已有模型的编号
        self.hanzi_map = {} # 对所有汉字建立索引
        self.duyin_map = {} # 对所有拼音建立索引
        self.hanzi_num = hanzi_num
        self.ir = ir

    def cal_init_map(self): # 构建hanzi_map和duyin_map
        '''
        - 计算每个汉字在语料库在中出现的次数，作为初始化矩阵Pi
        '''
        print("Constructing MAP ...")

        with open(hanzi_table, 'r', encoding='utf-8') as f_read1:
            data1 = f_read1.read()
            for i in range(len(data1)):
                self.hanzi_map[i] = data1[i]
            
        with open(pinyin_table, "r", encoding="utf-8") as f_read2:
            lines = f_read2.readlines()
            for i in range(len(lines)):
                line = lines[i].split()
                self.duyin_map[i] = line[0]

    def cal_transfer_matrix(self):
        '''
        - 计算转移矩阵
        '''
        print("Constructing Transfer-matrix ...")
        self.transfer = pd.read_csv(transfer_matrix_path)
    
    def cal_emit_matrix(self):
        '''
        - 计算发射矩阵
        - 调用外部 API (pypinyin: https://pypi.org/project/pypinyin/ )，转换语料库的拼音，不能直接认为每个字的每个读音都是平均的
        '''
        print("Constructing Emit-matrix ...")
        self.emit_matrix = pd.read_csv(emit_marix_path)
        self.emit_matrix = self.emit_matrix.fillna(0)

    
    def train(self):
        print("Model Training ...")
        self.train_file = [hanzi_table, yuliao_data]
        self.cal_init_map()
        self.cal_transfer_matrix()
        self.cal_emit_matrix()
        print("Training Process Finished")

    def decoding(self, Input):
        '''
        - input结构为数组
        - 维特比算法，进行decoding，实现全拼输入法功能
        '''
        delta = []
        h_words = []
        sentence = []
        for i in range(len(Input)):
            spelling = Input[i]
            emit_prob = []
            if (i == 0): # 第一个拼音
                h_words = [hanzi_set.find(x) for x in pinyin_biao2[spelling]] # 隐变量(汉字的rank)集合
                sentence = [self.hanzi_map[y] for y in h_words] # 隐变量(汉字)集合
                emit_prob = [self.emit_matrix.iloc[list(self.duyin_map.values()).index(spelling), x] for x in h_words] # 该拼音对应的各汉字的概率
                head_prob = [self.transfer.iloc[x, -1] for x in h_words] # 各汉字出现句首的概率
                delta = np.multiply(np.power(np.array(emit_prob), self.ir),np.power(np.array(head_prob), 1-self.ir)).tolist()
                # 归一化处理
                delta_sum = sum(delta)
                delta = [d / delta_sum for d in delta]

                
            else:
                temp_h_words = [hanzi_set.find(x) for x in pinyin_biao2[spelling]] # 隐变量(汉字的rank)集合
                emit_set = [self.emit_matrix.iloc[list(self.duyin_map.values()).index(spelling), x] for x in temp_h_words] # 该拼音对应的各汉字的概率
                temp_sentence = []
                temp_delta = []
                for word in temp_h_words: # 对于所有可能的隐变量
                    # 分别计算转移概率和发射概率，将乘积最大的作为这一组隐变量的delta
                    trans_prob = [self.transfer.iloc[word][x]*delta[h_words.index(x)]*emit_set[pinyin_biao2[spelling].index(hanzi_set[word])] for x in h_words] # 计算上一个状态的变量到达这个变量的转移概率
                    temp_delta.append(max(trans_prob))
                    temp_sentence.append(sentence[trans_prob.index(max(trans_prob))] + self.hanzi_map[word])
                
                # 归一化处理
                delta_sum = sum(temp_delta)
                delta = [x/delta_sum for x in temp_delta]
                sentence = temp_sentence
                h_words = temp_h_words

        return sentence[delta.index(max(delta))]
        
def convert_test(engine, file_read, file_write):
    '''
    engine是翻译引擎，HMM对象
    '''
    print("using engine::"+ engine.MID + " --initial rate = " + str(engine.ir))
    with open(file_read, "r", encoding='utf-8') as f1:
        with open(file_write, "w", encoding='utf-8') as f2:
            lines = f1.readlines()
            for data in tqdm(lines, desc="Translating.."):
                # 先判断是否有非法输入
                quanpin = data.split()
                valid_input = 1
                illegal = ""
                for yin in quanpin:
                    if yin not in pinyin_biao:
                        valid_input = 0
                        illegal += " " + yin
                if not valid_input:
                    print("Error::含有非法输入: " + illegal)
                else:
                    f2.write(engine.decoding(quanpin)+'\n')

def report_test(my_output, std_file):
    word_cnt = 0
    sentence_cnt = 0
    right_word_cnt = 0
    right_sen_cnt = 0
    results = []
    with open(std_file, "r", encoding='utf-8') as f_std:
        with open(my_output, "r", encoding='utf-8') as f_my:
            std_lines = f_std.readlines()
            my_lines = f_my.readlines()
            for my, std in zip(my_lines, std_lines):
                tmp_right_cnt = 0
                sentence_cnt += 1
                if (my == std):
                    right_sen_cnt += 1

                for my_word, std_word in zip(my, std):
                    word_cnt += 1
                    if (my_word == std_word):
                        right_word_cnt += 1
                        tmp_right_cnt += 1
                results.append([my.strip('\n'), std.strip('\n'), round(tmp_right_cnt/len(my), 4)])
        
            results = sorted(results, key = lambda x:x[2])
            print("单字准确率：", round(right_word_cnt / word_cnt, 4))
            print("整句准确率：", round(right_sen_cnt/len(my_lines), 4))
            print("好的例子：")
            for i in range(-5, -1):
                print(results[i])
            print("坏的例子")
            for i in range(1, 5):
                print(results[i])

if __name__ == '__main__':
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    pinyin = HMM()
    pinyin.train()
    convert_test(pinyin, input_file_path, output_file_path)
    #report_test(output_file_path, std_out_file)