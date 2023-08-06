import datahub.metadata.schema_classes as models

from . import Entity


class Link(Entity):
    @staticmethod
    def create_mpc_association(
        entity_type: str, entity_urn: str, links: dict, actor: str
    ) -> dict:
        """Create a MPC dictionary for links.

        Args:
             entity_type: The entity type.
             entity_urn: The entity URN.
             links: The dictionary of links
             actor: The actor.

        Return:
            The MPC dictionary.
        """
        return Link._create_mpc_dict(
            entity_type,
            entity_urn,
            "institutionalMemory",
            models.InstitutionalMemoryClass(
                elements=[
                    models.InstitutionalMemoryMetadataClass(
                        url=links[desc],
                        description=desc,
                        createStamp=models.AuditStampClass(time=0, actor=actor),
                    )
                    for desc in links.keys()
                ]
            ),
        )
