import os
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import click
import inquirer
import paramiko

from openapi_client import CliWorkspaceBackupCreateAPIInput
from openapi_client.models import (
    InfluxdbWorkloadLog,
    OrmWorkspacePort,
    ProtoVolumeMountRequests,
    ResponseWorkspaceDetail,
    ResponseWorkspaceList,
    WorkspaceCreateAPIInput,
)
from vessl import vessl_api
from vessl.kernel_cluster import list_cluster_nodes, read_cluster
from vessl.kernel_resource_spec import (
    _configure_custom_kernel_resource_spec,
    read_kernel_resource_spec,
)
from vessl.organization import _get_organization_name
from vessl.util.common import parse_time_to_ago
from vessl.util.config import VesslConfigLoader
from vessl.util.constant import SSH_CONFIG_FORMAT, SSH_CONFIG_PATH, TEMP_DIR
from vessl.util.exception import InvalidWorkspaceError, VesslException
from vessl.util.random import random_string
from vessl.util.zipper import Zipper
from vessl.volume import (
    _configure_volume_mount_request_datasets,
    _configure_volume_mount_request_local_files,
    _configure_volume_mount_requests,
    copy_volume_file,
)


def read_workspace(workspace_id: int, **kwargs) -> ResponseWorkspaceDetail:
    """Read workspace

    Keyword args:
        organization_name (str): override default organization
    """
    return vessl_api.workspace_read_api(
        workspace_id=workspace_id, organization_name=_get_organization_name(**kwargs)
    )


def list_workspaces(
    cluster_id: int = None, statuses: List[str] = None, mine: bool = True, **kwargs
) -> List[ResponseWorkspaceList]:
    """List workspaces

    Keyword args:
        organization_name (str): override default organization
    """
    statuses = (
        [",".join(statuses)] if statuses else None
    )  # since openapi-generator uses repeating params instead of commas
    return vessl_api.workspace_list_api(
        organization_name=_get_organization_name(**kwargs),
        cluster=cluster_id,
        mine=mine,
        statuses=statuses,
    ).results


def create_workspace(
    name: str,
    cluster_name: str,
    cluster_node_names: List[str] = None,
    kernel_resource_spec_name: str = None,
    processor_type: str = None,
    cpu_limit: float = None,
    memory_limit: str = None,
    gpu_type: str = None,
    gpu_limit: int = None,
    kernel_image_url: str = None,
    max_hours: int = 24,
    dataset_mounts: List[str] = None,
    local_files: List[str] = None,
    root_volume_size: str = "100Gi",
    ports: List[Dict[str, Any]] = None,
    init_script: str = None,
    **kwargs,
) -> ResponseWorkspaceDetail:
    """Create workspace

    Args:
        ports (List[Dict[str, Any]]):
            Element keys are 'expose_type' (str), 'port' (int), and 'name' (dict).

    Keyword args:
        organization_name (str): override default organization
    """
    cluster = read_cluster(cluster_name)
    cluster_node_ids = (
        [
            n.id
            for n in list_cluster_nodes(cluster.id, **kwargs)
            if n.name in cluster_node_names
        ]
        if cluster_node_names is not None
        else None
    )

    kernel_resource_spec = kernel_resource_spec_id = None
    if kernel_resource_spec_name:
        kernel_resource_spec_id = read_kernel_resource_spec(
            cluster.id,
            kernel_resource_spec_name,
        ).id
    else:
        kernel_resource_spec = _configure_custom_kernel_resource_spec(
            processor_type,
            cpu_limit,
            memory_limit,
            gpu_type,
            gpu_limit,
        )

    all_ports = [
        OrmWorkspacePort(expose_type="http", port=8888, name="jupyter"),
        OrmWorkspacePort(expose_type="tcp", port=22, name="ssh"),
    ]
    if ports is not None:
        for p in ports:
            all_ports.append(
                OrmWorkspacePort(
                    expose_type=p.get("expose_type"),
                    port=p.get("port"),
                    name=p.get("name"),
                )
            )

    requests = []
    if dataset_mounts is not None:
        requests.extend(
            _configure_volume_mount_request_datasets(
                dataset_mounts, should_add_project_datasets=False, **kwargs
            )
        )
    if local_files:
        requests.extend(
            _configure_volume_mount_request_local_files(local_files, **kwargs)
        )

    volume_mount_requests = ProtoVolumeMountRequests(
        root_volume_size=root_volume_size,
        requests=requests,
    )

    return vessl_api.workspace_create_api(
        organization_name=_get_organization_name(**kwargs),
        workspace_create_api_input=WorkspaceCreateAPIInput(
            cluster_id=cluster.id,
            cluster_node_ids=cluster_node_ids,
            resource_spec=kernel_resource_spec,
            resource_spec_id=kernel_resource_spec_id,
            image_url=kernel_image_url,
            name=name,
            max_hours=max_hours,
            ports=all_ports,
            volumes=volume_mount_requests,
            init_script=init_script,
        ),
    )


