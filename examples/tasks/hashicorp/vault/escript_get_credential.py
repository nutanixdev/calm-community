"""
----------------------------------------------------------------------------------------------------------------------------------
Copyright (c) 2022 Nutanix Inc. All rights reserved.
Licensed under the Apache License 2.0. See https://github.com/nutanixdev/calm-community/blob/main/LICENSE for license information.

Author: jose.gomez@nutanix.com
----------------------------------------------------------------------------------------------------------------------------------

This script allows the user to retrieve secrets from HashiCorp Vault using Nutanix Self-Service Credential Provider wiht eScript,
or alternatively using a Python 2/3 environment. It is assumed that AppRole authentication is in use.

When using a Python environment, this script requires that `requests` be installed within it.

This script requires the values of:

    * secret_id - SecretID is a credential that is required by default for any login (via secret_id). In Nutanix Self-Service this
                  variable is expanded with the macro value @@{account.vault_token}@@

    * role_id - RoleID is an identifier that selects the AppRole against which the other credentials are evaluated. When
                authenticating against this auth method's login endpoint, the RoleID is a required argument (via role_id). In
                Nutanix Self-Service this variable is expanded with the macro value @@{role_id}@@

    * vault_uri - This is the Vault server URL including the API version (ex.: https://my.vault.server/v1). In Nutanix
                  Self-Service this variable is expanded with the macro value @@{account.vault_uri}@@

    * vault_path - This is the Secrets Engine path for the desired secret to retrieve (ex.: /kv/foo/bar). In Nutanix Self-Service
                   this variable is expanded with the macro value @@{account.vault_uri}@@

This script prints out the k/v from the given `vault_path`. The Set Variable task using this eScript in Nutanix Self-Service
Credential Provider needs any required `Output` macro to be named after the JSON key printed out by this script.

(Optional) For debugging purposes, set `DEBUG = True`
"""

import base64

import requests

DEBUG = False

try:
    secret_id = input(
        "\nEnter Vault Token (default: 1a3b7ea9-3cf0-68a7-52ea-02f035c72aec):") or "1a3b7ea9-3cf0-68a7-52ea-02f035c72aec"
    role_id = input(
        "\nEnter Vault Role ID (default: 0c397e02-bf02-937c-47df-38a78a27c95a):") or "0c397e02-bf02-937c-47df-38a78a27c95a"
    vault_uri = input(
        "\nEnter Vault Server URL (default: https://10.45.100.129.nip.io/v1):") or "https://10.45.100.129.nip.io/v1"
    vault_path = input(
        "\nEnter Vault API endpoint (default: /calm/connection/ssh):") or "/calm/connection/ssh"
except Exception:
    secret_id = "@@{account.vault_token}@@"
    role_id = "@@{role_id}@@"
    vault_uri = "@@{account.vault_uri}@@"
    vault_path = "@@{path}@@"


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
    vault_uri + "/auth/approle/login",
    json=payload,
    headers=headers,
    verify=False,
    hooks=HOOKS
)

headers["X-Vault-Token"] = resp.json()["auth"]["client_token"]

resp = requests.get(
    vault_uri + vault_path,
    headers=headers,
    verify=False,
    hooks=HOOKS
)


for k, v in resp.json()["data"].items():

    # Multiline string values require to be encoded for Nutanix Self-Service Credential Provider consumption.
    if "\n" in v:

        # required to encode and decode later to support b64encode bytes in standalone Python 3 testing
        v = base64.b64encode(v.encode()).decode()

    print("{0}={1}".format(k, v))
