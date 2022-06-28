import base64

import requests

DEBUG = False

try:
    secret_id = input(
        "\nEnter Vault Token (default: 1a3b7ea9-3cf0-68a7-52ea-02f035c72aec):") or "1a3b7ea9-3cf0-68a7-52ea-02f035c72aec"
    role_id = input(
        "\nEnter Vault Role ID (default: 0c397e02-bf02-937c-47df-38a78a27c95a):") or "0c397e02-bf02-937c-47df-38a78a27c95a"
    vault_url = input(
        "\nEnter Vault Server URL (default: https://10.45.100.129.nip.io/v1):") or "https://10.45.100.129.nip.io/v1"
    api_endpoint = input(
        "\nEnter Vault API endpoint (default: /calm/connection/ssh):") or "/calm/connection/ssh"
except Exception:
    secret_id = "@@{account.vault_token}@@"
    role_id = "@@{role_id}@@"
    vault_url = "@@{account.vault_url}@@"
    api_endpoint = "@@{api_endpoint}@@"


def check_for_errors(response, *_args, **_kwargs):
    """check_for_errors:
    handle API errors
    """
    try:
        response.raise_for_status()
        if DEBUG:
            print(response.text)
    except requests.exceptions.RequestException:
        print(" ERROR ".center(80, "-"))
        if DEBUG:
            print(response.text)
        raise


HOOKS = {
    'response': check_for_errors
}


headers = {
    "Content-Type": "application/json"
}


payload = {
    "role_id": role_id,
    "secret_id": secret_id
}

resp = requests.post(
    vault_url + "/auth/approle/login",
    json=payload,
    headers=headers,
    verify=False,
    hooks=HOOKS
)

headers["X-Vault-Token"] = resp.json()["auth"]["client_token"]

resp = requests.get(
    vault_url + api_endpoint,
    headers=headers,
    verify=False,
    hooks=HOOKS
)

username = resp.json()["data"]["username"]
# required to encode and decode after to support b64encode bytes in Python 3
secret = resp.json()["data"]["secret"].encode()

print("username={}".format(username))
print("secret={}".format(base64.b64encode(secret).decode()))