def list_workspace_logs(
    workspace_id: int,
    tail: int = 200,
    **kwargs,
) -> List[InfluxdbWorkloadLog]:
    """List experiment logs

    Args:
        tail (int): number of lines to display from the end. Display all if -1.

    Keyword args:
        organization_name (str): override default organization
    """
    if tail == -1:
        tail = None

    return vessl_api.workspace_logs_api(
        workspace_id=workspace_id,
        organization_name=_get_organization_name(**kwargs),
        limit=tail,
    ).logs


def start_workspace(workspace_id: int, **kwargs) -> ResponseWorkspaceDetail:
    return vessl_api.workspace_start_api(
        organization_name=_get_organization_name(**kwargs), workspace_id=workspace_id
    )


def stop_workspace(workspace_id: int, **kwargs) -> ResponseWorkspaceDetail:
    return vessl_api.workspace_stop_api(
        organization_name=_get_organization_name(**kwargs), workspace_id=workspace_id
    )


def terminate_workspace(workspace_id: int, **kwargs) -> ResponseWorkspaceDetail:
    return vessl_api.workspace_terminate_api(
        organization_name=_get_organization_name(**kwargs), workspace_id=workspace_id
    )


def backup_workspace() -> None:
    """Backup the home directory of the workspace

    Should only be called inside a workspace.
    """

    workspace_id = VesslConfigLoader().workspace
    if workspace_id is None:
        raise InvalidWorkspaceError("Can only be called within a workspace.")

    workspace = read_workspace(workspace_id)

    filename = f'workspace-backup-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}-{random_string()}.zip'
    full_path = os.path.join(TEMP_DIR, filename)
    home_dir = str(Path.home())
    zipper = Zipper(full_path, "w")
    zipper.zipdir(home_dir, include_dotfiles=True)
    zipper.close()
    size = zipper.size()
    print(f"Backup file size: {size}")
    if size > 15 * 1024 * 1024 * 1024:
        zipper.remove()
        raise VesslException(f"{home_dir} is too large to backup.")

    print("Uploading the backup file...")
    copy_volume_file(
        source_volume_id=None,
        source_path=full_path,
        dest_volume_id=workspace.backup_volume_id,
        dest_path=filename,
    )
    zipper.remove()

    vessl_api.cli_workspace_backup_create_api(
        workspace_id=workspace_id,
        cli_workspace_backup_create_api_input=CliWorkspaceBackupCreateAPIInput(
            filename=filename,
        ),
    )


