from typing import Optional, List
from urllib.parse import urlparse
import datetime
import json

from hoss.error import *
from hoss.auth import AuthService
from hoss.dataset import Dataset, DeleteStatus
from hoss.api import CoreAPI
from hoss.objectstore import ObjectStore


class Namespace(CoreAPI):
    def __init__(self, server_url: str, name: str, bucket_name: str,
                 description: Optional[str] = None,
                 object_store: Optional[ObjectStore] = None,
                 auth_instance: Optional[AuthService] = None) -> None:
        """A class to interact with the Hoss core service
        
        Args:
            server_url: root URL to the server, including the protocol
            name: name of the namespace
            auth_instance: an optional AuthService instance that will be used instead of using the
                           server_url to instantiate one
        """
        super().__init__(server_url, auth_instance)
        self.name = name
        self.description = description
        self.object_store = object_store
        self.bucket = bucket_name

    def __repr__(self):
        return f"<Namespace: {self.name} - {self.description}>"

    def get_sync_configuration(self) -> dict:
        """Method to get the sync configuration for the namespace

        Returns:
            a list of dictionaries with the fields "target_core_service", "target_namespace", and "sync_type"
        """
        response = self._request("GET", f"/namespace/{self.name}/sync")
        result = {"sync_enabled": len(response) > 0, "sync_targets": list()}
        for t in response:
            result['sync_targets'].append({"target_core_service": t["target_core_service"],
                                           "target_namespace": t["target_namespace"],
                                           "sync_type": t["sync_type"]})

        return result

    def enable_sync_target(self, target_server_url: str, sync_type: str,
                           target_namespace: Optional[str] = None) -> None:
        """Enable a sync target, linking the namespaces together.

        Args:
            target_server_url: URL to the target server (e.g. https://hoss.mydomain.com)
            sync_type: The sync type ('simplex' or 'duplex')
            target_namespace: The namespace name to sync with

        Returns:
            None
        """
        parts = urlparse(target_server_url)
        target_core_service = f"{parts.scheme}://{parts.netloc}/core/v1"

        if not target_namespace:
            # If the target namespace is not provided, set it to the same name as the source namespace
            target_namespace = self.name

        if sync_type not in ["simplex", "duplex"]:
            raise HossException(f"'sync_type' must be either 'simplex' or 'duplex'")

        data = {"target_core_service": target_core_service,
                "target_namespace": target_namespace,
                "sync_type": sync_type}
        self._request("PUT", f"/namespace/{self.name}/sync", json=data)

    def disable_sync_target(self, target_server_url: str, target_namespace: str) -> None:
        """Remove a sync target, stopping all synchronization between the namespaces

        Args:
            target_server_url: URL to the target server (e.g. https://hoss.mydomain.com)
            target_namespace: The namespace name to remove

        Returns:
            None
        """
        parts = urlparse(target_server_url)
        target_core_service = f"{parts.scheme}://{parts.netloc}/core/v1"

        data = {"target_core_service": target_core_service,
                "target_namespace": target_namespace,
                "sync_type": "simplex"}
        self._request("DELETE", f"/namespace/{self.name}/sync", json=data)

    def _populate_dataset(self, api_response: dict) -> Dataset:
        perms_processsed = {
            perm["group"]["group_name"]: perm["permission"]
            for perm in api_response["permissions"]
        }

        # Because the zero value for golang representing a datetime does not have a decimal
        # component, but when the time is actually set it does, we need to parse the `delete_on`
        # value conditionally.
        if "." in api_response['delete_on']:
            delete_on = datetime.datetime.strptime(api_response['delete_on'], "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            delete_on = datetime.datetime.strptime(api_response['delete_on'], "%Y-%m-%dT%H:%M:%SZ")

        # For the user, we'll hide defaults for syncing if syncing is disabled
        if api_response['sync_enabled']:
            sync_type = api_response['sync_type']
            sync_policy = json.loads(api_response['sync_policy'])
        else:
            sync_type = None
            sync_policy = None

        return Dataset(self,
                       api_response["name"],
                       api_response["description"],
                       datetime.datetime.strptime(api_response['created'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                       delete_on,
                       DeleteStatus(api_response['delete_status']),
                       api_response['root_directory'],
                       api_response["owner"]["username"],
                       self.bucket,
                       perms_processsed,
                       sync_type,
                       sync_policy)

    def list_datasets(self) -> List[Dataset]:
        """List Datasets within the namespace

        Returns:
            A list of Dataset instances
        """
        response = self._request("GET", f"/namespace/{self.name}/dataset")
        return [self._populate_dataset(d) for d in response]

    def create_dataset(self, dataset_name: str, description: str = "") -> Dataset:
        """Create a new dataset

        Args:
            dataset_name: name of the dataset. Must be unique within the namespace
            description: A description of the dataset

        Returns:
            A populated Dataset instance
        """
        data = {"name": dataset_name, "description": description}
        response = self._request("POST", f"/namespace/{self.name}/dataset/", json=data)
        return self._populate_dataset(response)

    def get_dataset(self, dataset_name: str) -> Dataset:
        """Get a Dataset instance by name

        Args:
            dataset_name: The name of the dataset

        Returns:
            A populated Dataset instance
        """
        response = self._request("GET", f"/namespace/{self.name}/dataset/{dataset_name}")
        return self._populate_dataset(response)

    def delete_dataset(self, dataset_name: str) -> None:
        """Mark a dataset for deletion. Depending on your server configuration, this may happen immediately
        or after some fixed amount of time (e.g. 48hrs).

        Args:
            dataset_name: The name of the dataset to delete

        Returns:
            None
        """
        self._request("DELETE", f"/namespace/{self.name}/dataset/{dataset_name}")

    def restore_dataset(self, dataset_name: str) -> None:
        """Restore a dataset that has been marked for delete, but is still in the `SCHEDULED` state.

        Note: This is only available to users with the admin role.

        Args:
            dataset_name: The name of the dataset to "unmark" for delete

        Returns:
            None
        """
        self._request("PUT", f"/namespace/{self.name}/dataset/{dataset_name}/restore")


