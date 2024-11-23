from robot_nodes import *


class RelationItem:
    rel_name = None
    constraints = []

    def __init__(self, source: NodeItem, target: NodeItem):
        self.source = source
        self.target = target
        self.validate()

    @property
    def relation_type(self):
        for src, trg in self.constraints:
            if src in self.source.labels and trg in self.target.labels:
                return 1
        return None

    def validate(self):
        if self.relation_type is None:
            raise RuntimeError("You can not use {}-{} source-target combination in a relation of type {}".format(
                type(self.source).__name__, type(self.target).__name__, type(self).__name__))

    def db_create_relation(self, connection):
        source_id = self.source.get_node_id(connection)
        target_id = self.target.get_node_id(connection)
        query = f"MATCH (source), (target) " \
                f"WHERE ID(source) = {source_id} AND ID(target) = {target_id} " \
                f"MERGE (source)-[:SEMANTIC {{name: '{self.rel_name}'}}]->(target)"
        connection.query(query)

    def db_delete_relation(self, connection):
        source_id = self.source.get_node_id(connection)
        target_id = self.target.get_node_id(connection)
        query = f"MATCH (source)-[r:SEMANTIC {{name: '{self.rel_name}'}}]->(target) " \
                f"WHERE ID(source) = {source_id} AND ID(target) = {target_id} " \
                f"DELETE r"
        connection.query(query)


class TransitTo(RelationItem):
    rel_name = "переходить в"
    constraints = [("State", "State")]


class TransitionFrom(RelationItem):
    rel_name = "быть переходом из"
    constraints = [("Transition", "State")]


class TransitionTo(RelationItem):
    rel_name = "быть переходом в"
    constraints = [("Transition", "State")]


class BePredicate(RelationItem):
    rel_name = "быть условием перехода"
    constraints = [("Predicate", "Transition")]


# class Preceede(RelationItem):
#     rel_name = "предшествовать"
#     constraints = [("Action", "Transition")]


class Call(RelationItem):
    rel_name = "вызывать"
    constraints = [("Transition", "Action")]
