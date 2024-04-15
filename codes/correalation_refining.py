def refine(correlations):
    """
    什么情况下删除相关性a和b？：

    1.a与b的following_state一模一样，pre_event设备属性一模一样，但constriant相反

    第一轮筛完之后

    2.a与b的following_state一模一样，pre_event设备属性一模一样（特指温度），但constriant存在同类且也有的更严苛，则删掉不严苛的。（也就是原文的逻辑=>）
    """
    #功能一
    correlations_after_refining1 = []
    flag = []  # 标记每个相关性是否被筛
    flag.extend([0] * len(correlations))  # 插入0代表默认不筛
    for indexa, cora in enumerate(correlations):
        for indexb, corb in enumerate(correlations):
            # 第一种情况
            if cora.type == 'e2s' and corb.type == 'e2s' and cora.followedEventOrState == corb.followedEventOrState and cora.event.subject == corb.event.subject and ((
                    (cora.event.constraint == 'ON' and corb.event.constraint == 'OFF') or (
                    cora.event.constraint == 'OFF' and corb.event.constraint == 'ON')) or (
                    (cora.event.constraint == 'OPEN' and corb.event.constraint == 'CLOSE') or (
                    cora.event.constraint == 'CLOSE' and corb.event.constraint == 'OPEN'))):
                flag[indexa] = 1
                flag[indexb] = 1
    for index, cor in enumerate(correlations):
        if flag[index] == 0:
            correlations_after_refining1.append(cor)
    # 功能二:
    """
    'e2s' correlation:
    pre_event=Event(subject='T101', attribute='temperature', constraint='>=32',extraConstraint='None')
    condition=None
    following_state=State(subject='Fan1', attribute='fanMode', constraint='ON')

    'e2s' correlation:
    pre_event=Event(subject='T101', attribute='temperature', constraint='>=33',extraConstraint='None')
    condition=None
    following_state=State(subject='Fan1', attribute='fanMode', constraint='ON')
    删后面的
    """
    correlations_after_refining2 = []
    signal=[]
    signal.extend([0]*len(correlations_after_refining1))#接着筛
    for indexa, cora in enumerate(correlations_after_refining1):
        for indexb, corb in enumerate(correlations_after_refining1):
            if cora.type=='e2s' and corb.type=='e2s' and cora.followedEventOrState == corb.followedEventOrState and cora.event.subject == corb.event.subject:
                #a条件更严苛
                if is_harder(cora.event.constraint,corb.event.constraint)=='a':
                    signal[indexb]=1
                #b条件更严苛
                elif is_harder(cora.event.constraint,corb.event.constraint)=='b':
                    signal[indexa]=1

    for index, cor in enumerate(correlations_after_refining1):
        if signal[index] == 0:
            correlations_after_refining2.append(cor)
    #功能三:
    """
    两个相关性前事件和后事件/后状态一致，则有condition的覆盖没有condition的
    """
    correlations_after_refining3 = []
    signal=[]
    signal.extend([0]*len(correlations_after_refining2))#接着筛
    for indexa, cora in enumerate(correlations_after_refining2):
        for indexb, corb in enumerate(correlations_after_refining2):
            if cora.type==corb.type and cora.followedEventOrState == corb.followedEventOrState and cora.event.subject == corb.event.subject:
                #a有condition b没有
                if cora.conditionState!=None and corb.conditionState==None:
                    signal[indexb]=1
                # b有condition a没有
                if corb.conditionState != None and cora.conditionState == None:
                    signal[indexa] = 1

    for index, cor in enumerate(correlations_after_refining2):
        if signal[index] == 0:
            correlations_after_refining3.append(cor)
    #功能四：
    """
    去重
    """

    # 写到文件里
    with open('Allcorrelations_after_refining.txt', 'w') as file:
        # 遍历列表中的每个元素，并将其写入文件中
        for correlation in correlations_after_refining3:
            file.write(correlation.__repr__())  # 写入每个元素，并在末尾添加换行符
            file.write('\n\n')
    return correlations_after_refining3


def is_harder(cona, conb):
    if '>=' in cona and '>=' in conb:
        a=int(cona.strip('>='))
        b=int(conb.strip('>='))
        if a<b:
            return 'a'
        elif a>b:
            return 'b'
    elif '<' in cona and '<' in conb:
        a = int(cona.strip('<'))
        b = int(conb.strip('<'))
        if a<b:
            return 'b'
        elif a>b:
            return 'a'
        else:
            return None