from dotenv import load_dotenv
import os
import types
import neo4j_db_connector as nc
import pandas as pd

import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

import b2c_relations
import b2c_nodes
import b2c_rules
from b2c_generator import get_events

import robot_nodes
import robot_relations
import robot_rules
# from robot_generator import get_code
from robot_generator_turtle import get_template


load_dotenv()
conn = nc.Neo4jConnection(uri=os.getenv("NEO4J_URI"),
                          user=os.getenv("NEO4J_USERNAME"),
                          pwd=os.getenv("NEO4J_PASSWORD"))


def get_all_subclasses(ni, res: list):
    """Получение всех допустимых классов объектов"""
    for node in ni.__subclasses__():
        if isinstance(node.__init__, types.FunctionType):
            res.append(node)
        if len(node.__subclasses__()) > 0:
            get_all_subclasses(node, res)
    return res


def get_text_input_value(lbl, values):
    v = st.text_input(lbl)
    values.append(v)


def get_node_form(selected_ntype, node_types_avail, user_label, task_label):
    """Отрисовка формы для добавления объекта"""
    for node in node_types_avail:
        if node.__name__ == selected_ntype:
            attrs = [i for i in node.__init__.__code__.co_varnames if i != 'self']
            with st.form("add_node" + task_label):
                attr_values = []
                for attr in attrs:
                    if attr == 'user_label':
                        attr_values.append(user_label)
                    else:
                        get_text_input_value(attr, attr_values)

                submitted = st.form_submit_button("Создать")
                if submitted:
                    n = node(*attr_values)
                    n.db_merge_node(conn)
                    st.caption('Объект успешно создан')


def get_items_by_type(node_type, task_label, user_label):
    query = f"MATCH (a:{node_type}:{task_label}:{user_label}) RETURN a.name AS name"
    print(query)
    db_nodes = conn.query(query)
    print(db_nodes)
    return [n["name"] for n in db_nodes]


def get_node_class_from_db_result(db_node, task_label, user_label, node_module):
    """Получает экземпляра класса Nodes из элемента результата выполнения запроса, возвращающего список узлов"""
    nds = get_all_subclasses(node_module.NodeItem, [])
    # print(db_node)
    # print(nds)
    for node in nds:
        for label in db_node.labels:
            if label not in [user_label, task_label]:
                if node.__name__ == label:
                    attrs = [i for i in node.__init__.__code__.co_varnames if i != 'self']
                    attr_values = []
                    for attr in attrs:
                        if attr == 'user_label':
                            attr_values.append(user_label)
                        else:
                            attr_values.append(db_node[attr])
                    return node(*attr_values)
    return None


def get_node_class(node_name, node_type, task_label, user_label, node_module):
    """Получение экземпляра класса Nodes на основе его названия и типа"""
    query = f'MATCH (a:{node_type}:{user_label}:{task_label} {{name: "{node_name}"}}) RETURN a'
    db_nodes = conn.query(query)
    return get_node_class_from_db_result(db_nodes[0]['a'], task_label, user_label, node_module)


def get_relation_form(selected_rtype, rel_types_avail, task_label, user_label, node_module):
    """Отрисовка формы для добавления связи"""
    for rel in rel_types_avail:
        if rel.__name__ == selected_rtype:
            for cnstr in rel.constraints:
                main_node_type = cnstr[0]
                related_node_type = cnstr[1]
                # print(main_node_type, related_node_type)
                with st.form(f"add_node_{main_node_type}_{related_node_type}"):
                    main_node_name = st.selectbox(main_node_type,
                                                  get_items_by_type(main_node_type, task_label, user_label),
                                                  key=f'n1_{main_node_type}_{related_node_type}')
                    related_node_name = st.selectbox(related_node_type,
                                                     get_items_by_type(related_node_type, task_label, user_label),
                                                     key=f'n2_{main_node_type}_{related_node_type}')
                    submitted = st.form_submit_button("Создать")
                    if submitted:
                        main_node = get_node_class(main_node_name, main_node_type,
                                                   task_label, user_label, node_module)
                        related_node = get_node_class(related_node_name, related_node_type,
                                                      task_label, user_label, node_module)
                        # print(main_node)
                        # print(related_node)
                        r = rel(main_node, related_node)
                        r.db_create_relation(conn)
                        st.caption('Связь успешно создана')