def restore_workspace(workspace_id: int = None) -> None:
    """Restore the home directory from the previous backup

    Should only be called inside a workspace.
    """

    if workspace_id is None:
        workspace_id = VesslConfigLoader().workspace
        if workspace_id is None:
            raise InvalidWorkspaceError("Can only be called within a workspace.")

        workspace_list = list_workspaces(mine=True)
        backup_workspaces = [w for w in workspace_list if w.last_backup is not None]
        if len(backup_workspaces) == 0:
            raise click.ClickException("Available workspace backup not found.")

        workspace = inquirer.prompt(
            [
                inquirer.List(
                    "question",
                    message="Select workspace",
                    choices=[
                        (
                            f"{w.name} (backup created {parse_time_to_ago(w.last_backup.created_dt)})",
                            w,
                        )
                        for w in backup_workspaces
                    ],
                )
            ],
            raise_keyboard_interrupt=True,
        ).get("question")
    else:
        workspace = read_workspace(workspace_id=workspace_id)
        if workspace.last_backup is None:
            raise click.ClickException("This workspace does not have any backup.")

    dest_path = os.path.join(TEMP_DIR, "workspace-backup.zip")
    print("Downloading the backup file...")
    copy_volume_file(
        source_volume_id=workspace.backup_volume_id,
        source_path=workspace.last_backup.filename,
        dest_volume_id=None,
        dest_path=dest_path,
    )

    zipper = Zipper(dest_path, "r")
    size = zipper.size()
    print(f"Backup file size: {size}")
    extract_path = str(Path.home())
    if size > 15 * 1024 * 1024 * 1024:
        extract_path = os.path.join(TEMP_DIR, "workspace-backup")
    print("Extracting...")
    zipper.extractall(extract_path)
    if size > 15 * 1024 * 1024 * 1024:
        print(
            f"Restored to {extract_path} since the size of the backup file is larger than 15Gi."
        )
    zipper.close()
    zipper.remove()


def connect_workspace_ssh(private_key_path: str, **kwargs) -> None:
    """Connect to a running workspace via SSH

    Keyword args:
        organization_name (str): override default organization
    """
    running_workspaces = list_workspaces(statuses=["running"], mine=True)
    if len(running_workspaces) == 0:
        raise click.ClickException("There is no running workspace.")

    if len(running_workspaces) == 1:
        workspace = running_workspaces[0]
    else:
        workspace = inquirer.prompt(
            [
                inquirer.List(
                    "question",
                    message="Select workspace",
                    choices=[
                        (f"{w.name} (created {parse_time_to_ago(w.created_dt)})", w)
                        for w in running_workspaces
                    ],
                )
            ],
            raise_keyboard_interrupt=True,
        ).get("question")

    ssh_endpoint = urllib.parse.urlparse(workspace.endpoints.ssh.endpoint)
    ssh_private_key_option = f" -i {private_key_path}" if private_key_path else ""
    os.system(
        f"ssh -p {ssh_endpoint.port}{ssh_private_key_option} vessl@{ssh_endpoint.hostname}"
    )


def update_vscode_remote_ssh(private_key_path: str) -> None:
    """Update .ssh/config file for VSCode Remote-SSH plugin"""
    running_workspaces = list_workspaces(statuses=["running"], mine=True)
    if len(running_workspaces) == 0:
        raise click.ClickException("There is no running workspace.")

    ssh_config = paramiko.SSHConfig()
    try:
        with open(SSH_CONFIG_PATH, "r") as fr:
            ssh_config.parse(fr)
    except FileNotFoundError:
        pass

    host_set = ssh_config.get_hostnames()
    for workspace in running_workspaces:
        host = f"{workspace.name}-{int(workspace.created_dt.timestamp())}"
        if host in host_set:
            continue

        ssh_endpoint = urllib.parse.urlparse(workspace.endpoints.ssh.endpoint)

        config_value = SSH_CONFIG_FORMAT.format(
            host=host,
            hostname=ssh_endpoint.hostname,
            port=ssh_endpoint.port,
        )
        if private_key_path:
            config_value += f"    IdentityFile {private_key_path}\n"

        with open(SSH_CONFIG_PATH, "a") as f:
            f.write(config_value)
