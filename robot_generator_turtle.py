from jinja2 import Template
from robot_generator import get_states, get_states_to_transit, get_condition, get_operations_after_transition
from dotenv import load_dotenv
import neo4j_db_connector as nc
import os


def get_start_state(conn, user_label):
    query = f'MATCH (a:{user_label}:Robot:State) ' \
            f'WHERE NOT (:{user_label}:Robot:State)-[{{name: "переходить в"}}]->(a) RETURN a'
    res = conn.query(query)
    return res[0]['a']['codename']


def get_end_state(conn, user_label):
    query = f'MATCH (a:{user_label}:Robot:State) ' \
            f'WHERE NOT (a)-[{{name: "переходить в"}}]->(:{user_label}:Robot:State) RETURN a'
    res = conn.query(query)
    return res[0]['a']['codename']


def get_state_dict(conn, user_label, end_state):
    res = {}
    states = get_states(conn, user_label)

    for state in states:
        if state != end_state:
            transition_list = []
            linked_states = get_states_to_transit(states[state], conn, user_label)

            for linked_state in linked_states:
                trans_info = {}

                trans_info['state_to'] = linked_state

                condition = get_condition(states[state], linked_states[linked_state], conn, user_label)
                trans_info['condition'] = condition[0]

                actions_after = get_operations_after_transition(condition[1], conn, user_label)
                trans_info['actions_after'] = {i['codename']: i['name'] for _, i in actions_after.iterrows()}

                transition_list.append(trans_info)

            res[state] = transition_list
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

