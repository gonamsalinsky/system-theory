import b2c_relations
import b2c_nodes
from b2c_nodes import BranchType


def test_relation_include_constants():  # TODO: Establish tests in best-practice way instead of this crutch
    cases = [
        # relation, source, target, branch_type, case_valid
        (relations.Include, nodes.Scenario, nodes.UserStep, BranchType.main, True),
        (relations.Include, nodes.Scenario, nodes.GoodsCard, BranchType.main, False)
    ]
    for rel, source, target, branch, expect in cases:
        res = True
        try:
            rel(source("Test"), target("test", branch))
        except RuntimeError:  # TODO: make custom Exception
            res = False
        print("case {} {} {} :: {}   {}".format(source, target, branch, expect, "OK" if res == expect else "FAIL"))
        assert res == expect


if __name__ == "__main__":
    test_relation_include_constants()

    print("All good!")
