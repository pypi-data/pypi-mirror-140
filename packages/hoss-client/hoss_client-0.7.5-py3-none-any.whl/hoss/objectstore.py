from typing import Optional

import boto3
from boto3.s3.transfer import TransferConfig, MB
import botocore.exceptions
import datetime

from hoss.api import CoreAPI
from hoss.auth import AuthService


class ObjectStore(CoreAPI):
    """A class representing an Object Store that provides low-level functionality. Typically you should be interfacing
     with DatasetRef instances."""
    def __init__(self, object_store_name: str, description: str, endpoint: str, object_store_type: str,
                 server_url: str, auth_instance: Optional[AuthService] = None):
        """A class to interact with the Hoss core service
        
        Args:
            object_store_name: name of the object store
            description: description of the store
            endpoint: object store endpoint (e.g. http://localhost, https://s3.amazonaws.com)
            object_store_type: type of object store (e.g. "s3", "minio")
        """
        super().__init__(server_url, auth_instance)

        self.name = object_store_name
        self.description = description
        self.endpoint = endpoint
        self.object_store_type = object_store_type

        # S3 client
        self._client = dict()
        self._transfer_config = TransferConfig()
        self._sts_credential_expire = None
        self._sts_credential_expire_in_seconds = self.auth.jwt_exp_seconds / 2

    def __repr__(self):
        return f"<Object Store: {self.name} - {self.description} ({self.endpoint})>"

    def _get_sts_credentials(self, namespace: str) -> dict:
        return self._request("GET", f"/namespace/{namespace}/sts")

    def _get_client(self, namespace: str):
        if self._client.get(namespace) is not None:
            if self._sts_credential_expire > datetime.datetime.utcnow():
                # Credentials are still good. Return existing client.
                return self._client.get(namespace)

        # Fetch temporary credentials and create an S3 client
        creds = self._get_sts_credentials(namespace)
        self._sts_credential_expire = datetime.datetime.utcnow() + \
                                      datetime.timedelta(seconds=self._sts_credential_expire_in_seconds)

        client = boto3.client(
            "s3",
            endpoint_url=creds["endpoint"],
            aws_access_key_id=creds["access_key_id"],
            aws_secret_access_key=creds["secret_access_key"],
            aws_session_token=creds["session_token"],
            region_name=creds["region"]
        )
        self._client[namespace] = client
        return client

    def reset_client(self) -> None:
        """This method removes the boto3 clients stored in this instance. This is useful when trying to use the
        client lib with multiprocessing and you need to make sure each process has its own boto3 client.

        Returns:
            None
        """
        keys = [k for k in self._client.keys()]
        for k in keys:
            del self._client[k]

        self._client = dict()

    def object_exists(self, namespace: str, bucket: str, key) -> bool:
        """Check if an object exists in the object store

        Args:
            namespace: Namespace name
            bucket: Bucket name
            key: Object key

        Returns:
            True if the object exists, False if it does not
        """
        # TODO: Need to handle grabbing metadata here better
        client = self._get_client(namespace)

        try:
            client.head_object(Bucket=bucket, Key=key)
            return True
        except botocore.exceptions.ClientError as ce:
            code = ce.response["Error"]["Code"]
            if code == '404':
                return False
            raise

    def head_object(self, namespace: str, bucket: str, key) -> dict:
        """Method to perform a HEAD operation on an object

        Args:
            namespace: Namespace name
            bucket: Bucket name
            key: Object key

        Returns:
            Dict with the fields `last_modified`, `size_bytes`, `etag`, and `metadata`
        """
        client = self._get_client(namespace)
        response = client.head_object(Bucket=bucket, Key=key)
        return {"last_modified": response.get('LastModified'),
                "size_bytes": response.get('ContentLength'),
                "etag": response.get('ETag'),
                "metadata": response.get('Metadata')}

    @staticmethod
    def _remove_prefix(text, prefix):
        return text[text.startswith(prefix) and len(prefix):]

    def list_objects(self, namespace: str, bucket: str, prefix, recursive=False) -> dict:
        """Method to list objects in a bucket, optionally with a prefix and recursively

        While iterating, we use the `/` char as a delimiter to represent "folders" within the store

        Args:
            namespace: Name of the namespace
            bucket: Name of the bucket
            prefix: key prefix to start listing from
            recursive: If True, continue to list objects "down" the tree, instead of staying within the specified
                       "directory" level

        Yields:
            a dict with the fields `key`, `name`, `last_modified`, `size_bytes`, and `etag`

        """
        client = self._get_client(namespace)

        kwargs = {
            "Bucket": bucket,
            "Delimiter": "/",
        }

        if recursive:
            del kwargs["Delimiter"]

        if not prefix.endswith('/'):
            prefix += '/'
        kwargs["Prefix"] = prefix

        paginator = client.get_paginator("list_objects_v2")
        for resp in paginator.paginate(**kwargs):
            for d in resp.get("CommonPrefixes", []):
                yield {"key": d["Prefix"],
                       "name": self._remove_prefix(d["Prefix"], prefix),
                       "etag": d.get("ETag"),
                       "last_modified": d.get("LastModified"),
                       "size_bytes": d.get("Size")}

            for f in resp.get("Contents", []):
                name = self._remove_prefix(f["Key"], prefix)
                if name == ".dataset.yaml":
                    # Do not show the user the internal Hoss '.dataset.yaml' file.
                    continue

                yield {"key": f["Key"],
                       "name": name,
                       "etag": f.get("ETag"),
                       "last_modified": f.get("LastModified"),
                       "size_bytes": f.get("Size")}

    def get_object(self, namespace: str, bucket: str, key):
        """Method to get an object's contents from the object store

        Args:
            namespace: Namespace name
            bucket: Bucket name
            key: Object key

        Returns:
            contents of the object
        """
        # TODO: Need to handle grabbing metadata here better
        client = self._get_client(namespace)
        return client.get_object(Bucket=bucket, Key=key)["Body"].read()

    def put_object(self, namespace: str, bucket: str, key: str,
                   data: bytes, metadata: Optional[dict] = None) -> None:
        """Method to write an object to the object store

        Args:
            namespace: Namespace name
            bucket: Bucket name
            key: Object key
            data: The data to write
            metadata: A dictionary of key-value pairs to set as object metadata

        Returns:
            None
        """
        client = self._get_client(namespace)
        client.put_object(Bucket=bucket, Key=key, Body=data,
                          Metadata=metadata if metadata is not None else dict())

    def delete_object(self, namespace: str, bucket: str, key):
        """Method to delete an object from the object store

        Args:
            namespace: Namespace name
            bucket: Bucket name
            key: Object key

        Returns:
            None
        """
        client = self._get_client(namespace)
        client.delete_object(Bucket=bucket, Key=key)

    def copy_object(self, namespace: str, bucket: str, key: str, target_key: str) -> None:
        """Method to perform a copy an object from one key to another in the object store

        Args:
            namespace: Namespace name
            bucket: Bucket name
            key: Object key
            target_key: Destination object key

        Returns:
            None
        """
        client = self._get_client(namespace)
        source = {"Bucket": bucket, "Key": key}
        client.copy_object(Bucket=bucket, Key=target_key, CopySource=source)

    def download_file(self, namespace: str, bucket: str, key: str, filename: str):
        """Method to download an object to a file locally

        Args:
            namespace: Namespace name
            bucket: Bucket name
            key: Source object key
            filename: Absolute path to a file where the object's contents will be written

        Returns:

        """
        client = self._get_client(namespace)
        return client.download_file(bucket, key, filename, Config=self._transfer_config)

    def download_fileobj(self, namespace: str, bucket: str, key, fh):
        """Download an object to a file-like object.

        The file-like object must be in binary mode.
        This is a managed transfer which will perform a multipart download in multiple threads if necessary.

        Args:
            namespace: Namespace name
            bucket: Bucket name
            key: Object key
            fh: A file handle to a file-like object in binary mode

        Returns:

        """
        client = self._get_client(namespace)
        return client.download_fileobj(bucket, key, fh, Config=self._transfer_config)

    def upload_file(self, namespace: str, bucket: str, key, filename, metadata: Optional[dict] = None):
        """Upload a file to an object

        Args:
            namespace: Namespace name
            bucket: Bucket name
            key: Object key
            filename: Absolute path to the file to upload
            metadata: A dictionary of key-value pairs to set as object metadata

        Returns:

        """
        client = self._get_client(namespace)
        return client.upload_file(filename, bucket, key, Config=self._transfer_config,
                                  ExtraArgs={"Metadata": metadata} if metadata is not None else None)

    def upload_fileobj(self, namespace: str, bucket: str, key, fh, metadata: Optional[dict] = None):
        """Upload a file-like object to an object

        Args:
            namespace: Namespace name
            bucket: Bucket name
            key: Object key
            fh: File handle to a file-like object in binary mode
            metadata: A dictionary of key-value pairs to set as object metadata

        Returns:

        """
        client = self._get_client(namespace)
        return client.upload_fileobj(fh, bucket, key, Config=self._transfer_config,
                                     ExtraArgs={"Metadata": metadata} if metadata is not None else None)

    def set_transfer_config(self, multipart_threshold: int, max_concurrency: int,
                            multipart_chunksize: int = 8*MB) -> None:
        """Function to set the transfer configuration used in managed transfers.

        Args:
            multipart_threshold: The transfer size threshold for which multipart uploads, downloads,
                                 and copies will automatically be triggered.
            max_concurrency: The maximum number of threads that will be making requests to perform a transfer.
            multipart_chunksize: The partition size of each part for a multipart transfer. (default 8MB)

        Returns:

        """
        self._transfer_config = TransferConfig(
            multipart_threshold=multipart_threshold,
            max_concurrency=max_concurrency,
            multipart_chunksize=multipart_chunksize
        )

    def get_multipart_chunk_size(self) -> int:
        """Get the current multi-part chunk size

        Returns:
            The multi-part chunk size in bytes
        """
        return self._transfer_config.multipart_chunksize

    def get_multipart_threshold(self) -> int:
        """Get the current multi-part threshold

        Returns:
            The multi-part threshold in bytes
        """
        return self._transfer_config.multipart_threshold
