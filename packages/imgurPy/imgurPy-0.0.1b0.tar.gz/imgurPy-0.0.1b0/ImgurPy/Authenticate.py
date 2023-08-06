from .core import Core


class Authenticate(Core):
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

    @property
    def OAuth2(self) -> str:
        """Generate refresh token link.

        Returns:
            str: refresh token link
            
        """
        return f'{self.API}/oauth2/authorize?client_id={self.client_id}&response_type=token'

    @property
    def access_token(self):
        """Call GenerateAccessToken and return access token.

        Returns:
            str: access token
        """        
        response = self.GenerateAccessToken()
        self.__access_token = response['access_token']
        return self.__access_token

    def GenerateAccessToken(self) -> dict:
        """Given a user's refresh token, this endpoint generates an access token.

        Returns:
            dict: response of GenerateAccessToken
        """
        endpoint = f'{self.API}/oauth2/token'
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token',
        }
        response = self.make_request(
            "post",
            endpoint,
            data=payload
        ).json()
        return response
