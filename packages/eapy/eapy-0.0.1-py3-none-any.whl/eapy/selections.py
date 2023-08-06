import random
from . import baseclasses as bc


class TournamentSelection(bc.Selection):
    def __init__(self, n: int = 1, k: int = 2) -> None:
        self._n = n  # exchange_size
        self._k = k  # tournament size

    def select(
        self, members: list[bc.Member]
    ) -> tuple[list[bc.Member], list[bc.Member]]:
        members_to_reproduce = []
        members_to_delete = []
        for _ in range(self._n):
            competitors = random.sample(members, k=self._k)
            competitors.sort()
            members_to_reproduce.append(competitors[0])
            members_to_delete.append(competitors[-1])

        return members_to_reproduce, members_to_delete
