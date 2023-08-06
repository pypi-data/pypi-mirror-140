from typing import Union

import requests

from .Authenticate import Authenticate


class Image(Authenticate):
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

    def Image(
        self,
        imageHash: str
    ) -> requests.Response:
        """Get information about an image.

        Args:
            imageHash (str): image hash

        Returns:
            dict: response of request
        """
        endpoint = f'{self.API}/3/image/{imageHash}'
        headers = {
            'Authorization': 'Client-ID bbb05a47ec9b35e'
        }
        response = self.make_request(
            'get',
            endpoint,
            headers=headers,
        )
        return response

    def ImageUpload(
            self,
            file: Union[str, bytes],
            type: str,
            **kwargs
    ) -> dict:
        """Upload a new image or video.

        Args:
            file (Union[str, bytes]): file path, file bytes or file url.
            type (str): file, base64 or url.
            album (str, optional): upload image to the album. Defaults to None.
            name (str, optional): image file name.
            title (str, optional): image title.
            description (str, optional): image description.
            auth (bool, optional): if upload to hidden album, need to set True of auth. Default to False.
        Return: 
            dict:
        """
        endpoint = f'{self.API}/3/upload'
        headers = {'Authorization': f'Client-ID {self.client_id}'}
        payload = {
            'type': type
        }

        (headers.update({'Authorization': f'Bearer {self.access_token}'})
            if kwargs.get('auth', False) == True else ...)

        params = ['album', 'name', 'title', 'description']
        for param in params:
            (payload.update({param: kwargs.get(param, '')})
                if kwargs.get(param, '') != '' else ...)

        (payload.update({'image': file})
            if type == 'url' or isinstance(file, str) else ...)

        response = self.make_request(
            'post',
            endpoint,
            headers=headers,
            data=payload
        ).json()
        return response

    def ImageDelete(
        self,
        imageHash: str,
        auth: bool = False
    ) -> dict:
        """Deletes an image.

        Args:
            imageHash (str): image hash (auth is True) or image delete hash (auth is False).
            auth (bool, optional): auth. Defaults to False.
        Return: 
            dict:
        """
        endpoint = f'{self.API}/3/image/{imageHash}'
        headers = {'Authorization': f'Client-ID {self.client_id}'}
        (headers.update({'Authorization': f'Bearer {self.access_token}'})
            if auth == True else ...)

        response = self.make_request(
            'delete',
            endpoint,
            headers=headers,
        ).json()
        return response

    def ImageUpdate(
        self,
        imageHash: str,
        auth: bool = False,
        **kwargs
    ) -> dict:
        """Updates the title or description of an image.

        Args:
            imageHash (str): image hash (auth is True) or image delete hash (auth is False).
            auth (bool, optional): auth. Defaults to False.
        Return: 
            dict:
        """
        endpoint = f'{self.API}/3/image/{imageHash}'
        headers = {'Authorization': f'Client-ID {self.client_id}'}
        params = ['title', 'description']
        payload = {}
        (headers.update({'Authorization': f'Bearer {self.access_token}'})
            if auth == True else ...)
        for param in params:
            (payload.update({param: kwargs.get(param, '')})
                if kwargs.get(param, '') != '' else ...)
        response = self.make_request(
            'post',
            endpoint,
            headers=headers,
            data=payload,
        ).json()
        return response
