from wowspy import Region


class Clan:
    def __init__(self, region: Region, id_: str, logger):
        """

        :param region:
        :param id_:
        """
        self.region = region
        self.id_ = id_
        self.logger = logger
        self.player_ids = []