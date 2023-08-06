from typing import List

import datahub.emitter.mce_builder as builder
import datahub.metadata.schema_classes as models

from . import Entity


class User(Entity):
    entity_type: str = "corpUser"
    aspect_name: str = "corpUserInfo"

    """This class allows you to modify users.
    
    Examples:
    
        >>> client.user.upsert(name="userX", display_name="User X", email="userx@domain.com")
        $ cat new_user.json
        {"name": "foo", "email": "foo@domain.com", "display_name": "Foo"}
        >>> client.user.upsert(file_pattern="new_*.json")
    """

    def _create_mpc(
        self, name: str, email: str = "", display_name: str = None, active: bool = True
    ) -> List[dict]:
        """Create a user mpc dictionary.

        Args:
            name: The username.
            email: User's email address.
            display_name: The user's display name.
            active: True if user is active, else, False.

        Returns: A list with a single mpc dictionary.
        """
        return [
            dict(
                entityType=User.entity_type,
                entityUrn=builder.make_user_urn(username=name),
                aspectName=User.aspect_name,
                aspect=models.CorpUserInfoClass(
                    displayName=display_name if display_name else name,
                    email=email,
                    active=active,
                ),
            )
        ]
