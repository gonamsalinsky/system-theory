from dotenv import load_dotenv
import neo4j_db_connector as nc
import os
import streamlit as st
import graphviz as graphviz
import pandas as pd
from b2c_rules import trigger_rules


load_dotenv()
CONN = nc.Neo4jConnection(uri=os.getenv("URI"), user=os.getenv("USERNAME"), pwd=os.getenv("PASSWORD"))
# conn = nc.Neo4jConnection(uri=os.getenv("URI_CLOUD"),
#                           user=os.getenv("USERNAME_CLOUD"),
#                           pwd=os.getenv("PASSWORD_CLOUD"))


def get_linked_entities(node_name, rel_type=""):
    """Получает информацию о связанных узлах"""
    query = f"MATCH ({{name: '{node_name}'}})-[r {rel_type}]-(a) " \
            f"RETURN a.name AS node_name, a.nodeType AS nodeType, ID(a) AS node_id, labels(a) AS node_labels, " \
            f"a.description AS node_desc, a.propertyName AS property_name, " \
            f"r.name AS rel_name, TYPE(r) AS rel_type, startNode(r).name AS start_node"
    # print(query)
    entities = CONN.query(query)
    entities_df = pd.DataFrame.from_records(
        entities,
        columns=[
            'node_name', 'nodeType', 'node_id', 'node_labels', 'node_desc', 'property_name',
            'rel_name', 'rel_type', 'start_node'])
    entities_df = entities_df[entities_df['rel_type'] != 'GENERATED']
    # сортировка – для того, чтобы поля ввода генерировались последовательно (сначала для обязательных элементов)
    entities_df['rel_type'] = pd.Categorical(entities_df['rel_type'], ["REQUIRED", "OPTIONAL"])

    # убираем дубликаты связанных отношением "иметь вид" узлов, т.к. в интерфейсе для всех них предусмотрено одно поле
    types_df = entities_df[entities_df['rel_name'] == 'иметь вид']
    types_df = types_df[types_df['start_node'] != types_df['node_name']]
    types_df = types_df.drop_duplicates(subset=['start_node'])
    no_types_df = entities_df[entities_df['rel_name'] != 'иметь вид']
    entities_df = pd.concat([no_types_df, types_df])

    return entities_df.sort_values("rel_type")


def get_properties_str(prs: dict):
    """Преобразует словарь в строку свойств для Cypher-запроса"""
    prs_str = ''
    for key, value in prs.items():
        prs_str += f"{key}: '{value}', "
    return prs_str[:-2]


def get_options(node_id, rel_type='иметь значение'):
    """Получает список значений свойств"""
    query = f"MATCH (a)-[{{name: '{rel_type}'}}]->(b) " \
            f"WHERE ID(a) = {node_id} " \
            f"RETURN b.name AS name"
    # print(query)
    properties = CONN.query(query)
    return [pr["name"] for pr in properties]


def add_entity(p_entity, p_properties, p_previous_prs, f_iteration=False):
    """Добавляет сущность или сущность со связью в онтологию"""
    labels = p_entity['nodeType'] + p_entity['node_labels']
    labels.remove('Meta')

    prs_str = get_properties_str(p_properties)
    print(p_entity)
    if f_iteration:
        labels.remove('Base')
        query = f"MERGE (:{':'.join(labels)} {{{prs_str}}})"
        res = CONN.query(query)
        return False if res == None else True
    else:
        pr_prs_str = get_properties_str(p_previous_prs)
        match_prev = f"(prev {{{pr_prs_str}}})"
        match_curr = f"(curr:{':'.join(labels)} {{{prs_str}}})"
        query_1 = f"MERGE {match_prev}"
        query_2 = f"MERGE {match_curr}"
        query_3 = f"MATCH {match_prev}, {match_curr} " \
                  f"MERGE (prev)-[:{p_entity['rel_type']} {{name: '{p_entity['rel_name']}'}}]->(curr)"
        res_1 = CONN.query(query_1)
        res_2 = CONN.query(query_2)
        res_3 = CONN.query(query_3)
        return False if res_1 == None or res_2 == None or res_3 == None else True


