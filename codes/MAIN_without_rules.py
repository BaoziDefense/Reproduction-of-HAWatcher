import semantic_analysis
import calculate_similarity
import device_information
import known_rules
import eventLogs
import time
import correalation_refining
import anomaly_detection
import random
import  generate_correlations_without_rules
"""
共两种情况:
1.假设smarthomes平台闭源，无法获取自动化规则
2.已知自动化规则
"""
#未知自动化规则的情况
all_correlations=generate_correlations_without_rules.generate_correlations() #所有相关性最终将汇总到这里
devices=device_information.devices #设备状态
print(f"{len(all_correlations)} is generated.")
# # 从列表中随机抽取100个元素
# random_elements = random.sample(all_correlations, 100)
#
# # 输出随机抽取的元素
# print(random_elements)

logs = eventLogs.LogManager('3-10.txt')
start_time=time.time()
all_correlations=logs.hypothesis_Testing(all_correlations,P0=0.8)
end_time=time.time()
execution_time = end_time - start_time
print(f"The function took {execution_time} seconds to run.")

print(f"{len(all_correlations)} correlations after hypothesis testing.")
print()


#correlation refining
all_correlations=correalation_refining.refine(all_correlations)
print(f"{len(all_correlations)} correlations after correlation refining.")


"""
以上部分生成的all_correlations均可提前运行，保存在txt文件中，之后的异常检测部分只需读取txt文件即可
"""



#异常检测
# #将hh125-rules-0623拆分成训练集和测试集，分别存储在txt文件中，只需做一次
# anomaly_detection.extract_logs_from0401to0414()
new_logs=anomaly_detection.fake_event_insertion()

anomaly_detection.detection(all_correlations,new_logs)
