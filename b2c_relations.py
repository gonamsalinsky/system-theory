from b2c_nodes import *


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


class HaveState(RelationItem):
    rel_name = "иметь состояние"
    constraints = [("User", "Reason")]


class BeReason(RelationItem):
    rel_name = "быть причиной"
    constraints = [("Reason", "Step")]


class Preceede(RelationItem):
    rel_name = "предшествовать"
    constraints = [("Step", "Step"), ("Action", "Action")]


class Materialize(RelationItem):
    rel_name = "материализоваться в"
    constraints = [("Step", "Action")]


class BeTarget(RelationItem):
    rel_name = "быть целевым действием для"
    constraints = [("Step", "Reason")]


class Interact(RelationItem):
    rel_name = "предполагать взаимодействие с"
    constraints = [("Action", "Interface")]


class BePart(RelationItem):
    rel_name = "являться частью"
    constraints = [("Interface", "Interface")]


class Trigger(RelationItem):
    rel_name = "вызывать"
    constraints = [("Action", "Event")]


class SubClassOf(RelationItem):
    rel_name = "быть подклассом"
    constraints = [("User", "User")]
