from typing import List, Dict

import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models

from dh_client.entities import Entity
from dh_client.entities.glossary_terms import GlossaryTerm
from dh_client.entities.links import Link
from dh_client.entities.owners import Owner
from dh_client.entities.tags import Tag


class Dashboard(Entity):
    """
    Examples:

    """

    entity_type: str = "dashboard"

    @staticmethod
    def _get_chart_urn(name: str, platform: str) -> str:
        """Get the chart URN.

        Args:
             name: Chart name.
             platform: Platform name.

        Returns:
            The chart URN.
        """
        return builder.make_chart_urn(platform=platform, name=name)

    @staticmethod
    def _get_dashboard_urn(name: str, platform: str) -> str:
        """Get the dashboard URN.

        Args:
             name: The dashboard name.
             platform: The dashboard platform.

        Return: The dashboard URN.
        """
        return builder.make_dashboard_urn(platform=platform, name=name)

    def _create_mpc(
        self,
        name: str,
        inputs: List[str] = None,
        title: str = None,
        description: str = None,
        tags: List[str] = None,
        owners: List[str] = None,
        glossary_terms: List[str] = None,
        url: str = None,
        links: Dict[str, str] = None,
        platform: str = "datastudio",
    ) -> List[dict]:
        """Create a dashboard mpc.

        Args:
            name: dashboard name.
            inputs: Input charts.
            title: The title.
            description: The dashboard's name
            tags: List of tags.
            owners: List of owners.
            glossary_terms: List of glossary terms.
            url: The url.
            links: List of links.
            platform: The platform.


        Returns: A list with a single mpc dictionary.
        """
        inputs = inputs or []
        dashboard_urn = self._get_dashboard_urn(name, platform)

        mpc = [
            self._create_mpc_dict(
                "chart",
                self._get_chart_urn(name, platform),
                "chartInfo",
                models.ChartInfoClass(
                    title=title if title else name,
                    description=description,
                    externalUrl=url,
                    lastModified=models.ChangeAuditStampsClass(
                        created=models.AuditStampClass(
                            time=0, actor=self.emmiter.datahub_actor
                        )
                    ),
                    inputs=[
                        builder.make_dataset_urn(
                            platform=self.emmiter.dataset_platform,
                            name=input_,
                            env=self.emmiter.env,
                        )
                        for input_ in inputs
                    ],
                ),
            ),
            self._create_mpc_dict(
                self.entity_type,
                dashboard_urn,
                "dashboardInfo",
                models.DashboardInfoClass(
                    title=title if title else name,
                    description=description,
                    externalUrl=url,
                    charts=[self._get_chart_urn(name, platform)],
                    lastModified=models.ChangeAuditStampsClass(
                        created=models.AuditStampClass(
                            time=0, actor=self.emmiter.datahub_actor
                        )
                    ),
                ),
            ),
        ]

        if tags:
            mpc.append(
                Tag.create_mpc_association(self.entity_type, dashboard_urn, tags)
            )
        if owners:
            mpc.append(
                Owner.create_mpc_association(self.entity_type, dashboard_urn, owners)
            )
        if glossary_terms:
            mpc.append(
                GlossaryTerm.create_mpc_association(
                    self.entity_type,
                    dashboard_urn,
                    glossary_terms,
                    self.emmiter.datahub_actor,
                )
            )

        if links:
            mpc.append(
                Link.create_mpc_association(
                    self.entity_type, dashboard_urn, links, self.emmiter.datahub_actor
                )
            )

        return mpc
