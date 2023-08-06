
from .Authenticate import Authenticate


class Account(Authenticate):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        API: str,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.API = API
        self.__access_token = None
        Authenticate.__init__(
            self, client_id, client_secret, refresh_token, API)

    def AccountBase(self, username: str) -> dict:
        """Request standard user information. If you need the username for the account that is logged in, it is returned in the request for an access token. Note: This endpoint also supports the ability to lookup account base info by account ID. To do so, pass the query parameter account_id.

        Args:
            username (str): username

        Returns:
            dict: response of AccountBase
        """
        endpoint = f'{self.API}/3/account/{username}'
        headers = {
            'Authorization': f'Client-ID {self.client_id}'
        }
        return self.make_request(
            'get',
            endpoint,
            headers=headers,
        ).json()

    # FIXME: 回傳型態不一致問題
    def AccountBlockStatus(self, username: str) -> dict:
        """Determine if the user making the request has blocked a username.

        Args:
            username (str): username

        Returns:
            bool: True or False
        """
        self.__access_token = self.access_token
        endpoint = f'{self.API}/account/v1/{username}/block'
        headers = {
            'Authorization': f'Bearer {self.__access_token}',
            'Accept': 'application/vnd.api+json'
        }
        response = self.make_request(
            'get',
            endpoint,
            headers=headers,
        ).json()
        return response

    def AccountAlbum(
        self,
        username: str,
        albumHash: str
    ) -> dict:
        """Get additional information about an album, this endpoint works the same as the Album Endpoint. You can also use any of the additional routes that are used on an album in the album endpoint.

        Args:
            username (str): username
            albumHash (str): hash of the album

        Returns:
            dict: response of request
        """        
        endpoint = f'{self.API}/3/account/{username}/album/{albumHash}'
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = self.make_request(
            'get',
            endpoint,
            headers=headers,
        ).json()
        return response
