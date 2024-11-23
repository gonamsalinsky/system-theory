import pandas as pd


def create_rules(user_label, task_label):
    rules = []

#     rules.append((
#         """Если объекты s1 и a1, s2 и a2 (классов Step и Action соответственно)
# связаны отношением «материализоваться в»,
# а также объекты s1 и s2 связаны отношением «предшествовать»,
# то объекты a1 и a2 тоже связаны отношением «предшествовать».""",
#         """MATCH (s1:Step)-[{name: 'материализоваться в'}]->(a1:Action)
# MATCH (s1:Step)-[{name: 'предшествовать'}]->(s2:Step)
# MATCH (s2:Step)-[{name: 'материализоваться в'}]->(a2:Action)
# MERGE (a1)-[:SEMANTIC {name: 'предшествовать'}]->(a2)"""
#     ))

    rules.append((
        "Если действие a предполагает взаимодействие с элементом интерфейса i, "
        "а также элемент интерфейса i является частью другого элемента интерфейса i_p, то "
        "необходимо создать событие, связанное с действием a отношением «вызывать», "
        "название которого будет формироваться на основе свойств codename элементов интерфейса i и i_p, "
        "а также подтипа действия a.",
        f"""MATCH (a:{task_label}:{user_label}:Action)-[{{name: 'предполагать взаимодействие с'}}]->(i:{task_label}:{user_label}:Interface)
OPTIONAL MATCH (i:{task_label}:{user_label}:Interface)-[{{name: 'являться частью'}}]->(i_p:{task_label}:{user_label}:Interface)
UNWIND labels(a) AS a_lbls
UNWIND labels(i) AS i_lbls
WITH DISTINCT a, 
    a.name AS act_name, 
    CASE WHEN a_lbls IN ['B2C', 'demo', 'Action', '{user_label}'] THEN '' 
        ELSE a_lbls END AS act_type,
    i.name AS i_name,
    i.codename AS i_codename,
    CASE WHEN i_lbls IN ['B2C', 'demo', 'Interface'] THEN '' 
        ELSE i_lbls END AS i_type,
    CASE WHEN i_p.codename IS NULL THEN '' 
        ELSE i_p.codename + "_" END AS i_p_codename
WHERE act_type <> '' AND i_type <> ''
MERGE (a)-[:SEMANTIC {{name: "вызывать"}}]->(i:{task_label}:{user_label}:Event {{name: i_p_codename + i_codename + "_" + act_type, description: act_name}})"""
    ))

    return pd.DataFrame(rules, columns=['desc', 'code'])
