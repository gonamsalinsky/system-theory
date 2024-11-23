class Rule:
    def __int__(self, if_clause: str, then_clause: str):
        self.if_clause = if_clause
        self.then_clause = then_clause

RULES = []

# если шаг сценария 1 предшествует шагу сценария 2, а сценарий Х включает в себя шаг сценария 1,
# то сценарий Х включает в себя также и шаг 2
STEPS_RULE = "MATCH(step1:ScenarioStep)-[{name: 'предшествовать'}]->(step2:ScenarioStep), " \
             "(sc:Scenario)-[r {name: 'включать в себя'}]->(step1) " \
             "MERGE(sc)-[:GENERATED {name: 'включать в себя'}]->(step2)"
RULES.append(STEPS_RULE)

# если шаг сценария осуществляется на экране Х и предполагает взаимодействие с Y,
# то Y располагается на экране Х
LOCATION_RULE = "MATCH(step:ScenarioStep)-[{name: 'осуществляться на'}]->(screen:Screen), " \
                "(step)-[{name: 'предполагать взаимодействие с'}]->(el) " \
                "MERGE(el)-[:GENERATED {name: 'располагаться на'}]->(screen)"
RULES.append(LOCATION_RULE)

# если шаг сценария A относится к экрану В, то необходимо создать событие типа view (свойство action),
# которое будет связано с шагом сценария А отношением "вызывать" и с экраном В – отношением "относиться к";
# название события (свойство name) генерируется на основе свойства event_name экрана и типа события;
# описание события (свойтсво description) генерируется на основе названия экрана
SCREEN_VIEW_RULE = "MATCH (step:ScenarioStep)-[r {name: 'осуществляться на'}]->(screen:Screen) " \
                   "MERGE (event:Event {action: 'view', description: 'Просмотр экрана «' + screen.name + '»'}) " \
                   "ON CREATE SET event.name = screen.event_name + '_' + event.action " \
                   "MERGE (step)-[:GENERATED {name: 'вызывать'}]->(event) " \
                   "MERGE (event)-[:GENERATED {name: 'относиться к'}]->(screen)"
RULES.append(SCREEN_VIEW_RULE)


def trigger_rules(client):
    for rule in RULES:
        client.query(rule)
