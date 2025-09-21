from jinja2 import Template
from robot_generator import get_states, get_states_to_transit, get_condition, get_operations_after_transition
from dotenv import load_dotenv
import neo4j_db_connector as nc
import os

def get_start_state(conn, user_label):
    query = f'MATCH (a:{user_label}:Robot:State) WHERE NOT (:{user_label}:Robot:State)-[{{name: "переходить в"}}]->(a) RETURN a'
    res = conn.query(query)
    return res[0]['a']['codename']

def get_end_state(conn, user_label):
    query = f'MATCH (a:{user_label}:Robot:State) WHERE NOT (a)-[{{name: "переходить в"}}]->(:{user_label}:Robot:State) RETURN a'
    res = conn.query(query)
    return res[0]['a']['codename']

# НОВАЯ ФУНКЦИЯ для получения процессов
def get_processes_for_state(state_name, conn, user_label):
    """Получает все процессы, которые необходимо выполнить внутри состояния"""
    query = f"""
    MATCH (s:State:{user_label} {{name: '{state_name}'}})-[{{name: 'выполнять в'}}]->(p:Process:{user_label})
    RETURN p.name as name, p.codename as codename
    """
    res = conn.query(query)
    return {item['codename']: item['name'] for item in res}

def get_state_dict(conn, user_label, end_state):
    res = {}
    states = get_states(conn, user_label)

    for state_codename in states:
        state_name = states[state_codename]
        if state_codename != end_state:
            state_info = {}
            transition_list = []
            
            # Получаем процессы для текущего состояния
            state_info['processes'] = get_processes_for_state(state_name, conn, user_label)
            
            linked_states = get_states_to_transit(state_name, conn, user_label)

            for linked_state_codename in linked_states:
                trans_info = {}
                linked_state_name = linked_states[linked_state_codename]
                
                trans_info['state_to'] = linked_state_codename

                condition_codename, condition_name = get_condition(state_name, linked_state_name, conn, user_label)
                trans_info['condition'] = condition_codename

                actions_after = get_operations_after_transition(condition_name, conn, user_label)
                trans_info['actions_after'] = {i['codename']: i['name'] for _, i in actions_after.iterrows()}

                transition_list.append(trans_info)
            
            state_info['transitions'] = transition_list
            res[state_codename] = state_info
    return res

def get_template(conn, user_label):
    start_state = get_start_state(conn, user_label)
    end_state = get_end_state(conn, user_label)
    state_list = get_state_dict(conn, user_label, end_state)

    with open("robot_generator_template.jinja2") as f:
        res = Template(f.read(), trim_blocks=True, lstrip_blocks=True).render(
            start_state=start_state,
            end_state=end_state,
            state_list=state_list,
        )
    with open("robot_generated_code.py", mode='w') as f:
        f.write(res)
    return res

if __name__ == "__main__":
    load_dotenv()
    conn = nc.Neo4jConnection(uri=os.getenv("NEO4J_URI"),
                              user=os.getenv("NEO4J_USERNAME"),
                              pwd=os.getenv("NEO4J_PASSWORD"))
    print(get_template(conn, 'demo'))