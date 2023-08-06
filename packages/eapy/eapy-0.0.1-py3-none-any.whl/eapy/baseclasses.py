import abc
import numpy as np


class Member(abc.ABC):
    fitness: float

    # @abc.abstractmethod
    # def process(self, inputs: np.ndarray) -> np.ndarray:
    #     raise NotImplementedError

    def __lt__(self, other: "Member") -> bool:
        return self.fitness < other.fitness


class Problem(abc.ABC):
    @abc.abstractmethod
    def evaluate(self, member: Member) -> float:
        raise NotImplementedError

    # @property
    # @abc.abstractmethod
    # def Ni(self) -> int:
    #     raise NotImplementedError

    # @property
    # @abc.abstractmethod
    # def No(self) -> int:
    #     raise NotImplementedError


class Operator(abc.ABC):
    @abc.abstractmethod
    def new_member(self, problem: Problem) -> Member:
        raise NotImplementedError

    @abc.abstractmethod
    def reproduce(self, member: Member, problem: Problem) -> Member:
        raise NotImplementedError


class Selection(abc.ABC):
    @abc.abstractmethod
    def select(self, members: list[Member]) -> tuple[list[Member], list[Member]]:
        raise NotImplementedError


class Population(abc.ABC):
    @abc.abstractmethod
    def populate(
        self, population_size: int, operator: Operator, problem: Problem
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def advance(
        self, selection: Selection, operator: Operator, problem: Problem
    ) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def insert_migrants(self, members: list[Member]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_migrants(self, emigrants_requested: int) -> list[Member]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def populace(self) -> list[Member]:
        raise NotImplementedError
