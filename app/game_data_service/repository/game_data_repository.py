from common.game_data.resources import Resources
from common.game_data.stats import Stats

class GameDataRepository:
    def __init__(self) -> None:
        pass
    
    def get_stats(self, player_id: int):
        pass

    def get_resources(self, player_id: int):
        pass

    def set_stats(self, player_id: int, stats: Stats):
        pass

    def set_resources(self, player_id: int, resources: Resources):
        pass

    def delete_stats(self, stats: Stats):
        pass