def get_graph_info(p_entity, p_previous, p_previous_prs):
    """Рисует картинку о связи с предыдущей сущностью"""
    previous_name = p_previous_prs['name'] if 'name' in p_previous_prs.keys() \
        else p_previous_prs[list(p_previous_prs.keys())[0]]
    graph = graphviz.Digraph()
    graph.attr('node', shape='box')
    graph.node(f"{p_previous['node_name']} «{previous_name}»")
    graph.node(p_entity['node_name'])
    if p_entity["start_node"] == p_previous['node_name'] or p_entity["start_node"] != p_entity["node_name"]:
        graph.edge(f"{p_previous['node_name']} «{previous_name}»", p_entity['node_name'], label=p_entity['rel_name'])
    else:
        graph.edge(p_entity['node_name'], f"{p_previous['node_name']} «{previous_name}»", label=p_entity['rel_name'])
    return graph


def get_existing_nodes(p_entity, property_name, f_iteration):
    labels = p_entity['nodeType'] + p_entity['node_labels']
    labels.remove('Meta')
    if 'Base' in labels:
        labels.remove('Base')
    query = f"MATCH (a:{':'.join(labels)}) RETURN a.{property_name} AS {property_name}"
    res = CONN.query(query)
    return [i[property_name] for i in res]


def create_property_section(linked_entity, properties, entity, key_name, first_iteration):
    options = get_options(linked_entity["node_id"])
    # отмечаем звездочкой необязательные поля
    input_label = linked_entity["node_name"] if linked_entity["rel_type"] == "REQUIRED" \
        else linked_entity["node_name"] + ' *'
    if len(options) > 0:  # если есть заданные значения свойств, показываем выпадающий список
        selected_property = st.selectbox(
            input_label, options=[''] + options, help=linked_entity["node_desc"], key=key_name)
    else:  # если заданных значений свойств нет, показываем поле ввода
        if linked_entity["rel_type"] == "REQUIRED":
            inp1, inp2 = st.columns(2)
            input_data = inp1.text_input(input_label, help=linked_entity["node_desc"], key=key_name)
            existing_nodes = get_existing_nodes(entity, linked_entity["property_name"], first_iteration)
            selected_data = inp2.selectbox('Выбрать из существующих', key=key_name,
                                           options=[''] + existing_nodes)
            selected_property = input_data if selected_data == '' else selected_data
        else:
            selected_property = st.text_input(input_label, help=linked_entity["node_desc"], key=key_name)
    if selected_property != '':
        properties[linked_entity["property_name"]] = selected_property
    return properties


