from . import baseclasses as bc


class FlatPopulation(bc.Population):
    def populate(
        self, population_size: int, operator: bc.Operator, problem: bc.Problem
    ) -> None:
        self._populace = []
        for _ in range(population_size):
            new_member = operator.new_member(problem)
            new_member.fitness = problem.evaluate(new_member)
            self._populace.append(new_member)

    def advance(
        self, selection: bc.Selection, operator: bc.Operator, problem: bc.Problem
    ) -> int:
        members_to_reproduce, members_to_delete = selection.select(self._populace)

        for member in members_to_delete:
            self._populace.remove(member)

        for member in members_to_reproduce:
            new_member = operator.reproduce(member, problem)
            new_member.fitness = problem.evaluate(new_member)
            self._populace.append(new_member)

        return len(members_to_reproduce)

    def insert_migrants(self, members: list[bc.Member]) -> None:
        insert_index = len(self._populace) - len(members)
        self._populace[insert_index:] = members[:]

    def get_migrants(self, emigrants_requested: int) -> list[bc.Member]:
        self._populace.sort()
        return self._populace[:emigrants_requested]

    @property
    def populace(self) -> list[bc.Member]:
        return self._populace
