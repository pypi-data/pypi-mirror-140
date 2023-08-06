import requests


class Core(object):
    def make_request(
        self,
        method: str,
        url: str,
        *args,
        **kwargs
    ) -> requests.Response:
        """Make a request

        Args:
            method (str): request method.
            url (str): request url.

        Returns:
            requests.Response: response of request.
        """
             
        response = requests.request(
            method.upper(),
            url,
            *args,
            **kwargs
        )
        return response
