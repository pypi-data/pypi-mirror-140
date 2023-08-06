from streambird.api_resources.magic_links import MagicLinks

from ._version import __version__  # noqa: F401
from .api import Api

class Client:
    """Main class serves as an interface for Streambird API"""

    def __init__(self, api_key, source=None, api_instance_url=None):
        self.api = Api(
            api_key, user_agent_extension=source, api_instance_url=api_instance_url
        )
        self.magic_links = MagicLinks(self)
