from typing import TYPE_CHECKING, Optional

import datetime
from enum import Enum
import json

from hoss.api import CoreAPI
from hoss.ref import DatasetRef
import hoss.error

if TYPE_CHECKING:
    from hoss.namespace import Namespace

PERM_NONE = None
PERM_READ = "r"
PERM_READ_WRITE = "rw"


class DeleteStatus(Enum):
    NOT_SCHEDULED = "NOT_SCHEDULED"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    ERROR = "ERROR"


class Dataset(CoreAPI, DatasetRef):
    def __init__(self, namespace: 'Namespace', dataset_name: str, description: str,
                 created_on: datetime.datetime, delete_on: datetime.datetime, delete_status: DeleteStatus,
                 root_directory: str, owner: str, bucket: str, permissions: dict, sync_type: Optional[str],
                 sync_policy: Optional[dict]) -> None:
        self.namespace = namespace
        self.dataset_name = dataset_name
        self.description = description
        self.created_on = created_on
        self.delete_on = delete_on
        self.delete_status = delete_status
        self.root_directory = root_directory
        self.owner = owner
        self.bucket = bucket
        self.permissions = permissions
        self.sync_type = sync_type
        self.sync_policy = sync_policy

        CoreAPI.__init__(self, server_url=self.namespace.base_url, auth_instance=namespace.auth)
        DatasetRef.__init__(self, namespace=self.namespace, parent=None, dataset_name=dataset_name,
                            key=root_directory, name='', etag=None, last_modified=None, size_bytes=None)

    def __repr__(self) -> str:
        if self.delete_status != DeleteStatus.NOT_SCHEDULED:
            return f"<Dataset: {self.namespace} - {self.dataset_name} (DELETE STATUS: {self.delete_status.value})>"
        else:
            return f"<Dataset: {self.namespace} - {self.dataset_name}>"

    def display(self):
        """Helper to print some useful info about the dataset"""
        print("--Dataset------")
        print(f"Name: {self.dataset_name}")
        print(f"Description: {self.description}")
        print(f"Namespace: {self.namespace}")
        print(f"Created On: {self.created_on}")
        print(f"Root Directory: {self.root_directory}")
        print(f"Owner: {self.owner}")
        print(f"Delete Status: {self.delete_status.value}")
        if self.delete_status != DeleteStatus.NOT_SCHEDULED:
            print(f"Delete On: {self.delete_on}")
        print("Permissions:")
        for u, p in self.permissions.items():
            print(f"\t{u}: {p}")
        print("---------------")
        return self

    def is_sync_enabled(self) -> bool:
        """Check if sync is enabled for the dataset"""
        response = self._request("GET", f"/namespace/{self.namespace.name}/dataset/{self.dataset_name}/sync")
        return response

    def enable_sync(self, sync_type: str, sync_policy: Optional[dict] = None) -> None:
        """Method to enable syncing on a dataset. The namespace must also already have syncing enabled.

        You can call this multiple times if syncing is already enabled and you are trying to modify the sync policy.
        If you are trying to modify the sync type, you should first disable and then re-enable the sync policy.

        If the namespace is configured with duplex syncing, you can set the dataset to either simplex or duplex
        If the namespace is configured with only simplex syncing, you can only set the dataset to simplex

        Note - currently syncing only will sync objects mutated after syncing is enabled.

        Args:
            sync_type: type of sync config (`simplex` or `duplex`)
            sync_policy: Dictionary specifying an optional sync policy to modify sync behavior. Review documentation
                         for details on how to create a sync policy.

        Returns:
            None
        """
        if sync_type not in ["simplex", "duplex"]:
            raise hoss.error.HossException(f"'sync_type' must be either 'simplex' or 'duplex'")

        data = {"sync_type": sync_type}

        if sync_policy:
            data["sync_policy"] = json.dumps(sync_policy)

        self._request("PUT", f"/namespace/{self.namespace.name}/dataset/{self.dataset_name}/sync", json=data)

    def disable_sync(self) -> None:
        """Disable dataset syncing

        Returns:
            None
        """
        self._request("DELETE", f"/namespace/{self.namespace.name}/dataset/{self.dataset_name}/sync")

    # Dataset admin methods
    def set_user_permission(self, username, permission):
        """Set permissions on the dataset for a user.

        This will attach the user's "personal" group under the hood.

        Args:
            username: username for the user you wish to set
            permission: permission level ('r', 'rw', or None)

        Returns:

        """
        if permission == PERM_NONE:
            self._request("DELETE", f"/namespace/{self.namespace.name}/dataset/{self.dataset_name}/user/{username}")
            del self.permissions[username + "-hoss-default-group"]
        else:
            self._request("PUT", f"/namespace/{self.namespace.name}/dataset/{self.dataset_name}/user/{username}/access/{permission}")
            self.permissions[username + "-hoss-default-group"] = permission
        return self
    
    def set_group_permission(self, group_name, permission):
        """Set permissions on the dataset for a groupd.

        This will attach the user's "personal" group under the hood.

        Args:
            group_name: group you wish to set
            permission: permission level ('r', 'rw', or None)

        Returns:

        """
        if permission == PERM_NONE:
            self._request("DELETE", f"/namespace/{self.namespace.name}/dataset/{self.dataset_name}/group/{group_name}")
            del self.permissions[group_name]
        else:
            self._request("PUT", f"/namespace/{self.namespace.name}/dataset/{self.dataset_name}/group/{group_name}/access/{permission}")
            self.permissions[group_name] = permission
        return self
    
    def suggest_keys(self, prefix, limit=None):
        """Get suggestions for keys based on existing metadata.
        
        Args:
            prefix: substring that will be autocompleted to get suggestions
            limit: number of documents to return suggestions (due to duplicate results in multiple documents
                the actual number of suggestions could be lower than the limit, and due to multiple matching
                keys in a single document the number of suggestions could be higher than the limit)
        
        Returns:
            A list of suggested keys
        """

        # construct query parameters
        query_params = [f"prefix={prefix}"]
        if limit:
            query_params.append(f"limit={limit}")
        query_param_str = "&".join(query_params)

        # make request
        url = f"/search/namespace/{self.namespace.name}/dataset/{self.dataset_name}/key?{query_param_str}"
        response = self._request("GET", url)

        return response["keys"]

    def suggest_values(self, key, prefix, limit=None):
        """Get suggestions for values for a given key based on existing metadata.
        
        Args:
            key: the key for which to return suggested values
            prefix: substring that will be autocompleted to get suggestions
            limit: number of documents to return suggestions (due to duplicate results in multiple documents
                the actual number of suggestions could be lower than the limit, and due to multiple matching
                keys in a single document the number of suggestions could be higher than the limit)
        
        Returns:
            A list of suggested values
        """

        # construct query parameters
        query_params = [f"prefix={prefix}"]
        if limit:
            query_params.append(f"limit={limit}")
        query_param_str = "&".join(query_params)

        # make request
        url = f"/search/namespace/{self.namespace.name}/dataset/{self.dataset_name}/key/{key}/value?{query_param_str}"
        response = self._request("GET", url)

        return response["values"]
