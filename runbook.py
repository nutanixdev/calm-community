from calm.dsl.runbooks import runbook, runbook_json
from calm.dsl.runbooks import RunbookTask as Task, RunbookVariable as Variable
from calm.dsl.builtins import CalmTask

@runbook
def DslCommunityRunbook():

    ntnx_calm_catalog_base_url = Variable.Simple.string(
        "https://raw.githubusercontent.com/nutanixdev/calm-community/main",
        is_hidden=True,
        description="main branch URL raw path"
    )

    ntnx_calm_catalog_example_folder = Variable.Simple.string(
        "examples",
        is_hidden=True,
        description="Folder with all the examples"
    )

    ntnx_calm_catalog_metadata_filename = Variable.Simple.string(
        "metadata.json",
        is_hidden=True,
        description="content library metadata (what Calm Importer reads for presenting options to the user)"
    )

    ntnx_calm_catalog_metadata_url = Variable.Simple.string(
        "/".join(["@@{ntnx_calm_catalog_base_url}@@","@@{ntnx_calm_catalog_metadata_filename}@@"]),
        # is_hidden=True,
        label="Calm Importer - metadata URL (for reference)"
    )

    ntnx_calm_catalog_examples_url = Variable.Simple.string(
        "/".join(["@@{ntnx_calm_catalog_base_url}@@","@@{ntnx_calm_catalog_example_folder}@@"]),
        # is_hidden=True,
        label="Calm Importer - examples folder URL (for reference)"
    )

    ntnx_calm_importer_current_version = Variable.Simple.string(
        "1.0",
        is_hidden=True,
        description="DO NOT CHANGE. Used for future Calm Importer upgrades"
    )

    ntnx_calm_import_to_project = Variable.Simple.string(
        "default",
        is_mandatory=True,
        runtime=True,
        label="Self-Service Project",
        description="In what project the content will be imported to"
    )

    ntnx_calm_check_version = Variable.WithOptions.FromTask(
        CalmTask.Exec.escript(
            filename="lib/check_app_version.py"
        ),
        is_mandatory=True,
        label="Calm Importer - upgrade available?"
    )

    ntnx_calm_object_kinds = Variable.WithOptions.FromTask(
        CalmTask.HTTP.get(
            "@@{ntnx_calm_catalog_metadata_url}@@",
            content_type="application/json",
            verify=True,
            status_mapping={200: True},
            response_paths={"ntnx_calm_object_kinds": "$.referenceKinds[*]"},
        ),
        is_mandatory=True,
        label="Kind of Self-Service content to import"
    )

    ntnx_calm_object_kind = Variable.WithOptions.FromTask(
        CalmTask.HTTP.get(
            "@@{ntnx_calm_catalog_metadata_url}@@",
            content_type="application/json",
            verify=True,
            status_mapping={200: True},
            response_paths={"ntnx_calm_object_kind": "$.entities[?(@.kind == '@@{ntnx_calm_object_kinds}@@')].metadata.name"},
        ),
        is_mandatory=True,
        label="Content name"
    )

    ntnx_calm_object_uri = Variable.WithOptions.FromTask(
        CalmTask.HTTP.get(
            "@@{ntnx_calm_catalog_metadata_url}@@",
            content_type="application/json",
            verify=True,
            status_mapping={200: True},
            response_paths={"ntnx_calm_object_uri": "$.entities[?(@.kind == \"@@{ntnx_calm_object_kinds}@@\" && @.metadata.name == \"@@{ntnx_calm_object_kind}@@\")].uri"},
        ),
        is_mandatory=True,
        label="Content direct link (for reference)"
    )

    ntnx_calm_object_overwrite = Variable.WithOptions.Predefined(
        ["True", "False"],
        default="False",
        is_mandatory=True,
        runtime=True,
        label="Overwrite existing content",
        description="If there is already content with the same name, it can be overwritten or create an additional version (appended epoch timestamp)"
    )

    Task.Delay(1, name="Delay")

    Task.Exec.escript(
        filename="lib/generate_content.py",
        name="Generate content"
    )

def main():
    print(runbook_json(DslCommunityRunbook))


if __name__ == "__main__":
    main()