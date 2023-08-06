from typing import List, Union

import datahub.metadata.schema_classes as models
from datahub.ingestion.source.metadata.business_glossary import make_glossary_term_urn

from . import Entity


class GlossaryTerm(Entity):
    """

    Examples:

        >>> client.glossary_term.upsert(name="glossary term y")
    """

    entity_type: str = "glossaryTerm"
    aspect_name: str = "glossaryTermInfo"

    def _create_mpc(self, name: str, source: str = "INTERNAL") -> List[dict]:
        """Create a tag mpc.

        Args:
            name: glossary term name.
            source: The source.

        Returns: A list with a single mpc dictionary.
        """
        return [
            dict(
                entityType=GlossaryTerm.entity_type,
                entityUrn=make_glossary_term_urn([name]),
                aspectName=GlossaryTerm.aspect_name,
                aspect=models.GlossaryTermInfoClass(definition=name, termSource=source),
            )
        ]

    @staticmethod
    def create_mpc_association(
        entity_type: str,
        entity_urn,
        glossary_terms: List[Union[str, List[str]]],
        actor: str,
    ) -> dict:
        """Create a glossary terms MPC dictionary.

        Args:
             entity_type: The entity type.
             entity_urn: The entity URN.
             glossary_terms: The list of custom properties.

        Return:
            The MPC dictionary.
        """
        return GlossaryTerm._create_mpc_dict(
            entity_type,
            entity_urn,
            "glossaryTerms",
            models.GlossaryTermsClass(
                terms=[
                    models.GlossaryTermAssociationClass(
                        make_glossary_term_urn(
                            [term] if isinstance(term, str) else term
                        )
                    )
                    for term in glossary_terms
                ],
                auditStamp=models.AuditStampClass(time=0, actor=actor),
            ),
        )
