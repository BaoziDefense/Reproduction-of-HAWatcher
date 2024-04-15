import semantic_analysis


#已知的rule转化后都是e2e 的smartapp correlation
#原14条rule，将rule 5和rule 7拆开，rule 6和rule 8各算两条，所以总计18条rule
knownRules=[]
smartapp_correlations=[]
#1
trigger= {"subject": "M002", "attribute": "motion", "constraint": "ON", "extraConstraint": None}
condition=None
action = {"subject": "L001", "attribute": "lightingMode", "constraint": "ON", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#2
trigger= {"subject": "M002", "attribute": "motion", "constraint": "OFF", "extraConstraint": None}
condition=None
action = {"subject": "L001", "attribute": "lightingMode", "constraint": "OFF", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#3
trigger= {"subject": "M004", "attribute": "motion", "constraint": "ON", "extraConstraint": None}
condition=None
action = {"subject": "L002", "attribute": "lightingMode", "constraint": "ON", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#4
trigger= {"subject": "M004", "attribute": "motion", "constraint": "OFF", "extraConstraint": None}
condition=None
action = {"subject": "L002", "attribute": "lightingMode", "constraint": "OFF", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#5.1
trigger= {"subject": "M001", "attribute": "motion", "constraint": "ON", "extraConstraint": None}
condition={"subject": "L003", "attribute": "lightingMode", "constraint": "OFF"}
action = {"subject": "L003", "attribute": "lightingMode", "constraint": "ON", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#5.2
trigger= {"subject": "M003", "attribute": "motion", "constraint": "ON", "extraConstraint": None}
condition={"subject": "L003", "attribute": "lightingMode", "constraint": "OFF"}
action = {"subject": "L003", "attribute": "lightingMode", "constraint": "ON", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#6.1
trigger= {"subject": "M001", "attribute": "motion", "constraint": "OFF", "extraConstraint": None}
condition={"subject": "M003", "attribute": "motion", "constraint": "OFF"}
action = {"subject": "L003", "attribute": "lightingMode", "constraint": "OFF", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#6.2
trigger= {"subject": "M003", "attribute": "motion", "constraint": "OFF", "extraConstraint": None}
condition={"subject": "M001", "attribute": "motion", "constraint": "OFF"}
action = {"subject": "L003", "attribute": "lightingMode", "constraint": "OFF", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#7.1
trigger= {"subject": "M007", "attribute": "motion", "constraint": "ON", "extraConstraint": None}
condition={"subject": "L004", "attribute": "lightingMode", "constraint": "OFF"}
action = {"subject": "L004", "attribute": "lightingMode", "constraint": "ON", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#7.2
trigger= {"subject": "M008", "attribute": "motion", "constraint": "ON", "extraConstraint": None}
condition={"subject": "L004", "attribute": "lightingMode", "constraint": "OFF"}
action = {"subject": "L004", "attribute": "lightingMode", "constraint": "ON", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#8.1
trigger= {"subject": "M007", "attribute": "motion", "constraint": "OFF", "extraConstraint": None}
condition={"subject": "M008", "attribute": "motion", "constraint": "OFF"}
action = {"subject": "L004", "attribute": "lightingMode", "constraint": "OFF", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#8.2
trigger= {"subject": "M008", "attribute": "motion", "constraint": "OFF", "extraConstraint": None}
condition={"subject": "M007", "attribute": "motion", "constraint": "OFF"}
action = {"subject": "L004", "attribute": "lightingMode", "constraint": "OFF", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#9
trigger= {"subject": "T101", "attribute": "temperature", "constraint": ">=32", "extraConstraint": None}
condition={"subject": "Fan1", "attribute": "fanMode", "constraint": "OFF"}
action = {"subject": "Fan1", "attribute": "fanMode", "constraint": "ON", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#10
trigger= {"subject": "T101", "attribute": "temperature", "constraint": "<31", "extraConstraint": None}
condition={"subject": "Fan1", "attribute": "fanMode", "constraint": "ON"}
action = {"subject": "Fan1", "attribute": "fanMode", "constraint": "OFF", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#11
trigger= {"subject": "T103", "attribute": "temperature", "constraint": ">=25", "extraConstraint": None}
condition={"subject": "Fan2", "attribute": "fanMode", "constraint": "OFF"}
action = {"subject": "Fan2", "attribute": "fanMode", "constraint": "ON", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#12
trigger= {"subject": "T103", "attribute": "temperature", "constraint": "<24", "extraConstraint": None}
condition={"subject": "Fan2", "attribute": "fanMode", "constraint": "ON"}
action = {"subject": "Fan2", "attribute": "fanMode", "constraint": "OFF", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#13
trigger= {"subject": "T104", "attribute": "temperature", "constraint": ">=25", "extraConstraint": None}
condition={"subject": "Fan3", "attribute": "fanMode", "constraint": "OFF"}
action = {"subject": "Fan3", "attribute": "fanMode", "constraint": "ON", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)
#14
trigger= {"subject": "T104", "attribute": "temperature", "constraint": "<24", "extraConstraint": None}
condition={"subject": "Fan3", "attribute": "fanMode", "constraint": "ON"}
action = {"subject": "Fan3", "attribute": "fanMode", "constraint": "OFF", "extraConstraint": None}
rule = semantic_analysis.Rule(trigger, condition, action)
knownRules.append(rule)

for i in knownRules:
    smartapp_correlations.append(i.ruleToCorrelation())

if __name__ == "__main__":
    # print(len(knownRules))
    # print(knownRules)
    print(len(smartapp_correlations))
    print(smartapp_correlations)

