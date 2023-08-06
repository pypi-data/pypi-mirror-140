from typing import List

import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models

from dh_client.entities import Entity


class Owner(Entity):
    @staticmethod
    def create_owners_aspect(
        owners: List[str], dataowner: str = "DATAOWNER"
    ) -> models.OwnershipClass:
        """Create a `models.OwnershipClass` instance based on the given list of owners.

        Args:
            owners: List of owners.

        Return:
            A `models.OwnershipClass` instance.
        """
        return models.OwnershipClass(
            owners=[
                models.OwnerClass(builder.make_user_urn(owner), type=dataowner)
                for owner in owners
            ]
        )

    @staticmethod
    def create_mpc_association(
        entity_type: str,
        entity_urn: str,
        owners: List[str],
        owner_type: str = "DATAOWNER",
    ) -> dict:
        """Create a MPC dictionary with owners.

        Args:
             entity_type: The entity type.
             entity_urn: The entity URN.
             owners: The list of owners.
             owner_type: The owner type.

        Return:
            The MPC dictionary.
        """
        return Owner._create_mpc_dict(
            entity_type,
            entity_urn,
            "ownership",
            models.OwnershipClass(
                owners=[
                    models.OwnerClass(builder.make_user_urn(owner), type=owner_type)
                    for owner in owners
                ]
            ),
        )
