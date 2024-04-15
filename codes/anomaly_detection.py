import eventLogs
from datetime import datetime
import random
import device_information


# 将hh125-rules-0623拆分成训练集和测试集，分别存储在txt文件中
def extract_logs_from0401to0414():
    # 定义开始和结束日期
    start_date = datetime.strptime("2013-04-01", "%Y-%m-%d")
    end_date = datetime.strptime("2013-04-14", "%Y-%m-%d")

    # 输入文件路径和两个输出文件路径
    input_file_path = "hh125-rules-0623.txt"
    output_file_within_range_path = "hh125-rules-0623-testing.txt"
    output_file_outside_range_path = "hh125-rules-0623-training.txt"

    # 打开输入文件和两个输出文件
    with open(input_file_path, "r") as input_file, \
            open(output_file_within_range_path, "w") as output_file_within_range, \
            open(output_file_outside_range_path, "w") as output_file_outside_range:
        # 逐行读取输入文件
        for line in input_file:
            # 尝试提取日期和时间，忽略无法解析的行
            try:
                log_date_str, log_time_str = line.split("\t")[0].split(" ")
                log_datetime = datetime.strptime(log_date_str, "%Y-%m-%d")
            except ValueError:
                continue  # 如果日期格式不正确，跳过这行

            # 检查日志的日期是否在指定的日期范围内
            if start_date <= log_datetime <= end_date:
                # 如果是，将该行写入范围内的输出文件
                output_file_within_range.write(line)
            else:
                # 否则，将该行写入范围外的输出文件
                output_file_outside_range.write(line)

    print("Completed. Data has been split based on the specified date range.")


def adjust_microseconds(prev_datetime):
    """
    调整给定datetime对象的微秒数，确保新的微秒数大于原有值。
    """
    new_microsecond = prev_datetime.microsecond + 1
    # 确保新的微秒数不会超过999999，这是datetime微秒的最大值
    if new_microsecond > 999999:
        new_microsecond = 999999
    return prev_datetime.replace(microsecond=new_microsecond)


def fake_event_insertion():
    # 读取原始日志文件
    input_file_path = "hh125-rules-0623-testing.txt"
    with open(input_file_path, "r") as file:
        lines = file.readlines()

    # 准备插入的新日志条目
    new_logs = []
    for _ in range(50):
        # 随机选择插入位置
        insert_position = random.randint(1, len(lines) - 2)  # 避免选择第一行和最后一行

        # 获取前一个日志的时间戳
        prev_log_datetime = datetime.strptime(lines[insert_position - 1].split("\t")[0], "%Y-%m-%d %H:%M:%S.%f")

        # 调整微秒数
        new_log_datetime = adjust_microseconds(prev_log_datetime)
        new_log_time_str = new_log_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")  # 移除最后三个微秒数字以匹配格式

        # 创建新的日志条目
        new_log = f"{new_log_time_str}\tM002\tON\n"
        new_logs.append((insert_position, new_log))

    # 按插入位置的逆序排列新日志条目，以避免插入时改变后续插入位置
    new_logs.sort(reverse=True)

    # 插入新日志
    for position, log in new_logs:
        lines.insert(position, log)
        print(log)
    # 保存到新的日志文件
    output_file_path = "hh125-rules-0623-testing-fakeEvents-1.txt"
    with open(output_file_path, "w") as file:
        file.writelines(lines)

    print("50 new log entries have been inserted.")
    return new_logs

