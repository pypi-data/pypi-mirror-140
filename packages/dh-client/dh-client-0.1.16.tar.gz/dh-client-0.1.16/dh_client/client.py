import os

from datahub.emitter.rest_emitter import DatahubRestEmitter


class RestClient(DatahubRestEmitter):
    def __init__(
        self,
        env: str = "DEV",
        datahub_actor: str = "urn:li:corpuser:admin",
        dataset_platform: str = "bigquery",
        dashboard_platform: str = "bigquery",
        *args,
        **kwargs,
    ):
        """
        The main entrypoint to use this High level client.


        Args:
            env: Environment name.
            datahub_actor: Datahub actor.
            dataset_platform: Datahub platform.
            dashboard_platform: Dashboard platform.
            args: Extra positional arguments for `DatahubRestEmitter`.
            kwargs: Extra keyword arguments for `DatahubRestEmitter`.

        Examples:

            >>> from dh_client.client import RestClient
            >>> gms_server, token = "http://127.0.0.1:8080", "xxxxx..."  # or use env variables
            >>> client = RestClient(gms_server=gms_server, token=token)

        """
        from .entities import tags, users, datasets, glossary_terms, dashboards

        self.graphql_url = os.getenv("DATAHUB_GRAPHQL_HOST") or kwargs.pop(
            "graphql_server", None
        )
        super(RestClient, self).__init__(*args, **kwargs)
        self.env = env
        self.datahub_gms_server = kwargs.get("gms_server") or os.getenv(
            "DATAHUB_GMS_HOST"
        )
        self.datahub_token = kwargs.get("token") or os.getenv("DATAHUB_GMS_TOKEN")
        self.datahub_actor = datahub_actor
        self.dataset_platform = dataset_platform
        self.dashboard_platform = dashboard_platform

        # graphql-related attributes

        self.graphql_url = (
            f"{self.graphql_url}/api/graphql"
            if self.graphql_url
            else f"{self.datahub_gms_server}/api/graphql"
        )
        self.graphql_headers = {
            f"Authorization": f"Bearer {self.datahub_token}",
            "X-DataHub-Actor": self.datahub_actor,
            "Content-Type": "application/json",
        }

        # add entities
        self.tag = tags.Tag(self)
        self.user = users.User(self)
        self.dataset = datasets.Dataset(self)
        self.glossary_term = glossary_terms.GlossaryTerm(self)
        self.dashboard = dashboards.Dashboard(self)
