import numpy as np
import pandas as pd

# file_path
hanzi_table = "../src/一二级汉字表.txt"
yuliao_data = "../src/sentences_normal.txt" # 预处理后的语料库路径
pinyin_table = "../src/拼音汉字表.txt"
transfer_matrix_path = "../src/MPDH/0_data/0_all.csv"
emit_marix_path = "../src/MPDH/1_data/1_all.csv"

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
                    trans_prob = [self.transfer.iloc[word][x]*delta[h_words.index(x)] for x in h_words] # 计算上一个状态的变量到达这个变量的转移概率
                    temp_delta.append(max(trans_prob)*emit_set[pinyin_biao2[spelling].index(hanzi_set[word])])
                    temp_sentence.append(sentence[trans_prob.index(max(trans_prob))] + self.hanzi_map[word])
                
                # 归一化处理
                delta_sum = sum(temp_delta)
                delta = [x/delta_sum for x in temp_delta]
                sentence = temp_sentence
                h_words = temp_h_words

        output = sentence[delta.index(max(delta))]
        print(output)

def convert_shell(engine):
    '''
    engine是翻译引擎，HMM对象
    '''
    print("using engine::"+ engine.MID + "\n --initial rate = " + str(engine.ir))
    print("输入\"exit\"退出程序")
    while True:
        data = input("输入全拼:")
        if (data == "exit"):
            print("--EXIT--")
            break
        else:
            try:
                # 先判断是否有非法输入
                quanpin = data.split()
                valid_input = 1
                illegal = ""
                for yin in quanpin:
                    if yin not in pinyin_biao:
                        valid_input = 0
                        illegal += " " + yin
                if not valid_input:
                    print("含有非法输入: " + illegal)
                else:
                    engine.decoding(quanpin)
            except:
                print("Error")
                continue
        
if __name__ == '__main__':
    pinyin3 = HMM()
    pinyin3.train()
    convert_shell(pinyin3)