def detection(correlations,new_logs):
    """
    温度要特殊处理！！！
    带condition要特殊处理
    分几种情况：
    1.entry是温度传感器读数，那么correlation的
        pre_event也是温度传感器，读数带符号（</>=），特殊处理
        following_State不是温度传感器，正常处理即可
        following_event不是温度传感器，正常处理即可
    2.entry不是温度传感器读数，那么correlation的
        pre_event不是温度传感器，正常处理即可
        following_State可能是温度传感器
        following_event不是温度传感器
    另外condition也要匹配
    """

    file_path = "hh125-rules-0623-testing-fakeEvents-1.txt"
    test_logs = eventLogs.LogManager(file_path)  # 将测试数据集导入LogManager
    devices = device_information.devices  # 设备状态，相当于影子执行引擎
    anomaly_numbers = 0  # 检测到的异常日志数目
    precision=0 #准确率
    recall=0 #召回率
    true_postive=0
    false_postive=0
    false_negative=0
    for index, entry in enumerate(test_logs.logs):
        is_entry_anomaly = False  # 默认每条日志不是异常

        # 情况1，entry是温度传感器读数
        if entry['device_name'][0] == 'T':
            # contextual checking
            for correlation in correlations:
                # correlation前事件与当前日志事件匹配
                if correlation.type == 'e2s' and correlation.event.subject == entry[
                    'device_name'] and eval(entry['action'] + correlation.event.constraint) == True and (
                            (correlation.conditionState == None) or (devices[correlation.conditionState.subject][
                                                                         'value'] == correlation.conditionState.constraint)):
                    # 检查correlation后状态（subject、constraint）与此时devices对应设备状态是否一致
                    # 不一致
                    if devices[correlation.followedEventOrState.subject][
                        'value'] != correlation.followedEventOrState.constraint:
                        is_entry_anomaly = True
                        print("anomaly detected in contextual checking:")
                        print(f"{entry['timestamp']}    {entry['device_name']}  {entry['action']}")
                        print(f"violated\n{correlation}\n")
            if is_entry_anomaly == True:  # 该条日志未通过contextual checking
                # anomaly_numbers += 1
                continue  # 该日志，已被认定异常，无需继续检测
            # consequential checking
            else:
                """
                consequential checking要考虑带condition的情况
                'e2e' correlation:
                pre_event=Event(subject='T101', attribute='temperature', constraint='>=32',extraConstraint='None')
                condition=State(subject='Fan1', attribute='fanMode', constraint='OFF')
                following_event=Event(subject='Fan1', attribute='fanMode', constraint='ON',extraConstraint='None')
                """
                # 这条日志通过contextual checking，接着进行consequential checking
                # 首先影子执行引擎按照日志内容更新状态
                devices[entry['device_name']]['value'] = entry['action']
                # consequential checking
                for correlation in correlations:
                    # correlation前事件和condition与当前日志事件匹配
                    if correlation.type == 'e2e' and correlation.event.subject == entry[
                        'device_name'] and eval(entry['action'] + correlation.event.constraint) == True and (
                            (correlation.conditionState == None) or (devices[correlation.conditionState.subject][
                                                                         'value'] == correlation.conditionState.constraint)):
                        next_entry = test_logs.logs[index + 1]
                        # 越界则不处理
                        if index + 2 == len(test_logs.logs):
                            next_next_entry = None
                        else:
                            next_next_entry = test_logs.logs[index + 2]
                        # 后事件与接下来两条的日志不匹配
                        if correlation.followedEventOrState.subject != next_entry[
                            'device_name'] or (correlation.followedEventOrState.subject == next_entry[
                            'device_name'] and correlation.followedEventOrState.constraint != next_entry['action']): #后一条日志并不匹配
                            if next_next_entry==None or (correlation.followedEventOrState.subject != next_next_entry[
                                'device_name'] or (correlation.followedEventOrState.subject == next_next_entry[
                                'device_name'] and correlation.followedEventOrState.constraint != next_next_entry['action'])):#第二条也不匹配
                                is_entry_anomaly = True
                                print("anomaly detected in consequential checking:")
                                print(f"{entry['timestamp']}    {entry['device_name']}  {entry['action']}")
                                print(f"violated\n{correlation}\n")

                        # #遍历该事件之后一秒以内发生的事件是否与该相关性匹配
                        # is_find_following_event=False #是否找到匹配时间
                        # for tmp in test_logs.logs[index+1:]:
                        #     #若该日志与被检测日志时间超过一秒，则停止检测
                        #     if time_difference_less_than_one_second(tmp['timestamp'].split(' ')[1],entry['timestamp'].split(' ')[1])==False:
                        #         break
                        #     if correlation.followedEventOrState.subject==tmp['device_name'] and correlation.followedEventOrState.constraint==tmp['action']:
                        #         is_find_following_event=True #该事件之后一秒以内发生的事件与该相关性匹配
                        #         break
                        # if is_find_following_event==False:
                        #     is_entry_anomaly=True
                        #     print("anomaly detected in consequential checking:")
                        #     print(f"{entry['timestamp']}    {entry['device_name']}  {entry['action']}")
                        #     print(f"violated\n{correlation}\n")
                        #     break
                #if is_entry_anomaly==True:
                    # anomaly_numbers+=1



        # 情况2，entry不是温度传感器读数
        else:
            # contextual checking
            for correlation in correlations:
                # correlation前事件与当前日志事件匹配
                if correlation.type == 'e2s' and correlation.event.subject == entry[
                    'device_name'] and correlation.event.constraint == entry['action'] and (
                            (correlation.conditionState == None) or (devices[correlation.conditionState.subject][
                                                                         'value'] == correlation.conditionState.constraint)):
                    # 检查correlation后状态（subject、constraint）与此时devices对应设备状态是否一致
                    # 不一致(后状态可能是温度也可能不是)
                    if (correlation.followedEventOrState.attribute == 'temperature' and eval(
                            devices[correlation.followedEventOrState.subject][
                                'value'] + correlation.followedEventOrState.constraint) == False) or (
                            correlation.followedEventOrState.attribute != 'temperature' and
                            devices[correlation.followedEventOrState.subject][
                                'value'] != correlation.followedEventOrState.constraint):
                        is_entry_anomaly = True
                        print("anomaly detected in contextual checking:")
                        print(f"{entry['timestamp']}    {entry['device_name']}  {entry['action']}")
                        print(f"violated\n{correlation}\n")
            if is_entry_anomaly == True:  # 该条日志未通过contextual checking
                # anomaly_numbers += 1
                continue  # 该日志，已被认定异常，无需继续检测
            # consequential checking
            else:
                # 这条日志通过contextual checking，接着进行consequential checking
                # 首先影子执行引擎按照日志内容更新状态
                devices[entry['device_name']]['value'] = entry['action']
                # consequential checking
                for correlation in correlations:
                    # correlation前事件和条件与当前日志事件匹配(由于日志格式的特殊性，事实上只有一个相关性可以匹配该日志)
                    if correlation.type == 'e2e' and correlation.event.subject == entry[
                        'device_name'] and correlation.event.constraint == entry['action'] and (
                            (correlation.conditionState == None) or (devices[correlation.conditionState.subject][
                                                                         'value'] == correlation.conditionState.constraint)):
                        if index+1>=len(test_logs.logs):
                            next_entry=None
                            continue
                        else:
                            next_entry= test_logs.logs[index + 1]
                        #越界则不处理
                        if index+2>=len(test_logs.logs):
                            next_next_entry=None
                        else:
                            next_next_entry= test_logs.logs[index + 2]
                        # 后事件与接下来两条的日志不匹配
                        if correlation.followedEventOrState.subject != next_entry[
                            'device_name'] or (correlation.followedEventOrState.subject == next_entry[
                            'device_name'] and correlation.followedEventOrState.constraint != next_entry['action']): #后一条日志并不匹配
                            if next_next_entry==None or(correlation.followedEventOrState.subject != next_next_entry[
                                'device_name'] or (correlation.followedEventOrState.subject == next_next_entry[
                                'device_name'] and correlation.followedEventOrState.constraint != next_next_entry['action'])):#第二条也不匹配
                                is_entry_anomaly = True
                                print("anomaly detected in consequential checking:")
                                print(f"{entry['timestamp']}    {entry['device_name']}  {entry['action']}")
                                print(f"violated\n{correlation}\n")
                        # # 遍历该事件之后一秒以内发生的事件是否与该相关性匹配
                        # is_find_following_event = False  # 是否找到匹配时间
                        # for tmp in test_logs.logs[index + 1:]:
                        #     # 若该日志与被检测日志时间超过一秒，则停止检测
                        #     if time_difference_less_than_one_second(tmp['timestamp'].split(' ')[1],entry['timestamp'].split(' ')[1]) == False:
                        #         break
                        #     if correlation.followedEventOrState.subject == tmp[
                        #         'device_name'] and correlation.followedEventOrState.constraint == tmp['action']:
                        #         is_find_following_event = True  # 该事件之后一秒以内发生的事件与该相关性匹配
                        #         break
                        # if is_find_following_event == False:
                        #     is_entry_anomaly = True
                        #     print("anomaly detected in consequential checking:")
                        #     print(f"{entry['timestamp']}    {entry['device_name']}  {entry['action']}")
                        #     print(f"violated\n{correlation}\n")
                        #     break
        if is_entry_anomaly == True:

            anomaly_numbers += 1
        #统计
        # log 格式：2013-04-01 01:00:30.098683	T101	32
        is_true_positive=False
        if is_entry_anomaly==True:
            for position,log in new_logs:
                timestamp=log.strip('\n').split('\t')[0]
                device_name=log.strip('\n').split('\t')[1]
                action=log.strip('\n').split('\t')[2]
                if timestamp==entry['timestamp'] and device_name==entry['device_name'] and action==entry['action']:
                    is_true_positive=True
                    true_postive+=1
                    break
            if is_true_positive==False:
                false_postive+=1
        #若is_entry_anomaly=False
        else:
            for position,log in new_logs:
                timestamp = log.strip('\n').split('\t')[0]
                device_name = log.strip('\n').split('\t')[1]
                action = log.strip('\n').split('\t')[2]
                if timestamp == entry['timestamp'] and device_name == entry['device_name'] and action == entry[
                    'action']:
                    false_negative+=1
                    print(f"false_negative:\n{entry}")
    precision=true_postive/(true_postive+false_postive)
    recall=true_postive/(true_postive+false_negative)
    # 以上为日志的所有检查
    print(f"anomaly_numbers:{anomaly_numbers}")
    print(f"true_postive:{true_postive}")
    print(f"false_postive:{false_postive}")
    print(f"false_negative:{false_negative}")
    print(f"precision:{precision}")
    print(f"recall:{recall}")


