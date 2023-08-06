from .Authenticate import Authenticate


class Album(Authenticate):
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

    def Album(self, albumHash: str) -> dict:
        """Get additional information about an album.

        Args:
            albumHash (str): album hash

        Returns:
            dict: 
        """        
        endpoint = f'{self.API}/3/album/{albumHash}'
        headers = {
            'Authorization': f'Client-ID {self.client_id}'
        }
        response = self.make_request(
            'get',
            endpoint,
            headers=headers
        ).json()
        return response

    def AlbumImages(self, albumHash: str) -> dict:
        """Return all of the images in the album.

        Args:
            albumHash (str): album hash

        Returns:
            dict: 
        """        
        endpoint = f'{self.API}/3/album/{albumHash}/images'
        headers = {
            'Authorization': f'Client-ID {self.client_id}'
        }
        response = self.make_request(
            'get',
            endpoint,
            headers=headers
        ).json()
        return response

    def AlbumImage(self, albumHash: str, imageHash:str) -> dict:
        """Get information about an image in an album, any additional actions found in Image Endpoint will also work.

        Args:
            albumHash (str): album hash
            imageHash (str): image hash

        Returns:
            dict:
        """        
        endpoint = f'{self.API}/3/album/{albumHash}/images/{imageHash}'
        headers = {
            'Authorization': f'Client-ID {self.client_id}'
        }
        response = self.make_request(
            'get',
            endpoint,
            headers=headers
        ).json()
        return response

    