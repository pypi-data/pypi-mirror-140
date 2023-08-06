from beartype import beartype
from picsellia.decorators import exception_handler
from picsellia.sdk.connexion import Connexion
from picsellia.sdk.dao import Dao
from picsellia.sdk.run import Run


class Scan(Dao):

    def __init__(self, connexion: Connexion, project_token: str, id: str, name: str) -> None:
        super().__init__(connexion)
        self.project_token = project_token
        self.id = id
        self.name = name

    @exception_handler
    @beartype
    def launch(self,) -> None:
        """Distribute runs remotely for this scan.

        :info: The remote environment has to be setup prior launching the experiment.
        It defaults to our remote training engine.

        Examples:
            ```python
                scan.launch()
            ```
        """
        self.connexion.post('/scan/{}/launch'.format(self.id))

    @exception_handler
    @beartype
    def _convert_response_to_run(self, response: dict) -> Run:
        script = None
        script_object_name = None
        if "script" in response.keys():
            script = response["script"]
            script_object_name = response["script_object_name"]
        return Run(
            self.connexion,
            response["id"],
            response["config"],
            script,
            script_object_name,
            response["requirements"]
        )

    @exception_handler
    @beartype
    def get_run_by_id(self, id: str) -> Run:
        """Retrieve a run object by its id.

        Examples:
            ```python
                scan.get_run_by_id("cb750009-4e09-42bb-8c84-cc78aa004bf0")
            ```
        Arguments:
            id (str): id (primary key) of the run on Picsellia

        Returns:
            A (Run) object manipulable
        """
        r = self.connexion.get('/run/{}'.format(id)).json()
        run = self._convert_response_to_run(r["run"])
        return run

    @exception_handler
    @beartype
    def get_next_run(self,) -> Run:
        """Get next available Run for Scan.

        Examples:
            ```python
                scan.get_next_run()
            ```

        Returns:
            A (Run) object manipulable
        """
        r = self.connexion.get('/scan/{}/run/next'.format(self.id)).json()
        run = self._convert_response_to_run(r["run"])
        return run