def time_difference_less_than_one_second(time_str1, time_str2):
    # 将时间字符串转换为 datetime 对象
    time1 = datetime.strptime(time_str1, "%H:%M:%S.%f")
    time2 = datetime.strptime(time_str2, "%H:%M:%S.%f")

    # 计算时间差
    time_diff = abs(time1 - time2)

    # 判断时间差是否小于一秒
    return time_diff.total_seconds() < 3

if __name__ == '__main__':
    # extract_logs_from0401to0414()
    fake_event_insertion()

# # contextual checking
# for correlation in correlations:
#     # correlation前事件与当前日志事件匹配
#     if correlation.type == 'e2s' and correlation.event.subject == entry[
#         'device_name'] and correlation.event.constraint == entry['action']:
#         # 检查correlation后状态（subject、constraint）与此时devices对应设备状态是否一致
#         # 不一致
#         if devices[correlation.followedEventOrState.subject][
#             'value'] != correlation.followedEventOrState.constraint:
#             is_entry_anomaly = True
#             print("anomaly detected in contextual checking:")
#             print(f"{entry['timestamp']}    {entry['device_name']}  {entry['action']}")
#             print(f"violated\n{correlation}\n")
# if is_entry_anomaly == True:  # 该条日志未通过contextual checking
#     anomaly_numbers += 1
#     break  # 该日志，已被认定异常，无需继续检测
# # consequential checking
# else:
#     # 这条日志通过contextual checking，接着进行consequential checking
#     # 首先影子执行引擎按照日志内容更新状态
#     devices[entry['device_name']]['value'] = entry['action']
#     # consequential checking
#     for correlation in correlations:
#         # correlation前事件与当前日志事件匹配(由于日志格式的特殊性，事实上只有一个相关性可以匹配该日志)
#         if correlation.type == 'e2e' and correlation.event.subject == entry[
#             'device_name'] and correlation.event.constraint == entry['action']:
#             next_entry = test_logs.logs[index + 1]
#             #后事件与日志不匹配
#             if correlation.followedEventOrState.subject == next_entry[
#                 'device_name'] and correlation.followedEventOrState.constraint != next_entry['action']:
#                 is_entry_anomaly=True
#                 print("anomaly detected in consequential checking:")
#                 print(f"{entry['timestamp']}    {entry['device_name']}  {entry['action']}")
#                 print(f"violated\n{correlation}\n")
