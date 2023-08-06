import os
import asyncio
from pathlib import Path
from collections import deque
import ray
import numpy as np

from . import baseclasses as bc
from . import utils
from .populations import FlatPopulation
from .selections import TournamentSelection

logger = utils.setup_logger()


class Deme:
    def initialise(
        self,
        seed: int,
        population_size: int,
        population: dict,
        selection: dict,
        problem: dict,
        operator: dict,
    ) -> None:
        # (for docstrings) initialise must be used instead of __init__, due to
        # the latter not returning a waitable objectref
        utils.setup_rng(seed)

        self._population: bc.Population = population["type"](**population["args"])
        self._selection: bc.Selection = selection["type"](**selection["args"])
        self._problem: bc.Problem = problem["type"](**problem["args"])
        self._operator: bc.Operator = operator["type"](**operator["args"])

        self._population.populate(population_size, self._operator, self._problem)

    def process(
        self,
        variations_to_complete: int,
        immigrants: list[bc.Member],
        emigrants_requested: int,
    ) -> tuple[int, list[bc.Member], list[float]]:
        self._population.insert_migrants(immigrants)

        variations_completed = 0
        while variations_completed < variations_to_complete:
            variations_completed += self._population.advance(
                self._selection, self._operator, self._problem
            )

        emigrants = self._population.get_migrants(emigrants_requested)
        fitness_list = [member.fitness for member in self._population.populace]
        return (variations_completed, emigrants, fitness_list)

    def get_populace(self) -> list[bc.Member]:
        return self._population.populace


@ray.remote
class RayDeme(Deme):
    pass


class RayManager:
    def __init__(self, variations: int, variations_per_migration: int) -> None:
        self._variations_remaining = variations
        self._variations_completed = 0
        self._variations_per_migration = variations_per_migration

    async def run(
        self,
        raydemes: list[RayDeme],
        migrant_buffers: list[deque[bc.Member]],
        sync: bool = False,
    ) -> None:
        progress_task = asyncio.create_task(self._report_progress())

        make_task = lambda i: asyncio.create_task(
            self.manage(raydemes[i], migrant_buffers[i - 1], migrant_buffers[i]),
            name=str(i),
        )

        return_when = asyncio.ALL_COMPLETED if sync else asyncio.FIRST_COMPLETED

        self._fitness_logs = {raydeme: {} for raydeme in raydemes}

        done, pending = {}, {make_task(i) for i in range(len(raydemes))}
        while self._variations_remaining > 0:
            pending |= {make_task(int(task.get_name())) for task in done}
            done, pending = await asyncio.wait(pending, return_when=return_when)
        if pending:
            await asyncio.wait(pending, return_when=asyncio.ALL_COMPLETED)

        progress_task.cancel()

    async def manage(
        self,
        raydeme: RayDeme,
        immigrant_buffer: deque[bc.Member],
        emigrant_buffer: deque[bc.Member],
    ) -> None:
        variations_to_complete = min(
            self._variations_remaining, self._variations_per_migration
        )
        self._variations_remaining -= variations_to_complete

        immigrants = list(immigrant_buffer)
        immigrant_buffer.clear()
        variations_completed, emigrants, fitness_list = await raydeme.process.remote(
            variations_to_complete, immigrants, emigrant_buffer.maxlen
        )
        emigrant_buffer.extend(emigrants)

        self._variations_remaining += variations_to_complete - variations_completed
        self._variations_completed += variations_completed

        self._fitness_logs[raydeme][self._variations_remaining] = fitness_list

    async def _report_progress(self) -> None:
        total_variations = self._variations_remaining

        with utils.Progress() as progress:
            while True:
                progress.update(self._variations_completed / total_variations)
                await asyncio.sleep(1)

    def log_fitness(self, log_path: Path = None) -> None:
        if log_path is not None:
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(1, 1, figsize=(8, 8))

            for fitness_log in self._fitness_logs.values():
                x = self._variations_completed - np.array(list(fitness_log.keys()))

                fitness_array = np.array(list(fitness_log.values()))
                fitness_array.sort(axis=1)
                y = fitness_array[:, 0]
                ax.plot(x, y)

            ax.set_ylabel("Fitness")
            ax.set_xlabel("Variations")
            ax.set_title("Fitness vs Variations")

            fig.savefig(log_path / "fitness.png")