def generate_interface_section(
        entity,  # текущая сущность с полями в формате Series
        optional=False,  # является ли связь с предыдущей сущностью опциональной
        first_iteration=False,  # является ли это первой итерацией (используется для форматирования заголовков)
        previous=None,  # информация о предыдущей сущности в формате Series
        previous_prs=None,  # информация о свойствах экземпляра предыдущей сущности (информация из поля ввода)
        key_name=None,  # уникальный ключ для элементов интерфейса
        section_type='general'  # тип секции; возможные значения: types (родовидовые отношения с предыдущей сущностью)
):
    # вывод заголовка / подзаголовка
    header = entity["node_name"] + ' *' if optional else entity["node_name"]
    if first_iteration:
        st.header(header)
    elif section_type == 'general':
        st.markdown(f"### {header}")
    else:
        st.markdown(f"#### {header}")

    # вывод графической информации о связи с предыдущей связанной сущностью
    if not first_iteration and not section_type == 'types':
        st.graphviz_chart(get_graph_info(entity, previous, previous_prs))

    linked_entities = get_linked_entities(entity["node_name"])

    # ввод свойств сущностей (при наличии)
    properties = {}
    has_types = False
    for _, linked_entity in linked_entities.iterrows():
        if linked_entity["rel_name"] == 'иметь свойство':
            properties = create_property_section(linked_entity, properties, entity, key_name, first_iteration)
        if linked_entity["rel_name"] == 'иметь вид' and linked_entity['start_node'] == entity["node_name"]:
            options = get_options(entity["node_id"], rel_type=linked_entity["rel_name"])
            node_type = st.selectbox("Вид", options=options, key=key_name)
            if st.checkbox("Заполнить информацию о виде", key=key_name):
                entities = CONN.query(f"MATCH (parent)-[{{name: 'иметь вид'}}]->(a {{name: '{node_type}'}})"
                                      f", (p_parent {{name: '{previous['node_name']}'}})-[r]->(parent)"
                                      f"RETURN a.name AS node_name, ID(a) AS node_id, "
                                      f"a.nodeType AS nodeType, labels(a) AS node_labels"
                                      f", r.name AS rel_name, TYPE(r) AS rel_type"
                                      )
                entities_df = pd.DataFrame.from_records(
                    entities, columns=['node_name', 'node_id', 'nodeType', 'node_labels', 'rel_name', 'rel_type'])
                for _, i in entities_df.iterrows():
                    pr_prs = generate_interface_section(i, section_type='types', previous_prs=previous_prs,
                        key_name=previous_prs['name'] + linked_entity['node_name'] + node_type)
            has_types = True
    print(properties)

    # кнопка "Добавить"
    if not has_types:
        col1, col2 = st.columns([8, 1])
        if col1.button(f"Добавить {entity['node_name'].lower()}", key=key_name):
            if add_entity(entity, properties, previous_prs, first_iteration):
                col2.caption('Добавлено')
                trigger_rules(CONN)

    linked_entities_f = linked_entities.query('rel_name != "иметь свойство" and rel_name != "иметь вид"')
    linked_entities_f = linked_entities_f[linked_entities_f["start_node"] == entity["node_name"]]
    if linked_entities_f.shape[0] > 0:
        # опция для показа связанные сущности (реализовано как чекбокс)
        if st.checkbox("Заполнить связанную информацию", key=key_name):
            # рекурсивный вызов функции для следуюшего узла, связанного с текущим обязательным исходящим отношением
            for n, linked_entity in linked_entities_f.iterrows():
                optional = True if linked_entity['rel_type'] == 'OPTIONAL' else False

                # если нет свойств, то берем свойства, связанных отношением "быть типом" узлов
                new_previous_prs = properties if len(properties.items()) > 0 else pr_prs
                generate_interface_section(linked_entity, optional=optional, previous=entity,
                                           previous_prs=new_previous_prs,
                                           key_name=new_previous_prs[list(new_previous_prs.keys())[0]] + str(n))
    return properties


if __name__ == '__main__':
    st.title('Создание онтологии проекта')
    base_entities = CONN.query("MATCH (a:Meta:Base) RETURN a.name AS node_name")
    selected_base = st.selectbox('Базовая сущность', options=[i['node_name'] for i in base_entities])
    entities = CONN.query(f"MATCH (a:Meta:Base) WHERE a.name = '{selected_base}' "
                          "RETURN a.name AS node_name, ID(a) AS node_id, a.nodeType AS nodeType, "
                          "labels(a) AS node_labels")
    entities_df = pd.DataFrame.from_records(entities, columns=['node_name', 'node_id', 'nodeType', 'node_labels'])
    if st.checkbox('Начать', key='start'):
        generate_interface_section(entities_df.iloc[:1].squeeze(), first_iteration=True, previous_prs={'name': 'Base'})
    # for _, i in entities_df.iterrows():
    #     generate_interface_section(i, first_iteration=True, previous_prs={'name': 'Base'})
