import importlib.metadata

__version__ = importlib.metadata.version("strangeworks-annealing")

from .annealing import (
    get_backends,
    select_backend,
    get_coupling_map_from_backend,
    upload_problem,
    run,
)
