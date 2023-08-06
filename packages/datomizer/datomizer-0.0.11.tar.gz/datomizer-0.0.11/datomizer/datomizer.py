import requests
from datomizer.helpers.authentication import authentication_helper
from datomizer.utils.general import ACCESS_TOKEN, REFRESH_TOKEN, AUTHORIZATION, BEARER_TOKEN, D_REALM


class Datomizer(object):
    domain: str
    realm: str
    access_token: str
    refresh_token: str
    auth_headers: dict

    def __init__(self, username: str, password: str):
        """Create authentication object for Datomize.

        Args:
            username: your username
            password: your password
        Returns:
            Datomizer Authentication object"""
        self.domain = authentication_helper.get_domain_by_username(username=username)
        self.realm = authentication_helper.get_realm_by_domain(domain=self.domain)
        token_response = authentication_helper.get_token(username=username, password=password,
                                                         domain=self.domain, realm=self.realm)
        self.config_token(token_response)

    def refresh_token_headers(self):
        token_response = authentication_helper.refresh_token(domain=self.domain, realm=self.realm,
                                                             token=self.refresh_token)
        self.config_token(token_response)

    def config_token(self, token_response):
        try:
            self.access_token = token_response[ACCESS_TOKEN]
            self.refresh_token = token_response[REFRESH_TOKEN]
            self.auth_headers = {AUTHORIZATION: BEARER_TOKEN % self.access_token, D_REALM: self.realm}
        except Exception as ex:
            print(f"token res:{token_response}")
            raise ex

    def get_response_json(self, method: requests.Request, url: str, headers: {} = {}, url_params: [] = [], **kwargs):
        return self.api_request(method=method, url=url, headers=headers, url_params=url_params, **kwargs).json()

    def api_request(self, method: requests.Request,
                    url: str, headers: {} = {}, url_params: [] = [], **kwargs) -> requests.Response:
        kwargs['url'] = url % (self.domain, *url_params)

        headers.update(self.auth_headers)
        kwargs['headers'] = headers
        response: requests.Response = method(**kwargs)

        # refresh token and retry on unauthorized or forbidden request
        if response.status_code in [401, 403]:
            self.refresh_token_headers()
            headers.update(self.auth_headers)
            response = method(**kwargs)

        self.validate_response(response)
        return response

    @staticmethod
    def validate_response(response: requests.Response, not_valid_message: str = "Status is not OK"):
        if response.status_code != 200:
            print(response.status_code)
            print(response.url)
            print(response.content)
            raise Exception(not_valid_message)
