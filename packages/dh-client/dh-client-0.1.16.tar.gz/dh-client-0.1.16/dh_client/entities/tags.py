from typing import List

import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models

from dh_client.entities import Entity


class Tag(Entity):
    """This class allows you to modify tags.

    Examples:

        The standard way to modify a tag:

        >>> client.tag.upsert(name="foo", description="A random tag description")


        Modify a tag using a json file:

        $ cat new_user.json
        {"name": "foo2", "description": "A random tag description"}
        >>> client.tag.upsert(file_pattern="new_*.json")

    """

    entity_type: str = "tag"
    aspect_name: str = "tagProperties"

    def _create_mpc(self, name: str, description: str = "") -> List[dict]:
        """Create a tag mpc.

        Args:
            name: tag name.
            description: tag description.

        Returns: A list with a single mpc dictionary.
        """
        return [
            self._create_mpc_dict(
                Tag.entity_type,
                builder.make_tag_urn(name),
                Tag.aspect_name,
                models.TagPropertiesClass(name=name, description=description),
            )
        ]

    @staticmethod
    def create_mpc_association(
        entity_type: str, entity_urn: str, tags: List[str]
    ) -> dict:
        """Create an MPC tags association dictionary.

        Args:
            entity_type: The entity type.
            entity_urn: The entity URN.
            tags: The list of tags.

        Return: The MPC dictionary.
        """
        return Tag._create_mpc_dict(
            entity_type,
            entity_urn,
            "globalTags",
            models.GlobalTagsClass(
                tags=[
                    models.TagAssociationClass(builder.make_tag_urn(tag))
                    for tag in tags
                ]
            ),
        )
