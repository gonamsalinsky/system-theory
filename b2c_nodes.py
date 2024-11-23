class NodeItem:
    labels = ['B2C']
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


class User(NodeItem):
    class_name = "Пользователь"
    class_description = "Класс пользователей (сегмент пользователей, поведение которых внутри сервиса " \
                        "может различаться, так как различаются потребности, которые они закрывают с помощью сервиса)"
    labels = NodeItem.labels + ['User']

    def __init__(self, name: str, user_label: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"


class Reason(NodeItem):
    class_name = "Причина"
    class_description = "класс причин использования сервиса, или состояний, в котором находится пользователь " \
                        "и которое побуждает его воспользоваться сервисом"
    labels = NodeItem.labels + ['Reason']

    def __init__(self, name: str, user_label: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"


class Step(NodeItem):
    class_name = "Шаг сценария"
    class_description = "Шаг сценария использования сервиса без привязки к конкретной реализации " \
                        "данного шага внутри сервиса"
    labels = NodeItem.labels + ['Step']

    def __init__(self, name: str, user_label: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"


class Action(NodeItem):
    class_name = "Действие"
    class_description = "Техническое действие (может быть действием пользователя или «реакцией» сервиса), " \
                        "в набор которых материализуется шаг сценария"
    labels = NodeItem.labels + ['Action']


class View(Action):
    class_name = "Просмотр"
    class_description = "Просмотр или появление в поле видимости какого-либо интерфейсного элемента"
    labels = Action.labels + ['View']

    def __init__(self, name: str, user_label: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"


class Click(Action):
    class_name = "Нажатие"
    class_description = "Нажатие (например, на кнопку или баннер)"
    labels = Action.labels + ['Click']

    def __init__(self, name: str, user_label: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"


class Scroll(Action):
    class_name = "Прокрутка"
    class_description = "Прокрутка (например, экрана или слайдера)"
    labels = Action.labels + ['Scroll']

    def __init__(self, name: str, user_label: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"


class Type(Action):
    class_name = "Набор текста"
    class_description = "Набор текста"
    labels = Action.labels + ['Type']

    def __init__(self, name: str, user_label: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"


class Interface(NodeItem):
    class_name = "Элемент интерфейса"
    class_description = "Элемент пользовательского интерфейса, с которым пользователь осуществляет взаимодействие"
    labels = NodeItem.labels + ['Interface']


class Button(Interface):
    class_name = "Кнопка"
    class_description = "Кнопка"
    labels = Interface.labels + ['Button']

    def __init__(self, name: str, user_label: str, codename: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.codename = codename
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}', codename: '{self.codename}'}}"


class Screen(Interface):
    class_name = "Экран"
    class_description = "Экран"
    labels = Interface.labels + ['Screen']

    def __init__(self, name: str, user_label: str, codename: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.codename = codename
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}', codename: '{self.codename}'}}"


class Banner(Interface):
    class_name = "Баннер"
    class_description = "Баннер"
    labels = Interface.labels + ['Banner']

    def __init__(self, name: str, user_label: str, codename: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.codename = codename
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}', codename: '{self.codename}'}}"


class Block(Interface):
    class_name = "Блок"
    class_description = "Блок"
    labels = Interface.labels + ['Block']

    def __init__(self, name: str, user_label: str, codename: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.codename = codename
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}', codename: '{self.codename}'}}"


class Event(NodeItem):
    class_name = "Событие"
    class_description = "Событие (лог), которое вызывается в момент совершения действия для каждого уникального " \
                        "пользователя и в соответствии с которыми впоследствии можно осуществлять анализ поведения " \
                        "пользователя"
    labels = NodeItem.labels + ['Event']

    def __init__(self, name: str, user_label: str):
        self.name = name
        self.labels = self.labels + [user_label]
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"
