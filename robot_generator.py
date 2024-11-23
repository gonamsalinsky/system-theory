from csnake import CodeWriter, Function, Variable, Enum
import pandas as pd


def query_res_to_df(query_res):
    if len(query_res) == 0:
        return pd.DataFrame()
    cols = dict(query_res[0]).keys()
    data = {}
    for col in cols:
        vals = []
        for i in query_res:
            val = dict(i)[col]
            vals.append(val)
        data[col] = vals
    return pd.DataFrame(data=data).drop_duplicates(subset=[col for col in cols if col != 'labels'])


def get_states(conn, user_label):
    """Получает все доступные состояния"""
    query = f"MATCH (code:Robot:State:{user_label}) RETURN code"
    res = conn.query(query)
    print('get_states', res)
    return {r['code']['codename']: r['code']['name'] for r in res}


def get_states_to_transit(state_name, conn, user_label):
    """Получает все связанные состояния с заданным"""
    query = f"""
MATCH (state_1:State:{user_label} {{name: '{state_name}'}}), 
(state_1)-[ {{name: 'переходить в'}}]->(state_2)
RETURN state_1.name, state_2.name, state_2.codename"""
    res = conn.query(query)
    print('get_states_to_transit', res)
    return {i['state_2.codename']: i['state_2.name'] for i in res}


def get_operations_before_transition(state_name, conn, user_label):
    """Получает все операции, которые необходимо выполнить до перехода"""
    query = f"""
MATCH (s:State:{user_label} {{name: '{state_name}'}}), 
(t)-[{{name: 'быть переходом из'}}]->(s),
(process_name)-[ {{name: 'предшествовать'}}]->(t)
RETURN process_name.name as name, process_name.codename as codename, labels(process_name) as labels
"""
    res = conn.query(query)
    print('get_operations_before_transition', res)
    return query_res_to_df(res)
    # return {dict(i)['process_code.codename']: dict(i)['process_name.name'] for i in res}


def get_condition(s_1, s_2, conn, user_label):
    """Получает условие перехода"""
    print(s_1, s_2)
    query = f"""
MATCH (state_1:State:{user_label} {{name: '{s_1}'}}), (state_2:State:{user_label} {{name: '{s_2}'}}),
(t)-[ {{name: 'быть переходом из'}}]->(state_1), (t)-[ {{name: 'быть переходом в'}}]->(state_2),
(p)-[ {{name: 'быть условием перехода'}}]->(t)
RETURN p.name, p.codename"""
    print(query)
    res = conn.query(query)
    print('get_condition', res)
    if len(res) > 0:
        return res[0]['p.codename'], res[0]['p.name']
    else:
        return None, None


def get_operations_after_transition(predicate, conn, user_label):
    """Получает все операции, которые необходимо выполнить после перехода"""
    query = f"""
MATCH (pr:Predicate:{user_label} {{name: '{predicate}'}}),
(pr)-[ {{name: 'быть условием перехода'}}]->(t),
(t)-[ {{name: 'вызывать'}}]->(p)
RETURN p.name as name, p.codename as codename, labels(p) as labels"""
    res = conn.query(query)
    print('get_operations_after_transition', res)
    return query_res_to_df(res)
    # return {dict(i)['p_code.codename']: dict(i)['p.name'] for i in res}


def add_process_lines(p_cwr, df):
    for _, row in df.iterrows():
        line = row['codename']
        if 'Function' in row['labels']:
            line += '()'
        p_cwr.add_line(line+';', comment=row['name'])


def get_code(connection, user_label):
    cwr = CodeWriter()

    # состояния
    states = get_states(connection, user_label)
    enum = Enum('STATES')
    enum.add_values(states.keys())
    cwr.add_enum(enum)

    # switch
    cwr_switch = CodeWriter()
    var = Variable('state', 'str')

    cwr_switch.start_switch(var)

    for key_state in states:
        # состояние, из которого осуществляется переход
        state_var = Variable(key_state, 'str')
        cwr_switch.add_switch_case(state_var)

        # действие, которое необходимо выполнить до перехода
        # TODO увести внуть цикла
        pr_before = get_operations_before_transition(states[key_state], connection, user_label)
        add_process_lines(cwr_switch, pr_before)

        sts_to_transit = get_states_to_transit(states[key_state], connection, user_label)

        for key_state_2 in sts_to_transit.keys():
            # условие перехода
            cond, cond_comm = get_condition(states[key_state], sts_to_transit[key_state_2], connection, user_label)
            cwr_switch.add_line(f'if ({cond}) {{', comment=cond_comm)
            cwr_switch.indent()

            # изменение состояния
            cwr_switch.add_line(f'state = {key_state_2};')

            # действие, которое необходимо выполнить после перехода
            pr_after = get_operations_after_transition(cond_comm, connection, user_label)
            # print(pr_after)
            add_process_lines(cwr_switch, pr_after)
            cwr_switch.close_brace()

        cwr_switch.add_switch_break()

    # объявляем функцию step()
    step_fun = Function('step', return_type='void')
    step_fun.add_code(cwr_switch)
    cwr.add_function_definition(step_fun)
    connection.close()
    print(cwr)
    return cwr
    # cwr.write_to_file('tmp/generated_step.c')
    #
    # with open('tmp/generated_step.c') as f:
    #     return f.read()
