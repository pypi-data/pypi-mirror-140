import os
import hashlib

from boto3.s3.transfer import MB
from hoss.ref import DatasetRef


def hash_file(path: str, chunk_size: int = 8 * MB, multipart_threshold: int = 8 * MB) -> str:
    """Utility to hash a file like how S3 etags are generated.

    If the file is smaller than or equal to the multipart upload chunk size, it is assumed a single
    chunk was used. In this case, the etag is simply the hexdigest of the md5 hash of the file.

    If the file is larger than the multipart upload chunk size, it is assumed multiple parts
    were used to write the file. In this case, the etag is the hexdigest of the md5 hash
    of each part's md5 hash concatenated, with `-<number of parts>` appended.

    Args:
        path: path to the file to hash
        chunk_size: size in bytes that would be used to chunk a file during a multipart upload (default is 8MB)
        multipart_threshold: size in bytes that will trigger multipart uploads to be used (default is 8MB)

    Returns:
        etag formatted hash
    """
    info = os.stat(path)

    if info.st_size <= multipart_threshold:
        # Single part upload
        return hashlib.md5(open(path, 'rb').read()).hexdigest()
    else:
        # Multipart upload
        chunk_hashes = list()
        with open(path, 'rb') as f:
            while True:
                chunk_bytes = f.read(chunk_size)
                if not chunk_bytes:
                    break

                chunk_hashes.append(hashlib.md5(chunk_bytes))

        # A multi-part upload was used. Need to create combined hash
        combined_hash = b""
        for c in chunk_hashes:
            combined_hash += c.digest()
        return f"{hashlib.md5(combined_hash).hexdigest()}-{len(chunk_hashes)}"


def etag_does_match(ref: DatasetRef, path: str) -> bool:
    """Utility to check if an etag matches the contents of a local file

    Args:
        ref: the DatasetRef you are comparing against (this reference's etag will be used)
        path: path to the file to hash and compare

    Returns:
        true if contents are the same, false if they are not
    """
    local_etag = hash_file(path,
                           ref.namespace.object_store.get_multipart_chunk_size(),
                           ref.namespace.object_store.get_multipart_threshold())
    if ref.etag == f'"{local_etag}"':
        return True
    else:
        return False
