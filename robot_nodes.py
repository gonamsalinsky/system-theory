class NodeItem:
    labels = ['Robot']
    subquery = None

    def db_create_node(self, connection):
        connection.query(f"CREATE ({self.subquery})")

    def db_merge_node(self, connection):
        connection.query(f"MERGE ({self.subquery})")

    def get_node_id(self, connection):
        result = connection.query(f"MATCH (n{self.subquery}) RETURN ID(n) AS node_id")
        return result[0]['node_id']

    def db_delete_node(self, connection):
        connection.query(f"MERGE (n{self.subquery}) DETACH DELETE n")


class State(NodeItem):
    class_name = "Состояние"
    class_description = "Класс состояний системы"
    labels = NodeItem.labels + ['State']

    def __init__(self, name: str, user_label: str, codename: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.codename = codename
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}', codename: '{self.codename}'}}"


class Predicate(NodeItem):
    class_name = "Условие перехода"
    class_description = "Условие перехода из одного состояния системы в другое"
    labels = NodeItem.labels + ['Predicate']

    def __init__(self, name: str, user_label: str, codename: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.codename = codename
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}', codename: '{self.codename}'}}"


class Action(NodeItem):
    class_name = "Действие"
    class_description = "Действие системы"
    labels = NodeItem.labels + ['Action']

    def __init__(self, name: str, user_label: str, codename: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.codename = codename
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}', codename: '{self.codename}'}}"


class Transition(NodeItem):
    class_name = "Переход"
    class_description = "Класс переходов из одного состояния системы в другое"
    labels = NodeItem.labels + ['Transition']

    def __init__(self, name: str, user_label: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"


