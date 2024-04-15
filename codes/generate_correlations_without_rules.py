import semantic_analysis
import device_information
import known_rules
import calculate_similarity
def generate_correlations():
    #将所有可能的设备的所有可能的值作为trigger-condition-action
    #前事件是event，条件是state,后事件是event或state
    new_correlations=[]
    pre=semantic_analysis.Event('M002','motion','ON')
    fol=semantic_analysis.Event('L001','lightingMode','ON')
    new_correlations.append(semantic_analysis.Correlation(pre,None,fol,'e2e'))
    all_events=[]
    all_states=[]
    devices=device_information.devices
    for device_name in devices:
        #不是温度的情况
        if devices[device_name]['attribute']!='temperature':
            all_events.append(semantic_analysis.Event(device_name ,devices[device_name]['attribute'],devices[device_name]['range'][0]))
            all_events.append(semantic_analysis.Event(device_name, devices[device_name]['attribute'], devices[device_name]['range'][1]))
            all_states.append(semantic_analysis.Event(device_name, devices[device_name]['attribute'], devices[device_name]['range'][0]))
            all_states.append(semantic_analysis.Event(device_name, devices[device_name]['attribute'], devices[device_name]['range'][1]))
        #是温度的情况
        else:
            for degree in range(20, 36):
                all_events.append(semantic_analysis.Event(device_name, devices[device_name]['attribute'], '<' + str(degree)))
                all_events.append(semantic_analysis.Event(device_name, devices[device_name]['attribute'], '>=' + str(degree)))
                all_states.append(semantic_analysis.State(device_name, devices[device_name]['attribute'], '<' + str(degree)))
                all_states.append(semantic_analysis.State(device_name, devices[device_name]['attribute'], '>=' + str(degree)))

    #生成所有e2e correlation且带condition
    for pre_event in all_events:
        for condition in all_states:
            for followedEvent in all_events:
                new_correlations.append(semantic_analysis.Correlation(pre_event, condition, followedEvent, 'e2e'))

    # 生成所有e2e correlation且不带condition
    for pre_event in all_events:
        for followedEvent in all_events:
            new_correlations.append(semantic_analysis.Correlation(pre_event, None, followedEvent, 'e2e'))
    #生成所有e2s correlation且带condition
    for pre_event in all_events:
        for condition in all_states:
            for followedState in all_states:
                new_correlations.append(semantic_analysis.Correlation(pre_event, condition, followedState, 'e2s'))
    #生成所有e2s correlation且不带condition
    for pre_event in all_events:
        for followedState in all_states:
            new_correlations.append(semantic_analysis.Correlation(pre_event, None, followedState, 'e2s'))

    return new_correlations
#检验smartapp correlations和physical_and_userActivity_correlations未知规则时是否都生成了
if __name__ == "__main__":
    new_correlations=generate_correlations()
    smartapp_correlations=known_rules.smartapp_correlations
    physical_and_userActivity_correlations = calculate_similarity.generate_correlations()
    print(f"{len(smartapp_correlations)} smartapp_correlations.")
    print(f"{len(physical_and_userActivity_correlations)} physical_and_userActivity_correlations.")
    print(f"{len(new_correlations)} new_correlations.")
    found=0
    for correlation1 in smartapp_correlations:
        for correlation2 in new_correlations:
            if correlation1==correlation2:
                #print(f"smartapp correlations:\n{correlation1}\nhas been found in new_correlations\n")
                found+=1
                break
    print(f"{found} smartapp_correlations have been found in new_correlations.")
    found = 0
    for correlation1 in physical_and_userActivity_correlations:
        for correlation2 in new_correlations:
            if correlation1 == correlation2:
                # print(f"smartapp correlations:\n{correlation1}\nhas been found in new_correlations\n")
                found += 1
                break
    print(f"{found} sphysical_and_userActivity__correlations have been found in new_correlations.")