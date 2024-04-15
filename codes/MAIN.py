import semantic_analysis
import calculate_similarity
import device_information
import known_rules
import eventLogs
import time
import correalation_refining
import anomaly_detection
"""
共两种情况:
1.假设smarthomes平台闭源，无法获取自动化规则
2.已知自动化规则
"""
#首先测试已知所有规则的情况
all_correlations=[] #所有相关性最终将汇总到这里
devices=device_information.devices #设备状态

#semantic_analysis部分
#smartapp_correlations代表所有smartapp channel的相关性
smartapp_correlations=known_rules.smartapp_correlations
proposed_correlations=[]
#对每个相关性进行simplify和propose
for i in smartapp_correlations:
    i.simplify()
    tmp=i.propose()
    print()
    if tmp !=None:
        proposed_correlations.append(tmp)
smartapp_correlations.extend(proposed_correlations)
print(f"{len(smartapp_correlations)} smartapp correlations in total:")
print(smartapp_correlations)
print(f"{len(smartapp_correlations)} smartapp correlations in total.")
print()

#Correlation Mining部分
#该部分提出了physical channels and user activity channels的correlations
#1.日志预处理省略

#2.生成假设相关性
# physical_and_userActivity_correlations=[]
# physical_and_userActivity_correlations=calculate_similarity.generate_correlations()

#3.假设检验部分
#3.1 导入日志
logs = eventLogs.LogManager('hh125-rules-0623.txt')
#logs.__repr__()

#首先检验smartapp_correlations部分，因为这部分是预定义的自动化规则，所以按理讲成功率是100%，不会被假设检验筛除
smartapp_correlations=logs.hypothesis_Testing(smartapp_correlations,P0=0.5)
print(f"{len(smartapp_correlations)} smartapp correlations after hypothesis testing.")
#接着检验physical_and_userActivity_correlations部分
# start_time=time.time()
# physical_and_userActivity_correlations=logs.hypothesis_Testing(physical_and_userActivity_correlations,P0=0.8)
# end_time=time.time()
# execution_time = end_time - start_time
# print(f"The function took {execution_time} seconds to run.")
# print(f"{len(physical_and_userActivity_correlations)} physical_and_userActivity_correlations after hypothesis testing.")
# print()

#correlation refining
"""
单独对physical_and_userActivity_correlations进行refine，350个correlations最后只保留了42个
单独对smartapp correlation进行refine，没有一个被筛掉。
合并二者后refine
"""
# physical_and_userActivity_correlations=correalation_refining.refine(physical_and_userActivity_correlations)
# print(f"{len(physical_and_userActivity_correlations)} physical_and_userActivity_correlations after correlation refining.")

smartapp_correlations=correalation_refining.refine(smartapp_correlations)
print(f"{len(smartapp_correlations)} smartapp_correlations after correlation refining.")

#合并去重
# all_correlations=smartapp_correlations+[item for item in physical_and_userActivity_correlations if item not in smartapp_correlations]
# all_correlations=correalation_refining.refine(all_correlations)
# print(f"{len(all_correlations)} correlations after correlation refining.")

"""
以上部分生成的all_correlations均可提前运行，保存在txt文件中，之后的异常检测部分只需读取txt文件即可
"""


# # 保存到JSON文件
##semantic_analysis.save_correlations_to_json(all_correlations, 'Allcorrelations_after_refining.json')

# 从JSON文件中读取
#loaded_all_correlations = semantic_analysis.load_correlations_from_json('Allcorrelations_after_refining.json')

# # 打印读取到的correlations
# for correlation in loaded_all_correlations:
#     print(correlation)
# print(len(loaded_all_correlations))

#异常检测
# #将hh125-rules-0623拆分成训练集和测试集，分别存储在txt文件中，只需做一次
# anomaly_detection.extract_logs_from0401to0414()
new_logs=anomaly_detection.fake_event_insertion()

anomaly_detection.detection(smartapp_correlations,new_logs)
