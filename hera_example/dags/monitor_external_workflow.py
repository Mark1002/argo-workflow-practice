from hera.workflows import (
    CronWorkflow, Steps, DAG, WorkflowTemplate, script
)
from hera.workflows.models import WorkflowTemplateRef

from hera_example.service import WorkflowService
from hera_example.utils import monitor_external_workflow


@script(image="python:3.11-alpine")
def task(message: str):
    print(message)


@script(image="python:3.11-alpine")
def notify():
    print("Exiting workflow and sending notification.")


WORKFLOW_NAME = "monitor-external-workflow"
WORKFLOW_NAME_TEMPLATE = f"{WORKFLOW_NAME}-template"

cron_workflow = CronWorkflow(
    name=WORKFLOW_NAME,
    on_exit="exit-handler",
    entrypoint="main-dag",
    schedule="*/2 * * * *",
    workflow_template_ref=WorkflowTemplateRef(name=WORKFLOW_NAME_TEMPLATE),
    workflows_service=WorkflowService()
)
# Create a workflow template with the DAG definition
with WorkflowTemplate(
    name=WORKFLOW_NAME_TEMPLATE,
    entrypoint="main-dag",
) as workflow_template:
    with Steps(name="exit-handler") as exit_handler:
        notify(
            name="exit-handler",
            when="{{workflow.status}} != Succeeded"
        )
    with DAG(name="main-dag"):
        t1 = monitor_external_workflow(name="external-sensor", arguments={
            "external_workflow_name": "daily-dag"
        })
        t2 = task(name="end", arguments={"message": "Finish Task"})
        t1 >> t2  # type: ignore
    workflow_template.on_exit = exit_handler
    # Compile to workflowtemplate YAML and submit to argo workflow
    print(workflow_template.to_yaml())
    workflow_template.lint()
    workflow_template.update()
# Compile the CronWorkflow that references the WorkflowTemplate
# cron_workflow.lint()
# cron_workflow.create()
