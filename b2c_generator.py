def get_screens(conn, user_label):
    """Получает все доступные состояния"""
    query = f"MATCH (s:Screen:{user_label}) RETURN s"
    res = conn.query(query)
    return [r['s']['name'] for r in res]


def get_events_for_screen(conn, user_label, screen):
    """Получает все доступные состояния"""
    query_1 = f'MATCH (a:Action:{user_label})-[{{name: "вызывать"}}]-(event:Event:{user_label}) ' \
              f'MATCH (a)-[{{name: "предполагать взаимодействие с"}}]->(s:Screen:{user_label} {{name: "{screen}"}}) ' \
              f'RETURN event'

    query_2 = f'MATCH (a:Action:{user_label})-[{{name: "вызывать"}}]-(event:Event:{user_label}) ' \
              f'MATCH (a)-[{{name: "предполагать взаимодействие с"}}]->(i:Interface:{user_label})' \
              f'-[{{name: "являться частью"}}]->(s:Screen:{user_label} {{name: "{screen}"}}) ' \
              f'RETURN event'

    res_str = f"**{screen}**:\n"

    for q in [query_1, query_2]:
        res = conn.query(q)
        for r in res:
            res_str += f"- **{r['event']['name']}** – {r['event']['description']}\n"
    res_str += '\n'
    return res_str


def get_events(conn, user_label):
    screens = get_screens(conn, user_label)
    res_str = ""
    for screen in screens:
        res_str += get_events_for_screen(conn, user_label, screen)
    return res_str
