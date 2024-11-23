from nodes import *
from rules import trigger_rules

# Relation types
REQUIRED = 'REQUIRED'
OPTIONAL = 'OPTIONAL'
GENERATED = 'GENERATED'


class RelationItem:
    rel_name = None
    constraints = []

    def __init__(self, source: NodeItem, target: NodeItem):
        self.source = source
        self.target = target
        self.validate()

    @property
    def relation_type(self):
        for src, trg, rel_type in self.constraints:
            if src in self.source.labels and trg in self.target.labels:
                return rel_type
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
                f"MERGE (source)-[:{self.relation_type} {{name: '{self.rel_name}'}}]->(target)"
        connection.query(query)
        trigger_rules(connection)


class Preceede(RelationItem):
    rel_name = "предшествовать"
    constraints = [("ScenarioStep", "ScenarioStep", OPTIONAL)]


class Include(RelationItem):
    rel_name = "включать в себя"
    constraints = [("Scenario", "ScenarioStep", REQUIRED), ("Block", "Element", REQUIRED)]


class BePartOf(RelationItem):
    rel_name = "быть частью"
    constraints = [("Element", "Block", OPTIONAL)]


class BePerformedOn(RelationItem):
    rel_name = "осуществляться на"
    constraints = [("ScenarioStep", "Screen", REQUIRED)]


class InteractWith(RelationItem):
    rel_name = "предполагать взаимодействие с"
    constraints = [("ScenarioStep", "Element", OPTIONAL), ("ScenarioStep", "Block", OPTIONAL)]
