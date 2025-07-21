import requests
from hera.workflows import script


@script(image="argo-workflow-practice:v0.1.0")
def monitor_external_workflow(cron_workflow: str, host: str, namespace: str):
    """Monitor latest run external workflow created by CronWorkflow."""
    from hera.workflows import Workflow
    from hera_example.service import WorkflowService
    from hera_example.utils import _get_current_running_workflow_name

    current_workflow_name = _get_current_running_workflow_name(
        cron_workflow_name=cron_workflow,
        argo_server_url=host,
        namespace=namespace
    )
    # Create a reference to the external workflow
    external_workflow = Workflow(
        name=current_workflow_name,
        workflows_service=WorkflowService(host=host, namespace=namespace)
    )
    external_workflow.wait(poll_interval=30)
    print(f"External workflow {current_workflow_name} completed successfully") # noqa


def _get_current_running_workflow_name(
    cron_workflow_name: str,
    argo_server_url: str,
    namespace: str = "default",
) -> str:
    argo_api = f"{argo_server_url}/api/v1/workflows/{namespace}/{cron_workflow_name}" # noqa

    response = requests.get(argo_api)
    response.raise_for_status()
    running_workflows: list[dict] = response.json()["status"]["active"]

    if not running_workflows:
        raise RuntimeError(f"No running workflows found for CronWorkflow {cron_workflow_name}") # noqa

    # Sort running workflows by timestamp descending to get the latest
    running_workflows.sort(
        key=lambda w: w["name"].split("-")[-1],
        reverse=True
    )

    latest_running_wf_name = running_workflows[0]["name"]
    return latest_running_wf_name


if __name__ == "__main__":
    # monitor_external_workflow(external_workflow_name="daily-dag")
    name = _get_current_running_workflow_name(
        cron_workflow_name="hello-world-etl",
        argo_server_url="http://127.0.0.1:2746",
        namespace="argo"
    )
    print(name)
