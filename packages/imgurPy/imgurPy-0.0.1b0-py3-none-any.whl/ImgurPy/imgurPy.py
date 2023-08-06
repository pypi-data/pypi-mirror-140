from .Account import Account
from .Album import Album
from .Image import Image


class ImgurPy(Account, Album, Image):
    """Integrate Account, Comment (not implemented), Album, Gallery (not implemented) and Image modules

    """
    API = 'https://api.imgur.com'
    __version__ = '0.0.1beta'

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str = None
    ):
        Account.__init__(self, client_id, client_secret,
                         refresh_token, self.API)
        Album.__init__(self, client_id, client_secret,
                       refresh_token, self.API)
        Image.__init__(self, client_id, client_secret,
                       refresh_token, self.API)
        self.__access_token = None

    @property
    def __version__(self,a) -> str:
        
        return self.__version__
