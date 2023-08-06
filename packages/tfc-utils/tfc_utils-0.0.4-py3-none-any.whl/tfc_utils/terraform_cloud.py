import json
from typing import Dict

from terrasnek.api import TFC


def get_workspace_output(
    tfc: TFC,
    organization_name: str,
    workspace_name: str,
    output_name: str,
) -> str:
    tfc.set_org(org_name=organization_name)
    response = list_current_state_version_outputs(tfc, workspace_name)
    for output in response["data"]:
        attrs = output["attributes"]
        if attrs["name"] == output_name:
            value = attrs["value"]
            if isinstance(value, str):
                return value
            return json.dumps(value)

    raise LookupError(
        f"Failed to find output in workspace: {organization_name}/{workspace_name}/{output_name}"
    )


def get_workspace_outputs(
    tfc: TFC,
    organization_name: str,
    workspace_name: str,
    prefix: str,
    preserve_case: bool = False,
) -> Dict[str, str]:
    tfc.set_org(org_name=organization_name)
    response = list_current_state_version_outputs(tfc, workspace_name)
    outputs_dict: Dict[str, str] = {}
    for output in response["data"]:
        attrs = output["attributes"]
        output_name: str = attrs["name"]
        if output_name.startswith(prefix):
            if not preserve_case:
                output_name = output_name.upper()
            value = attrs["value"]
            if not isinstance(value, str):
                value = json.dumps(value)
            outputs_dict[output_name] = value
    return outputs_dict


def list_current_state_version_outputs(tfc: TFC, workspace_name: str):
    response = tfc.workspaces.show(workspace_name=workspace_name)
    current_state_version = response["data"]["relationships"]["current-state-version"]
    current_state_version_id = current_state_version["data"]["id"]
    response = tfc.state_versions.list_state_version_outputs(current_state_version_id)
    return response
