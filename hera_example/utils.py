import requests
from hera.workflows import script


@script(image="argo-workflow-practice:v0.1.0")
def monitor_external_workflow(external_workflow_name: str):
    """Monitor external workflow using Hera's native capabilities"""
    from hera.workflows import CronWorkflow
    from hera_example.service import WorkflowService

    # Create a reference to the external workflow
    external_workflow = CronWorkflow(
        name=external_workflow_name,
        workflows_service=WorkflowService(
            # host="http://argo-server.argo.svc.cluster.local:2746",
            # namespace="argo",
        )
    )
    external_workflow.wait(poll_interval=30)
    print(f"External workflow {external_workflow_name} completed successfully") # noqa


def get_current_running_workflow_name(
    cron_workflow_name: str,
    argo_server_url: str,
    namespace: str = "default",
) -> str:
    argo_api = f"{argo_server_url}/api/v1/workflows/{namespace}"
    # Label selector filters child workflows created by the CronWorkflow
    params = {
        "labelSelector": f"workflows.argoproj.io/cron-workflow={cron_workflow_name}" # noqa
    }

    response = requests.get(argo_api, params=params)
    response.raise_for_status()
    workflows = response.json().get("items", [])

    # Filter workflows with status.phase == 'Running'
    running_workflows = [
        wf for wf in workflows
        if wf.get("status", {}).get("phase") == "Running"
    ]

    if not running_workflows:
        raise RuntimeError(f"No running workflows found for CronWorkflow {cron_workflow_name}") # noqa

    # Sort running workflows by creationTimestamp descending to get the latest
    running_workflows.sort(
        key=lambda w: w["metadata"]["creationTimestamp"],
        reverse=True
    )

    latest_running_wf_name = running_workflows[0]["metadata"]["name"]
    return latest_running_wf_name


if __name__ == "__main__":
    # monitor_external_workflow(external_workflow_name="daily-dag")
    name = get_current_running_workflow_name(
        cron_workflow_name="daily-dag",
        argo_server_url="http://127.0.0.1:2746",
        namespace="argo"
    )
    print(name)
