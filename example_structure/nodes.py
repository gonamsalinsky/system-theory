class NodeItem:
    labels = []
    subquery = None

    def db_create_node(self, connection):
        connection.query(f"CREATE ({self.subquery})")

    def db_merge_node(self, connection):
        connection.query(f"MERGE ({self.subquery})")

    def get_node_id(self, connection):
        result = connection.query(f"MATCH (n{self.subquery}) RETURN ID(n) AS node_id")
        return result[0]['node_id']


class BehaviorItem(NodeItem):
    """Группа узлов, с помощью которых составляется формализованное описание поведенческой части (сценариев)"""
    labels = NodeItem.labels + ['Behavior']


class Scenario(BehaviorItem):
    class_name = "Сценарий"
    class_description = "Последовательностей действий пользователя и приложения " \
                        "в рамках одного функционального блока"
    labels = BehaviorItem.labels + ['Scenario']

    def __init__(self, name: str):
        self.name = name
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}'}}"


class BranchType:
    main = "Основная"
    alternative = "Альтернативная"
    negative = "Негативная"


class ScenarioStep(BehaviorItem):
    class_name = "Шаг сценария"
    class_description = "Атомарное действие пользователя или мобильного приложения"
    labels = BehaviorItem.labels + ['ScenarioStep']

    def __init__(self, name: str, branch_type: BranchType):
        self.name = name
        self.branch_type = branch_type
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}', branch_type: '{self.branch_type}'}}"


class UserStep(ScenarioStep):
    class_name = "Действие пользователя"
    class_description = "Атомарное действие пользователя"
    labels = ScenarioStep.labels + ['UserStep']


class AppStep(ScenarioStep):
    class_name = "Действие мобильного приложения"
    class_description = "Действие мобильного приложения"
    labels = ScenarioStep.labels + ['AppStep']


class InterfaceItem(NodeItem):
    """Группа узлов, с помощью которых составляется формализованное описание интерфейса"""
    labels = NodeItem.labels + ['Interface']

    def __init__(self, name: str, event_name: str):
        self.name = name
        self.event_name = event_name
        self.subquery = f":{':'.join(self.labels)} {{name: '{self.name}', event_name: '{self.event_name}'}}"


class Screen(InterfaceItem):
    class_name = "Экран"
    labels = InterfaceItem.labels + ['Screen']


class Block(InterfaceItem):
    class_name = "Блок элементов"
    labels = InterfaceItem.labels + ['Block']


class Element(InterfaceItem):
    class_name = "Элемент экрана"
    labels = InterfaceItem.labels + ['Element']


class Button(Element):
    class_name = "Кнопка"
    labels = Element.labels + ['Button']
    event_params = ['button_text']


class GoodsCard(Element):
    class_name = "Карточка товара"
    labels = Element.labels + ['GoodsCard']
    event_params = ['goods_name', 'goods_price']


class Banner(Element):
    class_name = "Баннер"
    labels = Element.labels + ['Banner']
    event_params = ['banner_text', 'banner_url']
