#这部分用于将一个描述语句分为Event部分和Command部分
#第一部分，拆分
def extract_parts(tree):
    # 寻找SBAR部分
    sbar_index = tree.index('(SBAR')
    # 寻找SBAR结束位置
    depth = 0
    start = sbar_index
    end = sbar_index
    while end < len(tree):
        if tree[end] == '(':
            depth += 1
        elif tree[end] == ')':
            depth -= 1
        if depth == 0:
            break
        end += 1

    # 提取SBAR字符串
    sbar_part = tree[start:end + 1]

    # 提取非SBAR部分
    before_sbar = tree[:sbar_index]
    after_sbar = tree[end + 1:]

    # 删除额外的空格和不必要的括号
    rest_of_sentence = before_sbar.strip() + after_sbar.strip()
    rest_of_sentence = rest_of_sentence.replace('(ROOT ', '').replace(' (. .))', '').strip()

    return sbar_part, rest_of_sentence


#第二部分，移除所有词性标记的模式（即移除例如(NP, VP等）
def extract_text_from_tree(tree_part):
    import re
    # 使用更宽泛的匹配模式，并正确处理词性标签中的特殊字符
    # \S+ 匹配任意非空白字符序列，[^()\s]+ 匹配不含括号和空白的字符序列
    text_parts = re.findall(r'\(\S+ ([^()\s]+)\)', tree_part)

    # 将结果连接成单个字符串，并处理常见的标点符号问题
    sentence = ' '.join(text_parts)
    sentence = sentence.replace(' ,', ',').replace(' .', '.').replace(' ?', '?').replace(' !', '!').replace(" 's", "'s").replace(' ;', ';').replace(' :', ':')
    return sentence
def division(tree_str):

    # 构成树字符串
    #tree_str = "(ROOT (S (VP (VB Turn) (NP (PRP$ your) (NNS lights)) (PRT (RP on)) (SBAR (WHADVP (WRB when)) (S (S (NP (DT a) (ADJP (JJ open) (HYPH /) (JJ close)) (NN sensor)) (VP (VBZ opens))) (CC and) (S (NP (DT the) (NN space)) (VP (VBZ is) (ADJP (JJ dark))))))) (. .)))"

    # 调用函数并打印结果
    sbar_part, rest_of_sentence = extract_parts(tree_str)
    print("SBAR part:", sbar_part)
    print("Rest of the sentence:", rest_of_sentence)
    print()
    sbar_part_after_extracting=extract_text_from_tree(sbar_part)
    rest_of_sentence_after_extracting=extract_text_from_tree(rest_of_sentence)
    print("Event part:", sbar_part_after_extracting)
    print("Command part:",rest_of_sentence_after_extracting)
    return [sbar_part_after_extracting,rest_of_sentence_after_extracting]