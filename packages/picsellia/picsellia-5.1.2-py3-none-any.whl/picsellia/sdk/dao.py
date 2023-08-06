from picsellia.sdk.connexion import Connexion


class Dao:

    def __init__(self, connexion: Connexion) -> None:
        self.connexion = connexion
