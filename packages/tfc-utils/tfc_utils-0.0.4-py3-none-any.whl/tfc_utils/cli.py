import json

import typer
from terrasnek.api import TFC

from .terraform_cloud import get_workspace_output, get_workspace_outputs

app = typer.Typer()

tfc_token_opt = typer.Option(
    default=...,
    envvar=["TFE_TOKEN", "TFC_TOKEN"],
    help="Terraform Cloud access token",
)
tfc_organization_opt = typer.Option(
    default=...,
    envvar=["TFC_ORGANIZATION", "TFE_ORGANIZATION"],
    help="Terraform Cloud organization name",
)
tfc_workspace_opt = typer.Option(
    default=...,
    envvar=["TFC_WORKSPACE", "TFE_WORKSPACE"],
    help="Terraform Cloud workspace name",
)


@app.command(name="get-output")
def get_output_cli(
    output_name: str = typer.Argument(
        default=..., help="Name of your Terraform output, e.g. 'instance_ip_addr'"
    ),
    tfc_token: str = tfc_token_opt,
    tfc_organization: str = tfc_organization_opt,
    tfc_workspace: str = tfc_workspace_opt,
):
    """Get the value of a Terraform Cloud workspace output."""
    tfc = TFC(api_token=tfc_token)
    output = get_workspace_output(tfc, tfc_organization, tfc_workspace, output_name)
    typer.echo(output)


@app.command(name="get-outputs")
def get_outputs_cli(
    tfc_token: str = tfc_token_opt,
    tfc_organization: str = tfc_organization_opt,
    tfc_workspace: str = tfc_workspace_opt,
    prefix: str = typer.Option(
        default="",
        help="Optional prefix for filtering out outputs (case-sensitive)",
    ),
    to_upper: bool = typer.Option(
        default=False,
        help="Convert output names to uppercase",
    ),
):
    """Get outputs of a Terraform Cloud workspace as JSON-formatted key-values."""
    tfc = TFC(api_token=tfc_token)
    outputs_dict = get_workspace_outputs(
        tfc=tfc,
        organization_name=tfc_organization,
        workspace_name=tfc_workspace,
        prefix=prefix,
        preserve_case=not to_upper,
    )
    typer.echo(json.dumps(outputs_dict, separators=(",", ":")))


@app.callback()
def callback():
    """A CLI helper tool for Terraform Cloud."""
