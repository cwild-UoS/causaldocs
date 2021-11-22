from abc import ABC
from causal_testing.specification.constraint import Constraint, NormalDistribution
from typing import Union
import networkx as nx

Node = Union[str, int]  # Node type hint: A node is a string or an int


class CausalDAG(nx.DiGraph):
    """
    A causal DAG is a directed acyclic graph in which nodes represent random variables and edges represent causality
    between a pair of random variables. We implement a CausalDAG as a networkx DiGraph with an additional check that
    ensures it is acyclic. A CausalDAG must be specified as a dot file.
    """

    def __init__(self, dot_path: str = None, **attr):
        super().__init__(**attr)
        if dot_path:
            self.graph = nx.DiGraph(nx.drawing.nx_agraph.read_dot(dot_path))
        else:
            self.graph = nx.DiGraph()

        if not self.is_acyclic():
            raise nx.HasACycle("Invalid Causal DAG: contains a cycle.")

    def add_edge(self, u_of_edge: Node, v_of_edge: Node, **attr):
        """
        Add an edge to the causal DAG. Overrides the default networkx method to prevent users from adding a cycle.
        :param u_of_edge: From node
        :param v_of_edge: To node
        :param attr: Attributes
        """
        self.graph.add_edge(u_of_edge, v_of_edge, **attr)
        if not self.is_acyclic():
            raise nx.HasACycle("Invalid Causal DAG: contains a cycle.")

    def is_acyclic(self) -> bool:
        """
        Checks if the graph is acyclic.
        :return: True if acyclic, False otherwise.
        """
        return not list(nx.simple_cycles(self.graph))

    def get_minimal_adjustment_set(self, treatments: [str], outcomes: [str]) -> [str]:
        """
        Get the smallest possible set of variables that blocks all back-door paths between the all pairs of treatments
        and outcomes.
        :param treatments: A list of strings representing treatments.
        :param outcomes: A list of strings representing outcomes.
        :return: A list of strings representing the minimal adjustment set.
        """
        backdoor_graph = self.get_proper_backdoor_graph(treatments, outcomes)
        return backdoor_graph.minimal_d_separator(treatments, outcomes)

    def get_proper_backdoor_graph(self, treatments: [str], outcomes: [str]) -> 'CausalDAG':
        """
        Convert the causal DAG to a proper back-door graph. A proper back-door graph of a causal DAG is obtained by
        removing the first edge of every proper causal path from treatments to outcomes. A proper causal path from
        X to Y is a path of directed edges that starts from X and ends in Y.

        Reference: (Separators and adjustment sets in causal graphs: Complete criteria and an algorithmic framework,
        Zander et al.,  2019, Definition 3, p.15)

        :param treatments: A list of treatment variables.
        :param outcomes: A list of outcomes.
        :return: A CausalDAG corresponding to the proper back-door graph.
        """
        for var in treatments + outcomes:
            if var not in self.graph.nodes:
                raise IndexError(f'{var} not a node in Causal DAG.')

        proper_backdoor_graph = self.copy()
        nodes_on_proper_causal_path = self.proper_causal_pathway(proper_backdoor_graph, treatments, outcomes)
        edges_to_remove = [(u, v) for (u, v) in proper_backdoor_graph.graph.out_edges(treatments) if v in
                           nodes_on_proper_causal_path]
        proper_backdoor_graph.graph.remove_edges_from(edges_to_remove)
        return proper_backdoor_graph

    def minimal_d_separator(self, treatments: [str], outcomes: [str]) -> [str]:
        """
        Get the smallest set of variables which d-separates treatments from outcomes. In other words, a set of variables
        from which the removal of any subset of variables would no d-connect the treatments and outcomes (i.e. no longer
        block all back-door paths).

        :param treatments: A list of treatment variables.
        :param outcomes: A list of outcomes.
        :return: A list of variables representing the smallest set of variables that d-separates the treatments from the
        outcomes.
        """
        pass

    def __str__(self):
        return f'Nodes: {self.graph.nodes}\nEdges: {self.graph.edges}'

    @staticmethod
    def proper_causal_pathway(causal_graph, treatments: [str], outcomes: [str]) -> str:
        """
        Given a list of treatments and outcomes, compute the proper causal pathways between them.
        PCP(X, Y) = {DeX^(X) - X} intersect AnX_(Y)}, where:
        - DeX^(X) refers to the descendents of X in the graph obtained by deleting all edges into X.
        - AnX_(Y) refers to the ancestors of Y in the graph obtained by deleting all edges leaving X.
        :param causal_graph: The Causal DAG that contains the treatments and outcomes.
        :param treatments: A list of treatment variables in the causal DAG.
        :param outcomes: A list of outcomes in the causal DAG.
        :return vars_on_proper_causal_pathway: Return a list of the variables on the proper causal pathway between
        treatments and outcomes.
        """
        treatments_descendants = set.union(*[nx.descendants(causal_graph.graph, treatment) for treatment in treatments])
        treatments_descendants_without_treatments = set(treatments_descendants).difference(treatments)
        backdoor_graph = CausalDAG.get_backdoor_graph(causal_graph, set(treatments))
        outcome_ancestors = set.union(*[nx.ancestors(backdoor_graph, outcome) for outcome in outcomes])
        nodes_on_proper_causal_paths = treatments_descendants_without_treatments.intersection(outcome_ancestors)
        return nodes_on_proper_causal_paths

    @staticmethod
    def get_backdoor_graph(causal_graph, treatments):
        """
        A back-door graph is a graph for the list of treatments is a Causal DAG in which all edges leaving the treatment
        nodes are deleted.

        :param causal_graph: A causal DAG from which the back-door graph will be derived.
        :param treatments: The set of treatments whose outgoing edges will be deleted.
        :return: A back-door graph corresponding to the given causal DAG and set of treatments.
        """
        outgoing_edges = causal_graph.graph.out_edges(treatments)
        backdoor_graph = causal_graph.graph.copy()
        backdoor_graph.remove_edges_from(outgoing_edges)
        return backdoor_graph


class Scenario(dict):
    """
    Given a system with X distinct inputs, a scenario is a series of constraints placed over a subset of these
    inputs that characterises some use-case of the system-under-test.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

    def add_constraint(self, input_variable: str, constraint: Constraint):
        self[input_variable] = constraint

    def add_constraints(self, constraints_dict: dict):
        self.update(constraints_dict)


class CausalSpecification(ABC):

    def __init__(self, scenario: Scenario, causal_dag: CausalDAG):
        self.scenario = scenario
        self.causal_dag = causal_dag

    def __str__(self):
        return f'Scenario: {self.scenario}\nCausal DAG:\n{self.causal_dag}'


if __name__ == "__main__":
    scenario = Scenario({"Vaccine": "Pfizer"})
    age_constraint = NormalDistribution(40, 10)
    scenario.add_constraint("Age", age_constraint)

    causal_dag = CausalDAG()
    causal_dag.add_edge("Vaccine", "Cumulative Infections")
    causal_dag.add_edge("Age", "Vaccine")
    causal_dag.add_edge("Age", "Cumulative Infections")

    causal_specification = CausalSpecification(scenario, causal_dag)
    print(causal_specification)
