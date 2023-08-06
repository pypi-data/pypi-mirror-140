from beartype import beartype
from picsellia import exceptions
from picsellia.decorators import exception_handler
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao


class Organization(Dao):

    def __init__(self, connexion: Connexion, id: str, name: str):
        super().__init__(connexion)
        self.id = id
        self.name = name

    @exception_handler
    @beartype
    def get_resource_url_on_platform(self,) -> str:
        """Get platform url of this resource.

        Examples:
            ```python
                print(foo_dataset.get_resource_url_on_platform())
                >>> https://app.picsellia.com/organization/62cffb84-b92c-450c-bc37-8c4dd4d0f590
            ```

        Returns:
            Url on Platform for this resource
        """
        if self.connexion.base_url is None:
            raise exceptions.PicselliaError('Could not parse platform url. You cannot get platform link')

        return "{}/organization/{}".format(self.connexion.base_url, self.id)

    @exception_handler
    @beartype
    def get_infos(self) -> dict:
        """Return some information about this organization

        Examples:
            ```python
                org = client.get_organization()
                print(org.get_infos())
            ```

        Returns:
            A dict with id and name of the organization
        """
        return {"id": self.id, "name": self.name}
