import device_information
from scipy.stats import binom_test
class LogManager:
    def __init__(self,filename):
        # 初始化一个空列表来存储所有日志
        self.logs = []
        self.read_logs_from_file(filename)
    def __repr__(self):
        for entry in self.logs:
            print(f"{entry['timestamp']}    {entry['device_name']}  {entry['action']}")
        print(f"{len(self.logs)} logs.")

    def read_logs_from_file(self, log_file_path):
        """
        从文件中读取日志，并存储在内部数据结构中。
        """
        with open(log_file_path, 'r') as file:
            for line in file:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    log_entry = {'timestamp': parts[0], 'device_name': parts[1], 'action': parts[2]}
                    self.logs.append(log_entry)


    def show_devices_state(self,devices):
        for device_name,device_info in devices.items():
            print(f"device:{device_name},value:{device_info['value']}")

    def hypothesis_Testing(self,correlations,P0):
        """
        p0:零假设（null hypothesis）H0下，事件相关成功的概率。在这里，它是基于领域知识或先前观察设定的一个阈值。
        针对单个correlation，进行假设检验，若相关性经不起验证则从列表中删除
        """
        accepted_correlations=[]
        p_value=[]
        success_count = []  # 成功事件
        total_count = []  # 事件总数
        success_rate=[] #成功率
        devices=device_information.devices #引入未初始化的设备状态
        for number,correlation in enumerate(correlations):
            p_value.append(0)
            success_count.append(0)
            total_count.append(0)
            success_rate.append(0)
            # 要特殊考虑温度!!!!!
            # 要特殊考虑带condition的correlation!!!!
            """
            所有可能的格式都要考虑
            1.
            'e2e' correlation:
            pre_event=Event(subject='M002', attribute='motion', constraint='ON',extraConstraint='None')
            condition=None
            following_event=Event(subject='L001', attribute='lightingMode', constraint='ON',extraConstraint='None')

            2.
             'e2e' correlation:
            pre_event=Event(subject='M001', attribute='motion', constraint='OFF',extraConstraint='None')
            condition=State(subject='M003', attribute='motion', constraint='OFF')
            following_event=Event(subject='L003', attribute='lightingMode', constraint='OFF',extraConstraint='None'),
            
            3.
            'e2e' correlation:
            pre_event=Event(subject='M003', attribute='motion', constraint='ON',extraConstraint='None')
            condition=State(subject='L003', attribute='lightingMode', constraint='OFF')
            following_event=Event(subject='L003', attribute='lightingMode', constraint='ON',extraConstraint='None')

            4.
            'e2e' correlation:
            pre_event=Event(subject='T101', attribute='temperature', constraint='>=32',extraConstraint='None')
            condition=State(subject='Fan1', attribute='fanMode', constraint='OFF')
            following_event=Event(subject='Fan1', attribute='fanMode', constraint='ON',extraConstraint='None')

            """
            tmp_devices=devices #检验单个correlation时模拟设备状态
            #correlation中没有温度的情况
            if correlation.event.attribute!='temperature' and correlation.followedEventOrState.attribute!='temperature':
                #遍历日志，寻找匹配的前事件
                #index是entry的索引
                for index, entry in enumerate(self.logs):

                    # 根据当前日志更新设备状态
                    tmp_devices[entry['device_name']]['value'] = entry['action']
                    # 遇到匹配的前事件(设备名称一致、动作一致),若有condition,则condition也匹配
                    if entry['device_name']==correlation.event.subject and entry['action']==correlation.event.constraint:
                        """
                        如果
                        1.在一秒内发生了假设相关性预测的后验事件(e2e)/
                        2.假设相关性预测的状态满足(e2s)
                        则认为correlation符合这条日志的事实
                        """
                        #correlation没有condition的情况
                        if correlation.conditionState == None:
                            total_count[number] += 1
                            #e2e
                            if correlation.type=='e2e':
                                # 因为CASA数据集中的后事件日志一定是前事件和条件都满足后的下一条，所以只需将下一条日志和假设相关性的后事件比对即可
                                if index+1==len(self.logs):
                                    continue
                                post_entry=self.logs[index+1]
                                # 遇到匹配的后事件(设备名称一致、动作一致),则假设相关性和这条日志的事实一致
                                if post_entry['device_name'] == correlation.followedEventOrState.subject and post_entry[
                                    'action'] == correlation.followedEventOrState.constraint:
                                    success_count[number]+=1
                            #e2s
                            else:
                                # 遇到匹配的后状态,则假设相关性和这条日志的事实一致
                                if tmp_devices[correlation.followedEventOrState.subject]['value']==correlation.followedEventOrState.constraint:
                                    success_count[number]+=1
                        #correlation有condition的情况,则condition对应的设备的值也要满足
                        else:
                            if tmp_devices[correlation.conditionState.subject]['value']==correlation.conditionState.constraint:
                                total_count[number]+=1
                                # e2e
                                if correlation.type == 'e2e':
                                    # 因为CASA数据集中的后事件日志一定是前事件和条件都满足后的下一条，所以只需将下一条日志和假设相关性的后事件比对即可
                                    if index + 1 == len(self.logs):
                                        continue
                                    post_entry = self.logs[index + 1]
                                    # 遇到匹配的后事件(设备名称一致、动作一致),则假设相关性和这条日志的事实一致
                                    if post_entry['device_name'] == correlation.followedEventOrState.subject and post_entry[
                                        'action'] == correlation.followedEventOrState.constraint:
                                        success_count[number] += 1
                                # e2s
                                else:
                                    # 遇到匹配的后状态,则假设相关性和这条日志的事实一致
                                    if tmp_devices[correlation.followedEventOrState.subject][
                                        'value'] == correlation.followedEventOrState.constraint:
                                        success_count[number] += 1

            #correlation的前事件有温度
            elif correlation.event.attribute=='temperature':
                for index, entry in enumerate(self.logs):
                    # 根据当前日志更新设备状态
                    tmp_devices[entry['device_name']]['value'] = entry['action']
                    # 遇到匹配的前事件(设备名称一致、动作一致),温度要满足，比如24满足'>=23'
                    if entry['device_name'] == correlation.event.subject and is_temperature_ok(entry[
                        'action'],correlation.event.constraint):
                        """
                        如果
                        1.在一秒内发生了假设相关性预测的后验事件(e2e)/
                        2.假设相关性预测的状态满足(e2s)
                        则认为correlation符合这条日志的事实
                        """
                        # correlation没有condition的情况
                        if correlation.conditionState == None:
                            total_count[number] += 1
                            # e2e
                            if correlation.type == 'e2e':
                                # 因为CASA数据集中的后事件日志一定是前事件和条件都满足后的下一条，所以只需将下一条日志和假设相关性的后事件比对即可
                                if index+1!=len(self.logs):
                                    post_entry = self.logs[index + 1]
                                    # 遇到匹配的后事件(设备名称一致、动作一致),则假设相关性和这条日志的事实一致
                                    if post_entry['device_name'] == correlation.followedEventOrState.subject and post_entry[
                                        'action'] == correlation.followedEventOrState.constraint:
                                        success_count[number] += 1
                            # e2s
                            else:
                                # 遇到匹配的后状态,则假设相关性和这条日志的事实一致
                                if tmp_devices[correlation.followedEventOrState.subject][
                                    'value'] == correlation.followedEventOrState.constraint:
                                    success_count[number] += 1
                        # correlation有condition的情况,则condition对应的设备的值也要满足
                        else:
                            if tmp_devices[correlation.conditionState.subject]['value'] == correlation.conditionState.constraint:
                                total_count[number] += 1
                                # e2e
                                if correlation.type == 'e2e':
                                    # 因为CASA数据集中的后事件日志一定是前事件和条件都满足后的下一条，所以只需将下一条日志和假设相关性的后事件比对即可
                                    if index + 1 == len(self.logs):
                                        continue
                                    post_entry = self.logs[index + 1]
                                    # 遇到匹配的后事件(设备名称一致、动作一致),则假设相关性和这条日志的事实一致
                                    if post_entry['device_name'] == correlation.followedEventOrState.subject and \
                                            post_entry['action'] == correlation.followedEventOrState.constraint:
                                        success_count[number] += 1
                                # e2s
                                else:
                                    # 遇到匹配的后状态,则假设相关性和这条日志的事实一致
                                    if tmp_devices[correlation.followedEventOrState.subject][
                                        'value'] == correlation.followedEventOrState.constraint:
                                        success_count[number] += 1


            #correlation的后事件有温度
            else:
                for index, entry in enumerate(self.logs):
                    # 根据当前日志更新设备状态
                    tmp_devices[entry['device_name']]['value'] = entry['action']
                    # 遇到匹配的前事件(设备名称一致、动作一致),温度要满足，比如24满足'>=23'
                    if entry['device_name'] == correlation.event.subject and entry[
                        'action']==correlation.event.constraint:
                        """
                        如果
                        1.在一秒内发生了假设相关性预测的后验事件(e2e)/
                        2.假设相关性预测的状态满足(e2s)
                        则认为correlation符合这条日志的事实
                        """
                        # correlation没有condition的情况
                        if correlation.conditionState == None:
                            total_count[number] += 1
                            # e2e
                            if correlation.type == 'e2e':
                                # 因为CASA数据集中的后事件日志一定是前事件和条件都满足后的下一条，所以只需将下一条日志和假设相关性的后事件比对即可
                                if index+1==len(self.logs):
                                    continue
                                post_entry = self.logs[index + 1]
                                # 遇到匹配的后事件(设备名称一致、动作一致),则假设相关性和这条日志的事实一致
                                if post_entry['device_name'] == correlation.followedEventOrState.subject and is_temperature_ok(post_entry[
                                    'action'],correlation.followedEventOrState.constraint):
                                    success_count[number] += 1
                            # e2s
                            else:
                                # 遇到匹配的后状态,则假设相关性和这条日志的事实一致
                                if is_temperature_ok(tmp_devices[correlation.followedEventOrState.subject][
                                    'value'],correlation.followedEventOrState.constraint):
                                    success_count[number] += 1
                        # correlation有condition的情况,则condition对应的设备的值也要满足
                        else:
                            if tmp_devices[correlation.conditionState.subject]['value']==correlation.conditionState.constraint:
                                total_count[number] += 1
                                # e2e
                                if correlation.type == 'e2e':
                                    # 因为CASA数据集中的后事件日志一定是前事件和条件都满足后的下一条，所以只需将下一条日志和假设相关性的后事件比对即可
                                    if index + 1 == len(self.logs):
                                        continue
                                    post_entry = self.logs[index + 1]
                                    # 遇到匹配的后事件(设备名称一致、动作一致),则假设相关性和这条日志的事实一致
                                    if post_entry[
                                        'device_name'] == correlation.followedEventOrState.subject and is_temperature_ok(
                                            post_entry[
                                                'action'], correlation.followedEventOrState.constraint):
                                        success_count[number] += 1
                                # e2s
                                else:
                                    # 遇到匹配的后状态,则假设相关性和这条日志的事实一致
                                    if is_temperature_ok(tmp_devices[correlation.followedEventOrState.subject][
                                                             'value'], correlation.followedEventOrState.constraint):
                                        success_count[number] += 1

            #至此完成了针对单个correlation的成功事件和总事件的数量统计
            #若没有遇到一个满足当前correlation的事件
            if total_count[number]==0:
                success_rate[number]=0
            else:
                success_rate[number]=success_count[number]/total_count[number]

            # 进行假设检验
            p_value[number]+=binom_test(success_count[number], total_count[number], P0, alternative='greater')
            if p_value[number] < 0.05:
                accepted_correlations.append(correlation)


        with open('physical_correlations_aftertesting.txt', 'w') as file:
            # 遍历列表中的每个元素，并将其写入文件中
            for index,correlation in enumerate(correlations):
                if p_value[index]<0.05:
                    file.write(correlation.__repr__())  # 写入每个元素，并在末尾添加换行符
                    file.write('\n')
                    file.write(f"success_count={success_count[index]},total_count={total_count[index]}\n")
                    file.write(f"success_rate={success_rate[index]}\np_value={p_value[index]}\n\n")

        return accepted_correlations



#检验24是否满足'>=23'的情况
def is_temperature_ok(temperature_value,constraint):
    """
    temperature_value类似24
    constraint类似>=23
    eg:
    a='24'
    b='<23'
    print(eval(a+b))
    结果为 False
    """
    return eval(temperature_value+constraint)





if __name__ == '__main__':
    logs = LogManager('hh125-rules-0623-training.txt')
    print(logs)
    # logs.__repr__()
    # print()
    # logs.show_devices_state(device_information.devices)