def get_color_dict(n_types, colors, task_label):
    res = {}
    for i, n_type in enumerate(n_types):
        if i + 1 >= len(colors):
            colors.extend(colors)
        res[n_type] = colors[i]
    return res


def get_graph(task_label, user_label):
    nodes = []
    edges = []

    query_nodes = f'MATCH (a:{task_label}:{user_label}) RETURN a'
    db_nodes = conn.query(query_nodes)

    colors = ['#f6511d', '#ffb400', '#00a6ed', '#7fb800', '#0d2c54', '#a2a2a2']

    node_types = []
    for db_node in db_nodes:
        n_labels = db_node['a'].labels
        for label in n_labels:
            if label not in [task_label, user_label] and label not in node_types:
                node_types.append(label)

    color_dict = get_color_dict(node_types, colors, task_label)
    # print(color_dict)
    for db_node in db_nodes:
        n_label = [l for l in db_node['a'].labels
                   if l not in [task_label, user_label,
                                'View', 'Click', 'Scroll', 'Type', 'Button', 'Screen', 'Banner', 'Block']][0]
        # print(n_label)
        # print(db_node['a'])
        nodes.append(Node(id=db_node['a'].element_id,
                          title=str({i[0]: i[1] for i in db_node['a'].items() if i[0] != 'name'}),
                          label=db_node['a']['name'], size=25, color=color_dict[n_label]))

    query_rels = f'MATCH (:{task_label}:{user_label})-[r]-(:{task_label}:{user_label}) RETURN r'
    db_rels = conn.query(query_rels)
    for db_rel in db_rels:
        edges.append(Edge(source=db_rel['r'].nodes[0].element_id,
                          label=db_rel['r']['name'],
                          type="CURVE_SMOOTH",
                          target=db_rel['r'].nodes[1].element_id))

    graph_config = Config(width=750,
                          height=500,
                          directed=True,
                          physics=False,
                          hierarchical=False,
                          collapsible=True,
                          dragNodes=True,
                          key=task_label
                          )

    return agraph(nodes=nodes, edges=edges, config=graph_config)


def get_relation_class_from_db_result(db_relation, source_node, target_node, relation_module):
    rels = get_all_subclasses(relation_module.RelationItem, [])
    for rel in rels:
        if rel.rel_name == db_relation['name']:
            return rel(source_node, target_node)
    return None


def get_relations_from_db(user_label, task_label, node_module, relation_module):
    result = conn.query(f"MATCH (s:{user_label}:{task_label})-[r]->(t:{user_label}:{task_label}) RETURN s,t,r")
    rels_list = []
    for relation in result:
        source_node = get_node_class_from_db_result(relation['s'], task_label, user_label, node_module)
        target_node = get_node_class_from_db_result(relation['t'], task_label, user_label, node_module)
        relation = get_relation_class_from_db_result(relation['r'], source_node, target_node, relation_module)
        rels_list.append((source_node, target_node, relation))
    return rels_list


