
from beartype import beartype
from picsellia.decorators import exception_handler
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao


class Worker(Dao):

    def __init__(self, connexion: Connexion, username: str):
        super().__init__(connexion)
        self.username = username

    @exception_handler
    @beartype
    def get_infos(self) -> dict:
        """Retrieve worker info

        Examples:
            ```python
                worker = project.list_workers()[0]
                print(worker.get_infos())
            ```

        Returns:
            A dict with data of the worker
        """
        return {"username": self.username}
