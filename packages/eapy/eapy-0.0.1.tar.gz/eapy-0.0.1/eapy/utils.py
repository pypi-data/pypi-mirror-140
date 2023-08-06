import os
import sys
import time
import random
import shutil
import pprint
import logging
import traceback
from pathlib import Path
import numpy as np


_PROCESS_RNG: np.random.Generator


def setup_rng(seed: int) -> None:
    global _PROCESS_RNG
    _PROCESS_RNG = np.random.default_rng(seed)
    random.seed(int.from_bytes(_PROCESS_RNG.bytes(4), "big"))


def get_rng() -> np.random.Generator:
    global _PROCESS_RNG
    return _PROCESS_RNG


class Progress:
    def update(self, progress: float) -> None:
        percent_str = f" {progress*100:5.1f}%"

        if progress == 0:
            eta_str = " eta: --:--:--"
        else:
            eta = (time.perf_counter() - self._start_time) * (1 - progress) / progress
            if eta < 24 * 60 * 60:
                eta_str = time.strftime(" eta: %H:%M:%S", time.gmtime(eta))
            else:
                eta_str = " eta:>24:00:00"

        bar_width = self._terminal_width - len(percent_str) - len(eta_str)
        whole_width = int(progress * (bar_width - 2))
        part_idx = int((progress * (bar_width - 2) - whole_width) * 8)
        part_str = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉"][part_idx]
        empty_width = bar_width - whole_width - len(part_str) - 2
        bar_str = "▕" + "█" * whole_width + part_str + " " * empty_width + "▏"

        sys.stdout.write(bar_str + percent_str + eta_str + "\r")
        sys.stdout.flush()

    def __enter__(self) -> "Progress":
        self._terminal_width = shutil.get_terminal_size((80, 24)).columns
        self._start_time = time.perf_counter()
        return self

    def __exit__(self, *exc_args) -> None:
        self.update(1)
        sys.stdout.write("\n")
        sys.stdout.flush()


LOG_FMT = logging.Formatter(
    fmt="%(asctime)s %(levelname)-8s: %(message)s", datefmt="%H:%M:%S"
)


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("eapy")
    logger.handlers = []
    logger.setLevel(logging.DEBUG)

    terminal_handler = logging.StreamHandler(sys.stdout)
    terminal_handler.setFormatter(LOG_FMT)
    terminal_handler.setLevel(logging.DEBUG)
    logger.addHandler(terminal_handler)
    return logger


def set_log_path(log_path: Path) -> None:
    logger = logging.getLogger("eapy")

    file_handler = logging.FileHandler(Path(log_path) / f"{logger.name}.log", mode="a")
    file_handler.setFormatter(LOG_FMT)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)


def log_config(kwargs: dict, log_path: Path = None) -> None:
    class repr_wrapper:
        def __init__(self, cls) -> None:
            self._cls = cls

        def __repr__(self) -> str:
            return f"{self._cls.__module__}.{self._cls.__name__}"

    if log_path is not None:
        kwargs["log_path"] = str(kwargs["log_path"])

        with open(log_path / "config.py", "w") as fp:
            fp.write(f"import sys\n")

            path_set = set()
            for component in "population", "selection", "operator", "problem":
                cls = kwargs[component]["type"]
                fp.write(f"import {cls.__module__}\n")
                cls_path = os.path.abspath(sys.modules[cls.__module__].__file__)
                path_set.add(Path(cls_path).parent)
                kwargs[component] = {
                    "type": repr_wrapper(cls),
                    "args": kwargs[component]["args"],
                }

            for path in path_set:
                fp.write(f"\nsys.path.append('{path}')\n")
            fp.write(f"\nCONFIG =")
            pprint.pprint(kwargs, stream=fp)


def catch_exceptions(original_function):
    def new_function(*args, **kwargs):
        try:
            return original_function(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            raise e

    return new_function