def get_task_content(task_label, user_label, title, node_module, relations_module, rules_module):
    st.title(title)
    if user_label != 'demo':
    # if True:
        st.header('Создание модели')

        st.subheader('Создание объектов')
        node_types = get_all_subclasses(node_module.NodeItem, [])

        node_dict = {}
        for i in node_types:
            node_dict[i.__name__] = i.class_name
        # node_labels = [i.__name__ for i in node_types]
        selected_node_label = st.selectbox("Класс объекта", node_dict.values())
        selected_node_type = [i for i in node_dict if node_dict[i] == selected_node_label][0]
        get_node_form(selected_node_type, node_types, user_label, task_label)

        st.subheader('Создание связей')
        rel_types = get_all_subclasses(relations_module.RelationItem, [])
        rel_dict = {}
        for i in rel_types:
            rel_dict[i.__name__] = i.rel_name
        # rel_labels = [i.__name__ for i in rel_types]
        selected_rel_label = st.selectbox("Тип связи", rel_dict.values())
        selected_rel_type = [i for i in rel_dict if rel_dict[i] == selected_rel_label][0]
        get_relation_form(selected_rel_type, rel_types, task_label, user_label, node_module)
        st.divider()

    st.header('Визуализация модели')
    get_graph(task_label, user_label)
    st.divider()

    st.header('Правила')
    rules_df = rules_module.create_rules(user_label, task_label)
    for _, row in rules_df.iterrows():
        st.code(row['code'], language='cypher')
        st.caption(row['desc'])

    if user_label != 'demo':
    # if True:
        rules_btn = st.button("Запустить правила", key="trigger_rules"+task_label)
        if rules_btn:
            for _, row in rules_df.iterrows():
                if not row['code'] is None:
                    conn.query(row['code'])
                    st.caption('Правила успешно выполнены')
                    st.experimental_rerun()
        st.divider()

        st.header('Удаление')

        st.subheader('Удаление объектов')
        all_nodes_db = conn.query(f"MATCH (a:{task_label}:{user_label}) RETURN a")
        if len(all_nodes_db) == 0:
            st.text("В модели пока нет объектов.")
        else:
            all_nodes = [get_node_class_from_db_result(i['a'], task_label, user_label, node_module) for i in all_nodes_db]
            all_nodes_df = pd.DataFrame()
            all_nodes_df['name'] = [i.name for i in all_nodes]
            all_nodes_df['node'] = all_nodes
            selected_node_name_for_removal = st.selectbox("Объект", all_nodes_df)
            selected_node_index = all_nodes_df[all_nodes_df['name'] == selected_node_name_for_removal].index[0]
            del_object_btn = st.button("Удалить объект", key="delete_node"+task_label)
            if del_object_btn:
                all_nodes_df.loc[selected_node_index]['node'].db_delete_node(conn)  # TODO Добавить подтверждаение
                st.experimental_rerun()

        st.subheader('Удаление связи')
        all_relations = get_relations_from_db(user_label, task_label, node_module, relations_module)
        if len(all_relations) == 0:
            st.text("В модели пока нет связей.")
        else:
            all_rels_df = pd.DataFrame()
            all_rels_df['name'] = [f"{s.name} -> {r.rel_name} -> {t.name}" for s, t, r in all_relations]
            all_rels_df['relation'] = [r for _, _, r in all_relations]
            selected_rel_for_removal = st.selectbox("Связь", all_rels_df)
            selected_rel_index = all_rels_df[all_rels_df['name'] == selected_rel_for_removal].index[0]
            del_rel_btn = st.button("Удалить связь", key="delete_relation"+task_label)
            if del_rel_btn:
                all_rels_df.loc[selected_rel_index]['relation'].db_delete_relation(conn)  # TODO Добавить подтверждаение
                st.experimental_rerun()

        st.subheader('Удаление модели')
        del_btn = st.button("Удалить модель", key="delete_model"+task_label)  # TODO Добавить подтверждаение
        if del_btn:
            conn.query(f"MATCH (n:{task_label}:{user_label}) DETACH DELETE n")
            st.experimental_rerun()


if __name__ == '__main__':
    with open('pages/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    name, authentication_status, username = authenticator.login('Login', 'main')

    if st.session_state["authentication_status"]:
        tab1, tab2 = st.tabs(["Робот", "B2C"])
        with tab1:
            with st.expander("Варианты заданий"):
                st.image("robot_variants.png", width=300)
                with open("robot_description.md", mode='r') as f:
                    st.markdown(f.read())

            get_task_content('Robot', username, 'Моделирование траектории робота',
                             node_module=robot_nodes, relations_module=robot_relations, rules_module=robot_rules)
            st.divider()
            st.header("Генерация кода на основе модели")
            generate_btn = st.button("Сгенерировать код", key='generate_code_robot')
            if generate_btn:
                # st.code(get_code(conn, username), language='c')
                st.code(get_template(conn, username), language='python')

        with tab2:
            with st.expander("Варианты заданий"):
                with open("b2c_description.md", mode='r') as f:
                    st.markdown(f.read())
                st.image("b2c_example.jpg")

            get_task_content('B2C', username, 'Аналитика пользовательского поведения в B2C-сервисе',
                             node_module=b2c_nodes, relations_module=b2c_relations, rules_module=b2c_rules)
            st.divider()
            st.header("Генерация документации на основе модели")
            generate_b2c_btn = st.button("Сгенерировать документацию", key='generate_b2c')
            if generate_b2c_btn:
                st.markdown(get_events(conn, username))
        authenticator.logout('Выйти', 'main', key='unique_key')

    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')
