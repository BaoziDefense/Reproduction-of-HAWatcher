from gensim import models
import re
import pandas as pd
import device_information
import semantic_analysis
class Attribute:

    def __init__(self,name:str,description:str):
        #description是一个包含逗号、空格和句号的英文字符串
        #separated_description是字符串分割后的单词组成的list(去除大小写)
        self.name=name
        self.description=description
        self.separated_description=self.separateWords(description)

    def separateWords(self,description):
        words = re.findall(r'\b\w+\b', description)
        words=list(map(str.lower,words))
        return words

    def __repr__(self):
        return f"name:{self.name}\ndescription:{self.description}\nseparated_description:{self.separated_description}"

#将结果保存在excel中
def save_to_excel(property_scores, allAttributes, filename='hh125_attributes_correlation.xlsx'):
    # 创建一个空的DataFrame，索引和列都是属性的名称
    attribute_names = [attr.name for attr in allAttributes]
    df = pd.DataFrame(index=attribute_names, columns=attribute_names)

    # 填充DataFrame
    # 遍历每个物理属性及其相关的前十个属性
    for prop, scores in property_scores.items():
        for i in range(len(scores)):
            for j in range(i + 1, len(scores)):  # 避免自身比较，只比较不同的属性
                attr1, _ = scores[i]
                attr2, _ = scores[j]
                # 如果单元格已经有值，追加物理属性；否则直接赋值
                existing_value = df.at[attr1.name, attr2.name]
                if pd.isnull(existing_value):
                    df.at[attr1.name, attr2.name] = prop
                    df.at[attr2.name, attr1.name] = prop  # 确保矩阵是对称的
                else:
                    df.at[attr1.name, attr2.name] = f"{existing_value}, {prop}"
                    df.at[attr2.name, attr1.name] = f"{existing_value}, {prop}"

    # 保存到Excel文件
    df.to_excel(filename)
    print(f"Saved to {filename}")

#判断属性之间是否相似，并将结果生成到excel中，只需运行一次就可
def similarity_generation(model,allAttributes):
    #函数作用:生成邻接表
    properties = ['illuminance', 'sound', 'temperature', 'humidity', 'vibration', 'power', 'airQuality']
    property_scores = {}
    print("排序前:")
    # 初始化每个物理属性的得分列表
    for prop in properties:
        property_scores[prop] = [] #property_scores是dict
        print(f"{prop}:")
        for attribute in allAttributes:
            # #n_similarity计算两个list之间的相似度
            # score=model.n_similarity(prop,attribute.separated_description)
            # property_scores[prop].append((attribute,score)) #property_scores[prop]是一个列表，列表中存储着n个元组，每个元组代表一个属性和它的得分
            # print(f"{attribute.name}:{score}",end=" ")
            highest_score=-1# 最高得分初始化为-1
            # 遍历属性描述中的每个单词
            for word in attribute.separated_description:
                # 计算单词与物理属性的相似度得分
                try:
                    score = model.similarity(word, prop)
                    highest_score = max(highest_score, score)
                except KeyError:
                    # 如果单词不在word2vec的词汇表中，则跳过
                    continue
            if highest_score != -1:  # 确保有有效得分
                property_scores[prop].append((attribute, highest_score))
                print(f"{attribute.name}:{highest_score}", end=" ")
        print()
    # 对每个物理属性的得分进行排序，并取前十个
    print("排序后:")
    for prop in properties:
        scores=property_scores[prop]
        scores.sort(key=lambda x: x[1],reverse=True)# 根据得分降序排序
        top_ten=scores[:3]# 取得分最高的前十个,hh125里是取得分最高的前三个
        property_scores[prop] = top_ten # 更新字典
        # 打印每个物理属性的前十个属性和相应得分
        print(f"Top attributes for {prop}:")
        for attr,score in top_ten:
            print(f"{attr.name}: {score}",end=" ")
        print("\n")
    save_to_excel(property_scores, allAttributes)

