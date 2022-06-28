import requests
import yaml
from calm.dsl.builtins import (AhvVmDisk, AhvVmGC, AhvVmNic, AhvVmResources,
                               CalmTask, CalmVariable, Metadata, Ref,
                               VmBlueprint, VmProfile, action, ahv_vm,
                               basic_cred, read_file, read_local_file,
                               readiness_probe, ref)

# Configuration
SCRIPTS_URL = "https://raw.githubusercontent.com/nutanixdev/calm-community/main/examples/tasks"

DSL_CONFIG = yaml.safe_load(read_file("config.yaml"))
IMAGE = DSL_CONFIG["AHV"]["IMAGES"]["DISK"]["DISK1"]

NETWORK = DSL_CONFIG["AHV"]["NETWORKS"]["NETWORK1"]
NETWORK_NAME = NETWORK["NAME"]

PROJECT = DSL_CONFIG["PROJECTS"]["PROJECT1"]
PROJECT_NAME = PROJECT["NAME"]


# Credentials
OS_USER = "nutanix"
OS_KEY = read_local_file(".tests/keys/linux")
OS_CRED = basic_cred(OS_USER, OS_KEY, name="OS_CRED", type="KEY", default=True)

PC_USER = "admin"
PC_PASSWORD = read_local_file(".tests/passwords/prism_central")
CRED_PC = basic_cred(PC_USER, PC_PASSWORD, name="CRED_PC",
                     type="PASSWORD", default=False)


class VaultAhvResources(AhvVmResources):
    """Vault configuration"""

    memory = 4
    vCPUs = 2
    cores_per_vCPU = 1

    disks = [
        AhvVmDisk.Disk.Scsi.cloneFromImageService(IMAGE["NAME"], bootable=True)
    ]

    nics = [AhvVmNic(NETWORK_NAME)]

    guest_customization = AhvVmGC.CloudInit(
        config={
            "hostname": "@@{name}@@",
            "users": [
                {
                    "name": "@@{OS_CRED.username}@@",
                    "ssh-authorized-keys": ["@@{OS_CRED.public_key}@@"],
                    "sudo": ["ALL=(ALL) NOPASSWD:ALL"],
                    "shell": "/bin/bash"
                }
            ]
        }
    )

    serial_ports = {0: False}


class Default(VmProfile):

    # Profile variables
    K3S_INSTALL = CalmVariable.Simple.string(
        value="True",
        name="K3S_INSTALL",
        label="Install K3s",
        is_hidden=True,
        description="Enabling K3s lets you easily install containerized applications.")

    VAULT_INSTALL = CalmVariable.WithOptions.Predefined.string(
        options=["True", "False"],
        default="True",
        name="VAULT_INSTALL",
        label="Install Vault",
        is_mandatory=True,
        description="Install Vault for secrets management.")

    VAULT_PRINT_KEYS = CalmVariable.WithOptions.Predefined.string(
        options=["True", "False"],
        default="False",
        name="VAULT_PRINT_KEYS",
        label="Print out Vault keys",
        is_mandatory=True,
        description="If true, Vault keys will be visible in Audit logs")

    DOCKER_HUB_USERNAME = CalmVariable.Simple.string("youruser", runtime=True)
    DOCKER_HUB_PASSWORD = CalmVariable.Simple.Secret(
        read_local_file(".tests/passwords/docker"), runtime=True)
    OS_DISK_SIZE = CalmVariable.Simple.int("20")
    NTNX_PC_IP = CalmVariable.Simple.string("127.0.0.1")

    # VM Spec for Substrate
    provider_spec = ahv_vm(resources=VaultAhvResources,
                           name="@@{calm_application_name}@@")

    # Readiness probe for substrate (disabled is set to false, for enabling check login)
    readiness_probe = readiness_probe(credential=ref(OS_CRED), disabled=False)

    # Only actions under Packages, Substrates and Profiles are allowed
    @action
    def __install__():
        CalmTask.Exec.escript(
            name="EXPAND_DISK",
            script=requests.get(
                SCRIPTS_URL + "/nutanix/prism_central/vm_disk_resize.py").text
        )
        CalmTask.Exec.ssh(
            name="K3S_INSTALL",
            script=requests.get(
                SCRIPTS_URL + "/linux/k3s/ubuntu_k3s_install.sh").text
        )
        CalmTask.Exec.ssh(
            name="HELM_INSTALL",
            script=requests.get(
                SCRIPTS_URL + "/linux/helm/ubuntu_helm_install.sh").text
        )
        CalmTask.SetVariable.ssh(
            name="VAULT_INSTALL",
            script=requests.get(
                SCRIPTS_URL + "/linux/vault/kubernetes_vault_install.sh").text,
            variables=["VAULT_HOST", "VAULT_UNSEAL_KEY", "VAULT_ROOT_TOKEN"]
        )


class SingleVaultNode(VmBlueprint):
    """[Vault](https://@@{DefaultService.VAULT_HOST}@@)"""

    # Blueprint credentials
    credentials = [OS_CRED, CRED_PC]

    # Blueprint profiles
    profiles = [Default]


class VaultMetadata(Metadata):

    project = Ref.Project(PROJECT_NAME)
    categories = {"TemplateType": "Vm"}
