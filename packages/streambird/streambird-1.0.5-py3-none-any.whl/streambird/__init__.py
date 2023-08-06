from streambird.api_resources.magic_link import MagicLink
from streambird.api_resources.otp import Otp
from streambird.api_resources.oauth import OAuth
from streambird.api_resources.wallet import Wallet
from streambird.api_resources.user import User
from streambird.api_resources.session import Session

from ._version import __version__  # noqa: F401
from .api import Api

class Client:
    """Main class serves as an interface for Streambird API"""

    def __init__(self, api_key, source=None, api_instance_url=None):
        self.api = Api(
            api_key, user_agent_extension=source, api_instance_url=api_instance_url
        )
        self.magic_links = MagicLink(self)
        self.otps = Otp(self)
        self.oauth = OAuth(self)
        self.wallets = Wallet(self)
        self.users = User(self)
        self.sessions = Session(self)
