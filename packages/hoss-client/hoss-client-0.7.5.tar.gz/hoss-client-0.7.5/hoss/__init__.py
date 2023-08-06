from typing import Optional

from hoss.error import *
from hoss.namespace import Namespace
from hoss.core import CoreService
from hoss.auth import AuthService

import urllib.parse


def connect(server_url: str, auth_instance: Optional[AuthService] = None) -> CoreService:
    """Connect to a server

    Args:
        server_url: URL to the server, including the protocol (e.g. https://hoss.myserver.com)
        auth_instance: Optionally provide an already configured auth instance. This can be useful when
                       interacting with multiple Hoss servers that each run their own auth service.

    Returns:
        A CoreService instance, which is the primary interface to a server.
    """
    return CoreService(server_url, auth_instance)


def resolve(uri, auth_instance: Optional[AuthService] = None):
    """Resolve a Hoss URI into a DatasetRef. This lets you directly load any ref.

    The Hoss URI format is `hoss+<server>:<namespace>:<dataset>/<object key>` and can be retrieved
    from any DatasetRef instance by the `uri` property.

    An example URI would be `hoss+https://hoss.myserver.com:default:example-ds/my-file.bin`

    Args:
        uri: Hoss URI formatted string
        auth_instance: Optionally provide an already configured auth instance. This can be useful when
                       interacting with multiple Hoss servers that each run their own auth service.

    Returns:
        A populated DatasetRef if the URI is valid
    """
    uri = urllib.parse.urlparse(uri)

    if not uri.scheme.lower().startswith("hoss"):
        raise ValueError("URI is not a valid Hoss URI")

    try:
        _, protocol = uri.scheme.lower().split("+")
        host, namespace_name, dataset_name = uri.netloc.split(":")
    except:
        raise ValueError("URI is not a valid Hoss URI")

    s = CoreService(f"{protocol}://{host}", auth_instance=auth_instance)
    ns = s.get_namespace(namespace_name)

    return ns.get_dataset(dataset_name) / uri.path
