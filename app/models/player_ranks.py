from typing import List


class PlayerRanks:
    ranks: List[str]

    def __init__(self):
      self.ranks = self.get_ranks()

    @staticmethod
    def get_ranks() -> List[str]:
       return ["Сержант", "Полковник"]