def ea(
    generations: int,
    population_size: int,
    problem: dict,
    operator: dict,
    population: dict = {"type": FlatPopulation, "args": {}},
    selection: dict = {"type": TournamentSelection, "args": {"n": 1, "k": 2}},
    deme_count: int = None,
    migration_size: int = None,
    migration_period: int = None,
    sync: bool = True,
    seed: int = int.from_bytes(os.urandom(4), "big"),
    log_path: Path = None,
    local_mode: bool = False,
) -> None:
    ### Input Validation ###
    if type(log_path) is str:  # Update typehint in python 3.10
        log_path = Path(log_path)
    if log_path is not None and not isinstance(log_path, Path):
        raise TypeError("log_path must be of type str or Path")
    elif log_path is not None and not os.path.exists(log_path):
        raise FileNotFoundError(f"No such file or directory: '{log_path}'")
    elif log_path is not None:
        utils.set_log_path(log_path)

    if type(generations) is not int:
        raise TypeError("generations must be of type int")
    elif generations < 1:
        raise ValueError("generations must be >= 1")

    cpu_count = os.cpu_count()
    if deme_count is None:
        deme_count = cpu_count
    elif type(deme_count) is not int:
        raise TypeError("deme_count must be of type int")
    elif deme_count < 1:
        raise ValueError("deme_count must be >= 1")
    elif deme_count > cpu_count:
        logger.warning(f"deme_count ({deme_count}) exceeds CPU count ({cpu_count})")

    if type(population_size) is not int:
        raise TypeError("population_size must be of type int")
    elif population_size < deme_count:
        raise ValueError("population_size must be >= deme_count")

    components = {
        "population": population,
        "selection": selection,
        "problem": problem,
        "operator": operator,
    }
    for name, comp in components.items():
        if not isinstance(comp, dict):
            raise TypeError(f"{name} must be a dict")
        elif "type" not in comp:
            raise ValueError(f"{name} must = {{'type': <type>, 'args': <kwargs>}}")
        elif "args" not in comp:
            comp["args"] = {}
        elif not isinstance(comp["args"], dict):
            raise TypeError(f"{name}['args'] must be a kwargs dict")
    if not issubclass(population["type"], bc.Population):
        raise TypeError(f"population['type'] must subclass eapy.baseclasses.Population")
    if not issubclass(selection["type"], bc.Selection):
        raise TypeError(f"selection['type'] must subclass eapy.baseclasses.Selection")
    if not issubclass(problem["type"], bc.Problem):
        raise TypeError(f"problem['type'] must subclass eapy.baseclasses.Problem")
    if not issubclass(operator["type"], bc.Operator):
        raise TypeError(f"operator['type'] must subclass eapy.baseclasses.Operator")

    if migration_size is None:
        migration_size = int(population_size / deme_count * 0.1)
    elif type(migration_size) is not int:
        raise TypeError("migration_size must be of type int")
    elif migration_size < 0 or migration_size > population_size // deme_count:
        raise ValueError("migration_size must be in [0, population_size/deme_count]")

    if migration_period is None:
        migration_period = int(np.ceil(generations / deme_count * 0.1))
    elif type(migration_period) is not int:
        raise TypeError("migration_period must be of type int")
    elif migration_period < 1 or migration_period > generations:
        raise ValueError("migration_period must be in [1, generations]")

    if type(sync) is not bool:
        raise TypeError("sync must be True or False")

    if type(seed) is not int:
        raise TypeError("seed must be of type int")

    if type(local_mode) is not bool:
        raise TypeError("local_mode must be of type bool")

    ### Initialisation ###
    logger.info("Initialising.")

    kwargs = {
        "generations": generations,
        "population_size": population_size,
        "deme_count": deme_count,
        "migration_size": migration_size,
        "migration_period": migration_period,
        "log_path": log_path,
        "seed": seed,
        "sync": sync,
        **components,
    }
    utils.log_config(kwargs, log_path)

    rng = np.random.default_rng(seed)
    deme_seeds = [int.from_bytes(rng.bytes(4), "big") for _ in range(deme_count)]

    quotient, remainder = divmod(population_size, deme_count)
    deme_sizes = [quotient] * deme_count
    deme_sizes[:remainder] = [q + 1 for q in deme_sizes[:remainder]]

    if not ray.is_initialized():
        ray.init(local_mode=local_mode)

    raydemes = [RayDeme.remote() for _ in range(deme_count)]
    init_objectrefs = [
        raydeme.initialise.remote(
            seed=seed,
            population_size=deme_size,
            **components,
        )
        for raydeme, deme_size, seed in zip(raydemes, deme_sizes, deme_seeds)
    ]
    ray.wait(init_objectrefs, num_returns=deme_count)

    variations = generations * population_size
    variations_per_migration = migration_period * population_size // deme_count
    manager = RayManager(variations, variations_per_migration)

    migrant_buffers = [deque(maxlen=migration_size) for _ in range(len(raydemes))]

    ### Processing ###
    logger.info("Processing.")
    asyncio.run(manager.run(raydemes, migrant_buffers, sync=sync))

    ### Results ###
    manager.log_fitness(log_path)

    deme_populaces = ray.get([raydeme.get_populace.remote() for raydeme in raydemes])
    best_member = min([min(populace) for populace in deme_populaces])
    logger.info(f"Done. Best fitness: {best_member.fitness}")
    return best_member
