import json


class Rule:

    def __init__(self, trigger: dict, condition: dict, action: dict):
        # 假设为trigger(T)-condition(C)-action(A)的格式
        # condition可能为空
        self.trigger = trigger  # 字典格式表示event的subject, attribute, constraint, extraConstraint
        self.condition = condition  # 字典格式表示state的subject, attribute, constraint
        self.action = action  ##字典格式表示event的subject, attribute, constraint, extraConstraint

    def __repr__(self):
        return f"trigger={self.trigger}\ncondition={self.condition}\naction={self.action}"

    def ruleToCorrelation(self):
        # rule一定是‘e2e’ correlation
        # 下面为临时格式
        event = Event(self.trigger["subject"], self.trigger["attribute"], self.trigger["constraint"],
                      self.trigger["extraConstraint"])
        if self.condition == None:
            condition_state = None
        else:
            condition_state = State(self.condition["subject"], self.condition["attribute"],
                                    self.condition["constraint"])
        followed_event_or_state = Event(self.action["subject"], self.action["attribute"], self.action["constraint"],
                                        self.action["extraConstraint"])
        correlationType = "e2e"
        return Correlation(event, condition_state, followed_event_or_state, correlationType)


class Event:

    def __init__(self, subject, attribute, constraint, extraConstraint=None):
        self.subject = subject
        self.attribute = attribute
        self.constraint = constraint
        self.extraConstraint = extraConstraint

    def __repr__(self):
        return f"Event(subject='{self.subject}', attribute='{self.attribute}', constraint='{self.constraint}'," \
               f"extraConstraint='{self.extraConstraint}')"

    def __eq__(self, other):
        #防止将非None对象和None对象进行比较会报错
        if self is None and other is None:
            return True
        elif self is None or other is None:
            return False
        else:
            return self.subject == other.subject and self.attribute == other.attribute and self.constraint == other.constraint and self.extraConstraint == other.extraConstraint


class State:

    def __init__(self, subject, attribute, constraint):
        self.subject = subject
        self.attribute = attribute
        self.constraint = constraint

    def __repr__(self):
        return f"State(subject='{self.subject}', attribute='{self.attribute}', constraint='{self.constraint}')"

    def __eq__(self, other):
        if self is None and other is None:
            return True
        elif self is None or other is None:
            return False
        else:
            return self.subject == other.subject and self.attribute == other.attribute and self.constraint == other.constraint


class Correlation:

    def __init__(self, event: Event, conditionState: State, followedEventOrState, correlationType: str):
        self.event = event
        self.conditionState = conditionState
        self.followedEventOrState = followedEventOrState
        self.type = type
        if isinstance(followedEventOrState, Event):
            self.type = "e2e"
        elif isinstance(followedEventOrState, State):
            self.type = "e2s"
        else:
            raise ValueError("followedEventOrState必须是Event或State的实例")

    def __repr__(self):
        if self.type == "e2e":
            return f"'{self.type}' correlation:\npre_event={self.event}\ncondition={self.conditionState}\nfollowing_event={self.followedEventOrState}"
        else:
            return f"'{self.type}' correlation:\npre_event={self.event}\ncondition={self.conditionState}\nfollowing_state={self.followedEventOrState}"

    def __eq__(self, other):
        #防止将非None对象和None对象进行比较会报错
        if self is None and other is None:
            return True
        elif self is None or other is None:
            return False
        else:
            return self.event == other.event and self.conditionState == other.conditionState and self.followedEventOrState == other.followedEventOrState and self.type == other.type

    def simplify(self):
        if self.conditionState != None:
            if self.event.subject == self.conditionState.subject and self.event.attribute == self.conditionState.attribute:
                print("The correlation has been simplified.")
                self.conditionState = None
            else:
                print("The correlation cannot be simplified.")
        else:
            print("No condition to simplify.")

    def propose(self):
        if self.conditionState == None:
            state = State(subject=self.event.subject, attribute=self.event.attribute, constraint=self.event.constraint)
            new_correlation = Correlation(event=self.followedEventOrState, conditionState=None,
                                          followedEventOrState=state, correlationType="e2s")
            print(f"new correlation:\n{new_correlation}")
            return new_correlation
        else:
            print("propose failed.")


# #以下六个函数均用于将生成的所有相关性保存在json文件中，可以方便的实现文件读取。
def correlation_to_dict(correlation):
    return {
        'event': vars(correlation.event),
        'conditionState': None if correlation.conditionState is None else vars(correlation.conditionState),
        'followedEventOrState': vars(correlation.followedEventOrState),
        'type': correlation.type
    }


def save_correlations_to_json(correlations, filename):
    correlations_dict = [correlation_to_dict(correlation) for correlation in correlations]
    with open(filename, 'w') as f:
        json.dump(correlations_dict, f, indent=4)


def dict_to_event(event_dict):
    return Event(**event_dict)


def dict_to_state(state_dict):
    return State(**state_dict) if state_dict is not None else None


def dict_to_correlation(correlation_dict):
    event = dict_to_event(correlation_dict['event'])
    conditionState = dict_to_state(correlation_dict['conditionState'])
    followed = correlation_dict['followedEventOrState']
    if correlation_dict['type'] == 'e2e':
        followed = dict_to_event(followed)
    else:  # 'e2s'
        followed = dict_to_state(followed)
    return Correlation(event, conditionState, followed, correlation_dict['type'])


def load_correlations_from_json(filename):
    with open(filename, 'r') as f:
        correlations_dict = json.load(f)
    return [dict_to_correlation(correlation) for correlation in correlations_dict]


if __name__ == "__main__":
    trigger = {"subject": "motionSensor", "attribute": "motion", "constraint": "active", "extraConstraint": None}
    # condition = {"subject": "temperatureSensor", "attribute": "temperature", "constraint": ">30"}
    # 一个rule的condition可能不存在
    condition = None

    # trigger= {"subject": "light", "attribute": "illuminace", "constraint": "<30", "extraConstraint": None}
    # condition={"subject": "light", "attribute": "illuminace", "constraint": "<30"}
    action = {"subject": "airConditioner", "attribute": "switch", "constraint": "on", "extraConstraint": None}

    rule = Rule(trigger, condition, action)
    print(f"create a rule:\n{rule}")
    correlation = rule.ruleToCorrelation()
    print()

    print(f"convert a rule to a correlation:\n{correlation}")
    print()

    print("simplify a correlation:")
    correlation.simplify()
    print(correlation)
    print()

    print("further propose:")
    correlation.propose()
    print()

    pre = Event("motionsensor", "motion", "active", None)
    ev = Event("light", "illuminance", "high", None)
    corr = Correlation(pre, None, ev, "e2e")
    print(corr)
