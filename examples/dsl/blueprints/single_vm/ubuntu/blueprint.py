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


class SingleVmAhvResources(AhvVmResources):
    """Vm configuration"""

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
                }
            ]
        }
    )


class Profile1(VmProfile):

    # Profile variables
    DOCKER_INSTALL = CalmVariable.WithOptions.Predefined.string(
        options=["True", "False"],
        default="True",
        name="DOCKER_INSTALL",
        label="Enable Docker",
        is_mandatory=True,
        description="Enabling Docker lets you easily install containerized applications.")

    # VM Spec for Substrate
    provider_spec = ahv_vm(resources=SingleVmAhvResources,
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
            name="DOCKER_INSTALL",
            script=requests.get(
                SCRIPTS_URL + "/linux/docker/ubuntu_docker_install.sh").text
        )


class SampleSingleVmBluerint(VmBlueprint):
    """Simple blueprint Spec"""

    # Blueprint credentials
    credentials = [OS_CRED]

    # Blueprint profiles
    profiles = [Profile1]


class SingleVmBpMetadata(Metadata):

    project = Ref.Project(PROJECT_NAME)
    categories = {"TemplateType": "Vm"}
