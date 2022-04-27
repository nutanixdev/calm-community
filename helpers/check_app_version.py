import requests

# CURRENT_VERSION = "1.0"
CURRENT_VERSION = "@@{ntnx_calm_importer_current_version}@@"
METADATA_URL = "@@{ntnx_calm_catalog_metadata_url}@@"


r = requests.get(METADATA_URL)

if r.ok:
    resp = r.json()
    latest_version = resp["version"]
else:
    print("Get Calm importer version request failed", r.text)
    exit(1)


if CURRENT_VERSION != latest_version:
    results = [
        "Skip update",
        "Install update {}".format(latest_version)

    ]
    print(",".join(results))
else:
    print("Latest version already installed")