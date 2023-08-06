from typing import Dict, List
from strangeworks.backend.backends import Backend
import networkx as nx
from minorminer import find_embedding
from dwave_embedding_utilities import embed_ising, unembed_samples
from strangeworks.jobs.jobs import Job


class Problem:
    """
    QUBO Problem
    """

    def __init__(
        self,
        linear: dict,
        quadratic: dict,
        problem_type: str = "QUBO",
        target_linear: dict = None,
        target_quadratic: dict = None,
        chain_quadratic: dict = None,
        embedding: dict = None,
        samples: List[Dict] = None,
    ):
        self.linear = linear
        self.quadratic = quadratic
        self.chain_quadratic = chain_quadratic
        self.embedding = embedding
        self.problem_type = problem_type
        self.target_linear = target_linear
        self.target_quadratic = target_quadratic
        self.samples = samples

    def to_dict(self) -> dict:
        payload = {
            "problem_type": self.problem_type,
        }
        nq = {}
        for v in self.target_quadratic:
            k = ",".join(map(str, v))
            nq[k] = self.target_quadratic[v]
        qb = {}
        qb["quadratic"] = nq
        qb["linear"] = self.target_linear
        payload["qubo"] = qb
        return payload

    def embed_problem(self, coupler: dict):
        # set up problem
        problem_graph = nx.Graph()
        problem_graph.add_nodes_from(self.linear.keys())
        problem_graph.add_edges_from(self.quadratic.keys())

        # fetch coupling from backend
        coupler_graph = nx.Graph()
        coupler_graph.add_nodes_from(coupler["qubits"])
        coupler_graph.add_edges_from(coupler["couplers"])

        self.embedding = find_embedding(problem_graph, coupler_graph)
        self.target_linear, self.target_quadratic, self.chain_quadratic = embed_ising(
            self.linear, self.quadratic, self.embedding, coupler_graph
        )

    def unembed_result(self, job: Job) -> List[Dict]:
        output = job.results()
        nodes = output["additionalMetadata"]["action"]["linear"]
        solutions = output["solutions"]
        sample_dictionary = {}
        for k, v in zip(nodes.keys(), solutions[0]):
            sample_dictionary[int(k)] = v
        self.samples = unembed_samples([sample_dictionary], self.embedding)
        return self.samples
