import requests
from datomizer.utils import constants


def get_domain_by_username(username: str) -> str:
    response = requests.get(constants.ONBOARDING_GET_USER_DOMAIN_DEFAULT % username)
    return response.url.replace("https://", "").split('/')[0]


def get_realm_by_domain(domain: str) -> str:
    response = requests.get(constants.IDENTITY_GET_REALM_BY_DOMAIN % domain)
    return response.text


def get_token(username, password, realm, domain):
    client_props = {
        "client_id": "direct",
        "grant_type": "password",
        "username": username,
        "password": password
    }

    response = requests.post(constants.KEYCLOAK_GET_TOKEN_URL % (domain, realm), client_props)
    return response.json()


def refresh_token(realm, domain, token):
    client_props = {
        "client_id": "direct",
        "grant_type": "refresh_token",
        "refresh_token": token
    }

    response = requests.post(constants.KEYCLOAK_GET_TOKEN_URL % (domain, realm), client_props)
    return response.json()


def base_config_api_client(realm, domain, username, password):
    token = get_token(realm, domain, username, password)
    # token = get_realm_admin_token(realm, domain) if is_admin_user else get_realm_user_token(realm, domain)
    # configuration = swagger_client.Configuration()
    # configuration.api_key_prefix['Authorization'] = 'Bearer'
    # configuration.api_key['Authorization'] = token['access_token']
    #
    # configuration.api_key['d-realm'] = realm
    # swagger_client.api_client = swagger_client.ApiClient(configuration)
    return token['refresh_token']


def config_api_client(realm, domain, username, password):
    base_config_api_client(realm, domain, username, password)
