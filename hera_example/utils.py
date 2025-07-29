import requests
import time

from typing import Optional, Tuple
from datetime import datetime, timedelta, timezone

from hera.workflows import Workflow
from hera_example.service import WorkflowService
from hera.workflows import script


def _get_current_running_workflow(
    cron_workflow_name: str,
    argo_server_url: str,
    namespace: str = "default",
) -> Tuple[Optional[str], Optional[datetime]]:
    last_scheduled_time: Optional[datetime] = None
    latest_running_wf_name: Optional[str] = None

    argo_api = f"{argo_server_url}/api/v1/cron-workflows/{namespace}/{cron_workflow_name}" # noqa

    response = requests.get(argo_api)
    if response.status_code == 404:
        print(f"CronWorkflow {cron_workflow_name} not found at {argo_api}")
        return None, None

    response.raise_for_status()
    workflow_status = response.json()["status"]
    running_workflows: Optional[list[dict]] = workflow_status["active"]
    time_str: Optional[str] = workflow_status["lastScheduledTime"]

    if time_str:
        last_scheduled_time = datetime.fromisoformat(
            time_str.replace("Z", "+00:00")
        )

    if running_workflows:
        # Sort running workflows by timestamp descending to get the latest
        running_workflows.sort(
            key=lambda w: w["name"].split("-")[-1],
            reverse=True
        )
        latest_running_wf_name = running_workflows[0]["name"]

    return latest_running_wf_name, last_scheduled_time


def _monitor_external_workflow(
    cron_workflow: str,
    host: str,
    namespace: str,
    poll_interval: int,
    wait_timeout: int,
    max_schedule_lag: int
):
    """Monitor latest run external workflow created by CronWorkflow."""

    start_time = datetime.now(timezone.utc)

    while True:
        elapsed_time = datetime.now(timezone.utc) - start_time
        if elapsed_time > timedelta(seconds=wait_timeout):
            raise TimeoutError(
                f"Timeout after {wait_timeout} seconds waiting for CronWorkflow {cron_workflow} to start a new run."
            )
        current_workflow_name, last_scheduled_time = _get_current_running_workflow(
            cron_workflow_name=cron_workflow,
            argo_server_url=host,
            namespace=namespace
        )
        if current_workflow_name:
            print(f"Found current running workflow: {current_workflow_name}")
            break
        if last_scheduled_time and (start_time - last_scheduled_time) <= timedelta(seconds=max_schedule_lag):
            current_workflow_name = f"{cron_workflow}-{int(last_scheduled_time.timestamp())}"
            print(f"Found last workflow name in time range: {current_workflow_name}") # noqa
            break
        print(f"Waiting for CronWorkflow {cron_workflow} to start a new run...")
        time.sleep(poll_interval)
    # Create a reference to the external workflow
    external_workflow = Workflow(
        name=current_workflow_name,
        workflows_service=WorkflowService(host=host, namespace=namespace)
    )
    external_workflow.wait(poll_interval=poll_interval)
    print(f"External workflow {current_workflow_name} completed successfully") # noqa


@script(image="argo-workflow-practice:v0.1.0")
def monitor_external_workflow(
    cron_workflow: str,
    host: str,
    namespace: str,
    poll_interval: int,
    wait_timeout: int,
    max_schedule_lag: int
):
    from hera_example.utils import _monitor_external_workflow
    _monitor_external_workflow(
        cron_workflow=cron_workflow,
        host=host,
        namespace=namespace,
        poll_interval=poll_interval,
        wait_timeout=wait_timeout,
        max_schedule_lag=max_schedule_lag
    )


if __name__ == "__main__":
    monitor_external_workflow(
        cron_workflow="hello-world-etl",
        host="http://127.0.0.1:2746",
        namespace="argo",
        poll_interval=10,
        wait_timeout=3600,
        max_schedule_lag=300
    )
