import json
import logging
import warnings
from glob import iglob
from typing import List, Any, Callable

import requests
from datahub.emitter.mcp import MetadataChangeProposalWrapper, DictWrapper
from datahub.metadata.schema_classes import ChangeTypeClass

from dh_client.client import RestClient
from dh_client.exceptions import FailedToEmmitMpc
from dh_client.exceptions import NotSupportedYet

__all__ = ["datasets", "glossary_terms", "owners", "tags", "users", "dashboards"]


class Entity:
    entity_type: str
    annotations = {"kwargs": Any}

    def __init__(self, emmiter: RestClient) -> None:
        self.emmiter = emmiter

    def _apply_mcp(
        self, change_type, mpc: List[dict] = None, use_graphql: bool = False
    ) -> None:
        """Apply a collection of MetaChangeProposals (mpc).

        Args:
            change_type: The change type (create, update, upsert, delete, patch), currently, upsert is the only supported change type.
            mpc: List of meta proposal changes.
            use_graphql: Make a graphql post request instead of using the datahub emmiter.
        """
        if not mpc:
            warnings.warn("No mpc items were provided")

        for mpc_ in mpc or []:
            if mpc_.pop("use_graphql", use_graphql):
                r = requests.post(
                    self.emmiter.graphql_url,
                    headers=self.emmiter.graphql_headers,
                    json=mpc_,
                )
                try:
                    j = r.json()
                except json.decoder.JSONDecodeError:
                    raise ValueError(r.text)
                if "errors" in j:
                    logging.error(f"request url: {r.url}")
                    logging.error(f"request header: {self.emmiter.graphql_headers}")
                    logging.error(f"request json: {mpc_}")
                    raise ValueError(f"response json {j}")
            else:
                try:
                    self.emmiter.emit(
                        MetadataChangeProposalWrapper(changeType=change_type, **mpc_)
                    )
                except Exception as e:
                    raise FailedToEmmitMpc(mpc_, change_type) from e

    def _create_mpc_from_file(
        self, file_pattern: str, filter_func: Callable = None, recursive: bool = False
    ) -> List[dict]:
        """Create list of mpc based on the given file pattern.

        Args:
            file_pattern: The file-pattern (feel free to use wildcards).
            filter_func: an extra function to filter files.
            recursive: Match files recursively or not.

        Return: The list of MPC dictionaries.
        """
        mpc = []
        files_iter = (
            filter(filter_func, iglob(file_pattern, recursive=recursive))
            if filter_func
            else iglob(file_pattern, recursive=recursive)
        )
        for filepath in files_iter:
            logging.info(f"processing: {filepath}")
            with open(filepath, "r") as f:
                j = json.load(f)
                if isinstance(j, dict):
                    j = [j]
                for item in j:
                    if item:
                        mpc.extend(self._create_mpc(**item))
        return mpc

    def _create_mpc(self, **kwargs) -> List[dict]:
        """This method is implemented by the subclasses."""
        return [kwargs]

    @staticmethod
    def _create_mpc_dict(
        entity_type: str,
        entity_urn: str,
        aspect_name: str,
        aspect: DictWrapper,
        **kwargs,
    ) -> dict:
        """Create the mpc dictionary using positional argumenrs.

        Args:
            entity_type: The entity type.
            entity_urn: The entiry URN.
            aspect_name: The aspect name.
            aspect: The aspect.

        Returns:
            a dictionary with key/values in order to create the MPC object.
        """
        return dict(
            entityType=entity_type,
            entityUrn=entity_urn,
            aspectName=aspect_name,
            aspect=aspect,
            **kwargs,
        )

    def _create_mpc_wrapper(
        self, file_pattern: str, use_graphql: bool, **kwargs
    ) -> dict:
        if not file_pattern:
            mpc = self._create_mpc(**kwargs)
        else:
            mpc = self._create_mpc_from_file(file_pattern)
        return {"mpc": mpc, "use_graphql": use_graphql}

    def upsert(
        self, file_pattern: str = None, use_graphql: bool = False, **kwargs
    ) -> None:
        """Upsert the current entity

        Args:
            file_pattern: The file pattern.
            use_graphql: Use graphql or not.
            **kwargs: MPC parameters, don't pass keyword argument if file_pattern is used.
        """
        return self._apply_mcp(
            ChangeTypeClass.UPSERT,
            **self._create_mpc_wrapper(
                file_pattern=file_pattern, use_graphql=use_graphql, **kwargs
            ),
        )

    def _update(self, **kwargs):
        """Not supported yet."""
        raise NotSupportedYet(f"{self._update.__name__} is not supported yet")

    def _delete(self, **kwargs):
        """Not supported yet."""
        raise NotSupportedYet(f"{self._delete.__name__} is not supported yet")

    def _patch(self, **kwargs):
        """Not supported yet."""
        raise NotSupportedYet(f"{self._patch.__name__} is not supported yet")

    def _create(self, **kwargs):
        """Not supported yet."""
        raise NotSupportedYet(f"{self._create.__name__} is not supported yet")
