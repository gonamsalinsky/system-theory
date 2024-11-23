import pandas as pd


def create_rules(user_label, task_label):
    rules = []

    rules.append((
        """Если состояния s1 и s2 связаны отношением «переходить в», то необходимо создать соответствующий переход.""",
        f"""MATCH (s1:{user_label}:{task_label})-[{{name: "переходить в"}}]->(s2:{user_label}:{task_label})
MERGE (p:{user_label}:{task_label}:Transition {{name: 'Переход из «' + s1.name + '» в «' + s2.name + '»'}})
MERGE (p)-[:SEMANTIC {{name: 'быть переходом из'}}]->(s1)
MERGE (p)-[:SEMANTIC {{name: 'быть переходом в'}}]->(s2)"""
    ))

    return pd.DataFrame(rules, columns=['desc', 'code'])
