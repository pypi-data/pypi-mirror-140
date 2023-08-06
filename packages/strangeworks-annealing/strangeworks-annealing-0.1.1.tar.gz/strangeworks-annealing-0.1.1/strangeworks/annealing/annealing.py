import numpy as np
from .problem import Problem
import strangeworks
from strangeworks.backend.backends import Backend, BackendService
from strangeworks.jobs.jobs import Job
from strangeworks.errors.error import StrangeworksError
from typing import Union, List
import uuid


# TODO: replace this w/ the backend's base url
__base_url = "/plugins/aws"


def get_backends(
    selected_backend: Union[str, Backend] = None, pprint: bool = True
) -> List[Backend]:
    return strangeworks.backends_service.get_backends(
        selected_backend, pprint, filters=lambda b: b.backend_type() == "annealing"
    )


def select_backend(selected_backend: Union[str, Backend] = None) -> Backend:
    return strangeworks.backends_service.select_backend(selected_backend)


def get_coupling_map_from_backend(backend: Backend) -> dict:
    return strangeworks.client.rest_client.get(
        f"{__base_url}/backend/{backend.name()}/coupling"
    )


def upload_problem(file_path: str = "") -> Problem:
    lin = {}
    quad = {}
    with open(file_path) as f:
        lines = f.readlines()
        for l in lines:
            ar = np.fromstring(l, dtype=int, sep=" ")
            if ar[0] == ar[1]:
                lin[int(ar[0])] = int(ar[2])
            else:
                quad[(int(ar[0]), int(ar[1]))] = int(ar[2])
    return Problem(linear=lin, quadratic=quad)


def run(
    problem: Problem,
    backend: Union[str, Backend],
    shots: int = 1,
    result_id: str = None,
) -> Job:
    """Low level annealing executor. Assumes user has already embedded problem to device target"""

    if isinstance(backend, str):
        backend = select_backend(backend)

    # create a new result for each job unless the user specifies a result in the client
    rid = str(uuid.uuid4()) if result_id is None else result_id

    # check if backend can run annealing problems
    if backend.backend_type() != "annealing":
        raise StrangeworksError.invalid_argument(
            f"{backend.name()} is not a supported backend for annealing service"
        )

    # check if problem is embedded, if not embed problem
    if problem.target_linear is None or problem.target_quadratic is None:
        coupling_map = get_coupling_map_from_backend(backend)
        problem.embed_problem(coupling_map)

    payload = {
        "target": backend.name(),
        "result_id": rid,
        "shots": shots,
    }
    payload.update(problem.to_dict())

    # post to the correct plugin and return a job
    response = strangeworks.client.rest_client.post(
        url=f"{__base_url}/run-annealing-job",
        json=payload,
        expected_response=200,
    )

    return Job.from_json(
        job=response,
        backend=backend,
        rest_client=strangeworks.client.rest_client,
    )