#读取excel,生成相关性
#4-5层循环，乐
def generate_correlations(filename='hh125_attributes_correlation.xlsx'):
    new_correlations=[]
    # 从Excel文件中读取数据到DataFrame
    df = pd.read_excel(filename, index_col=0)  # 假设第一列是索引列

    # 获取所有属性的名称（索引和列名应该是相同的）
    attribute_names = df.index

    # 遍历DataFrame的每个元素
    for i in range(len(attribute_names)):
        for j in range(i + 1, len(attribute_names)):  # 只检查一半，因为矩阵是对称的
            attr1 = attribute_names[i]
            attr2 = attribute_names[j]

            # 检查单元格是否非空（即两个属性是否相关）
            if pd.notnull(df.at[attr1, attr2]):
                # 打印属性对和它们的相关性信息
                print(f"{attr1} 和 {attr2} 之间相关，相关属性：{df.at[attr1, attr2]}")
                #生成相关性，并添加到new_correlations中，一对属性相关（没有温度）可以生成16个相关性,e2s 8个，e2e 8个
                devices=device_information.devices
                #遍历
                for device_name1 in devices:
                    for device_name2 in devices:
                        if devices[device_name1]['attribute']==attr1 and devices[device_name2]['attribute']==attr2:
                            #生成相关性，注意温度是特殊情况
                            #没有温度的情况
                            if attr1!='temperature' and attr2!='temperature':
                                #第一步，创造4个不同的Event和4个不同的State
                                eventa1 = semantic_analysis.Event(device_name1 ,attr1,devices[device_name1]['range'][0])
                                eventa2 = semantic_analysis.Event(device_name1, attr1, devices[device_name1]['range'][1])
                                eventb1 = semantic_analysis.Event(device_name2, attr2, devices[device_name2]['range'][0])
                                eventb2 = semantic_analysis.Event(device_name2, attr2, devices[device_name2]['range'][1])
                                statea1 = semantic_analysis.State(device_name1 ,attr1,devices[device_name1]['range'][0])
                                statea2 = semantic_analysis.State(device_name1, attr1, devices[device_name1]['range'][1])
                                stateb1 = semantic_analysis.State(device_name2, attr2, devices[device_name2]['range'][0])
                                stateb2 = semantic_analysis.State(device_name2, attr2, devices[device_name2]['range'][1])

                                #第二步，创造所有相关性
                                new_correlations.append(semantic_analysis.Correlation(eventa1,None,eventb1,'e2e'))
                                new_correlations.append(semantic_analysis.Correlation(eventa1, None, eventb2, 'e2e'))
                                new_correlations.append(semantic_analysis.Correlation(eventa1, None, stateb1, 'e2s'))
                                new_correlations.append(semantic_analysis.Correlation(eventa1, None, stateb2, 'e2s'))
                                new_correlations.append(semantic_analysis.Correlation(eventa2, None, eventb1, 'e2e'))
                                new_correlations.append(semantic_analysis.Correlation(eventa2, None, eventb2, 'e2e'))
                                new_correlations.append(semantic_analysis.Correlation(eventa2, None, stateb1, 'e2s'))
                                new_correlations.append(semantic_analysis.Correlation(eventa2, None, stateb2, 'e2s'))

                                new_correlations.append(semantic_analysis.Correlation(eventb1, None, eventa1, 'e2e'))
                                new_correlations.append(semantic_analysis.Correlation(eventb1, None, eventa2, 'e2e'))
                                new_correlations.append(semantic_analysis.Correlation(eventb1, None, statea1, 'e2s'))
                                new_correlations.append(semantic_analysis.Correlation(eventb1, None, statea2, 'e2s'))
                                new_correlations.append(semantic_analysis.Correlation(eventb2, None, eventa1, 'e2e'))
                                new_correlations.append(semantic_analysis.Correlation(eventb2, None, eventa2, 'e2e'))
                                new_correlations.append(semantic_analysis.Correlation(eventb2, None, statea1, 'e2s'))
                                new_correlations.append(semantic_analysis.Correlation(eventb2, None, statea2, 'e2s'))

                            #有温度的情况,两种可能，一种attr1是温度，一种attr2是温度
                            #这里假设可能的温度范围是20-35度
                            else:
                                #attr1是温度
                                if attr1=='temperature':
                                    #生成所有的event、state
                                    #1.生成attr2的event、state
                                    eventb1 = semantic_analysis.Event(device_name2, attr2,devices[device_name2]['range'][0])
                                    eventb2 = semantic_analysis.Event(device_name2, attr2,devices[device_name2]['range'][1])
                                    stateb1 = semantic_analysis.State(device_name2, attr2,devices[device_name2]['range'][0])
                                    stateb2 = semantic_analysis.State(device_name2, attr2,devices[device_name2]['range'][1])
                                    # 2.生成attr1的event、state
                                    hypothetical_temperature_event=[]
                                    hypothetical_temperature_state = []
                                    for degree in range(20,36):
                                        hypothetical_temperature_event.append(semantic_analysis.Event(device_name1 ,attr1,'<'+str(degree)))
                                        hypothetical_temperature_event.append(semantic_analysis.Event(device_name1, attr1, '>=' + str(degree)))
                                        hypothetical_temperature_state.append(semantic_analysis.State(device_name1 ,attr1,'<'+str(degree)))
                                        hypothetical_temperature_state.append(semantic_analysis.State(device_name1, attr1, '>=' + str(degree)))
                                    # 3.生成所有correlation
                                    for eventa in hypothetical_temperature_event:
                                        new_correlations.append(semantic_analysis.Correlation(eventa,None,eventb1,'e2e'))
                                        new_correlations.append(semantic_analysis.Correlation(eventa, None, eventb2, 'e2e'))

                                        new_correlations.append(semantic_analysis.Correlation(eventa, None, stateb1, 'e2s'))
                                        new_correlations.append(semantic_analysis.Correlation(eventa, None, stateb2, 'e2s'))

                                        new_correlations.append(semantic_analysis.Correlation(eventb1,None,eventa,'e2e'))
                                        new_correlations.append(semantic_analysis.Correlation(eventb2, None, eventa, 'e2e'))

                                    for statea in hypothetical_temperature_state:
                                        new_correlations.append(semantic_analysis.Correlation(eventb1, None, statea, 'e2s'))
                                        new_correlations.append(semantic_analysis.Correlation(eventb2, None, statea, 'e2s'))


                                #attr2是温度,与上面对称
                                else:
                                    # 生成所有的event、state
                                    # 1.生成attr1的event、state
                                    eventa1 = semantic_analysis.Event(device_name1, attr1,
                                                                      devices[device_name1]['range'][0])
                                    eventa2 = semantic_analysis.Event(device_name1, attr1,
                                                                      devices[device_name1]['range'][1])
                                    statea1 = semantic_analysis.State(device_name1, attr1,
                                                                      devices[device_name1]['range'][0])
                                    statea2 = semantic_analysis.State(device_name1, attr1,
                                                                      devices[device_name1]['range'][1])
                                    # 2.生成attr2的event、state
                                    hypothetical_temperature_event = []
                                    hypothetical_temperature_state = []
                                    for degree in range(20, 36):
                                        hypothetical_temperature_event.append(
                                            semantic_analysis.Event(device_name2, attr2, '<' + str(degree)))
                                        hypothetical_temperature_event.append(
                                            semantic_analysis.Event(device_name2, attr2, '>=' + str(degree)))
                                        hypothetical_temperature_state.append(
                                            semantic_analysis.State(device_name2, attr2, '<' + str(degree)))
                                        hypothetical_temperature_state.append(
                                            semantic_analysis.State(device_name2, attr2, '>=' + str(degree)))
                                    # 3.生成所有correlation
                                    for eventb in hypothetical_temperature_event:
                                        new_correlations.append(
                                            semantic_analysis.Correlation(eventb, None, eventa1, 'e2e'))
                                        new_correlations.append(
                                            semantic_analysis.Correlation(eventb, None, eventa2, 'e2e'))

                                        new_correlations.append(
                                            semantic_analysis.Correlation(eventb, None, statea1, 'e2s'))
                                        new_correlations.append(
                                            semantic_analysis.Correlation(eventb, None, statea2, 'e2s'))

                                        new_correlations.append(
                                            semantic_analysis.Correlation(eventa1, None, eventb, 'e2e'))
                                        new_correlations.append(
                                            semantic_analysis.Correlation(eventa2, None, eventb, 'e2e'))

                                    for stateb in hypothetical_temperature_state:
                                        new_correlations.append(
                                            semantic_analysis.Correlation(eventa1, None, stateb, 'e2s'))
                                        new_correlations.append(
                                            semantic_analysis.Correlation(eventa2, None, stateb, 'e2s'))

    #print(new_correlations)
    print(f"{len(new_correlations)} physical_and_userActivity_correlations in total.")
    print()
    with open('physical_and_userActivity_correlations.txt', 'w') as file:
        # 遍历列表中的每个元素，并将其写入文件中
        for item in new_correlations:
            file.write(item.__repr__())  # 写入每个元素，并在末尾添加换行符
            file.write('\n')
    return new_correlations


if __name__ == "__main__":
    #引入预训练模型
    model = models.keyedvectors.load_word2vec_format(r'G:\学习\IOT\HAWatcher复现\GoogleNews-vectors-negative300.bin.gz', binary=True)
    allAttributes=[]
    #读取文件，每读一行创建一个attribute对象，将name和description分割
    with open('hh125_descriptions_of_attributes.txt','r') as file:
        for line in file:
            # 使用strip()方法去除行末尾的换行符，并使用split(':')方法按冒号分割属性和描述
            parts=line.strip().split(':')
            #创建对象
            temp_attribute=Attribute(parts[0].strip(),parts[1].strip())
            allAttributes.append(temp_attribute)
            print(temp_attribute)
            print()
    similarity_generation(model,allAttributes)
    #generate_correlations()