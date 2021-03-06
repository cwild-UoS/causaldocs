import unittest
import os
import pandas as pd
from causal_testing.generation.abstract_causal_test_case import AbstractCausalTestCase
from causal_testing.specification.causal_specification import Scenario
from causal_testing.specification.variable import Input, Output
from scipy.stats import uniform, rv_discrete
from tests.test_helpers import create_temp_dir_if_non_existent, remove_temp_dir_if_existent
from causal_testing.testing.causal_test_outcome import Positive


class TestAbstractTestCase(unittest.TestCase):
    """
        Class to test abstract test cases.
    """
    def setUp(self) -> None:
        temp_dir_path = create_temp_dir_if_non_existent()
        self.dag_dot_path = os.path.join(temp_dir_path, "dag.dot")
        self.observational_df_path = os.path.join(temp_dir_path, "observational_data.csv")
        # Y = 3*X1 + X2*X3 + 10
        self.observational_df = pd.DataFrame({"X1": [1, 2, 3, 4], "X2": [5, 6, 7, 8], "X3": [10, 20, 30, 40]})
        self.observational_df["Y"] = self.observational_df.apply(lambda row: (3 * row.X1) + (row.X2 * row.X3) + 10,
                                                                 axis=1)
        self.observational_df.to_csv(self.observational_df_path)
        self.X1 = Input("X1", int, uniform(1, 4))
        self.X2 = Input("X2", int, rv_discrete(values=([7], [1])))
        self.X3 = Input("X3", int, uniform(10, 40))
        self.X4 = Input("X4", int, rv_discrete(values=([10], [1])))
        self.Y = Output("Y", int)

    def test_generate_concrete_test_cases(self):
        scenario = Scenario({self.X1, self.X2, self.X3, self.X4})
        scenario.setup_treatment_variables()
        abstract = AbstractCausalTestCase(
            scenario=scenario,
            intervention_constraints={scenario.treatment_variables[self.X1.name].z3 > self.X1.z3},
            treatment_variables={self.X1},
            expected_causal_effect=Positive,
            outcome_variables={self.Y},
            effect_modifiers=None,
        )
        concrete_tests, runs = abstract.generate_concrete_tests(2)
        assert len(concrete_tests) == 2, "Expected 2 concrete tests"
        assert len(runs) == 2, "Expected 2 runs"

    def tearDown(self) -> None:
        remove_temp_dir_if_existent()


if __name__ == "__main__":
    unittest.main()
