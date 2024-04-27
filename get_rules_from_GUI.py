#第一种比较差劲的方法，达不到效果
# import stanfordcorenlp
# from stanfordcorenlp import StanfordCoreNLP
# nlp = StanfordCoreNLP(r'G:\semantic_analysis\stanford-corenlp-4.5.6')
# a=nlp.word_tokenize('This is an example of tokenziation.')
# print(a)
# print(nlp.pos_tag('This is an example of tokenziation.'))
# print (nlp.parse('When you return home, turn on lights and air conditioning and close the curtains.'))
# print(nlp.dependency_parse('When you return home, turn on lights and air conditioning and close the curtains.'))
def adjust_sequence(item):
    if item['governor']<item['dependent']:
        return item['governorGloss']+' '+item['dependentGloss']
    else:
        return item['dependentGloss']+' '+item['governorGloss']
#最终使用的方法
from corenlp_client import CoreNLP
import causal_division
import calculate_similarity_BERT
corenlp_dir = r"G:\semantic_analysis\stanford-corenlp-4.5.6"
with CoreNLP(annotators="pos,parse", corenlp_dir=corenlp_dir, lang="en") as annotator:
    #write your code here
    origin_text1="When you return the home, turn on lights and air conditioning and close the curtains. "
    origin_text2 = "Turn your lights on when a open/close sensor opens and the space is dark. "
    origin_text3 = "When you pick up the phone, turn on lights and air conditioning and close the curtains. "
    anno = annotator.annotate(origin_text1)
    print(anno.tokens)
    print(anno.enhanced_pp_dep)  # enhanced++依存句法分析
    token=anno.tokens[0]
    #print(type(token))
    dependency_tree=anno.enhanced_pp_dep[0]
    #print(type(dependency_tree))
    constituency_tree=anno.parse_tree[0]
    print(annotator.pretty_print_tree(anno.parse_tree[0]))

    """1.分区"""
    [Event_part,Command_part]=causal_division.division(constituency_tree)
    print()
    """词序化"""
    anno_event=annotator.annotate(Event_part)
    anno_commmand=annotator.annotate(Command_part)
    dependency_tree_event=anno_event.enhanced_pp_dep[0]
    dependency_tree_command=anno_commmand.enhanced_pp_dep[0]
    print(anno_event.enhanced_pp_dep)
    print(anno_commmand.enhanced_pp_dep)
    event_list=[]
    command_list=[]
    #对event部分词序化
    for item in dependency_tree_event:
        #满足obj关系
        if item['dep']=='obj':
            governor=item['governorGloss']
            governor_number=item['governor']
            dependent=item['dependentGloss']
            dependent_number=item['dependent']
            #接下来检查compound
            #首先对governor检查
            for item1 in dependency_tree_event:
                if 'compound' in item1['dep']:
                    if governor_number==item1['governor']:
                        governor=adjust_sequence(item1)
                    elif governor_number==item1['dependent']:
                        governor = adjust_sequence(item1)
            # 接着对dependent检查
            for item1 in dependency_tree_event:
                if 'compound' in item1['dep']:
                    if dependent_number == item1['governor']:
                        dependent = adjust_sequence(item1)
                    elif dependent_number == item1['dependent']:
                        dependent = adjust_sequence(item1)
            event_list.append(governor+' '+dependent)

    #对command部分词序化
    for item in dependency_tree_command:
        #满足obj关系
        if item['dep']=='obj':
            governor=item['governorGloss']
            governor_number=item['governor']
            dependent=item['dependentGloss']
            dependent_number=item['dependent']
            #接下来检查compound
            #首先对governor检查
            for item1 in dependency_tree_command:
                if 'compound' in item1['dep']:
                    if governor_number==item1['governor']:
                        governor=adjust_sequence(item1)
                    elif governor_number==item1['dependent']:
                        governor=adjust_sequence(item1)
            # 接着对dependent检查
            for item1 in dependency_tree_command:
                if 'compound' in item1['dep']:
                    if dependent_number == item1['governor']:
                        dependent = adjust_sequence(item1)
                    elif dependent_number == item1['dependent']:
                        dependent = adjust_sequence(item1)
            command_list.append(governor+' '+dependent)
    print("Event and Command part:")
    print(event_list)
    print(command_list)
    capabilities=[]
    """capability matching"""
    #导入capabilities
    with open('capabilities.txt','r') as file:
        for line in file:
            capabilities.append(line.strip())
        print(f"\nknown capabilities:{capabilities}")
    #生成event部分的capability
    # hello=[]
    # with open('capabilities_only.txt','r') as file:
    #     for line in file:
    #         hello.append(line.strip())
    event_capabilities=calculate_similarity_BERT.most_similar_capability(event_list,capabilities)
    command_capabilities = calculate_similarity_BERT.most_similar_capability(command_list, capabilities)
    print(event_capabilities)
    print(command_capabilities)
