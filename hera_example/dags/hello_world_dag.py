from hera.workflows import (
    CronWorkflow, Steps, DAG, WorkflowTemplate, script
)
from hera.workflows.models import WorkflowTemplateRef

from hera_example.service import WorkflowService


@script(image="python:3.11-alpine")
def task(message: str):
    if message == "C":
        raise ValueError("Simulating a failure in task C")
    print(message)


@script(image="python:3.11-alpine")
def notify():
    print("Exiting workflow and sending notification.")


cron_workflow = CronWorkflow(
    name="hello-world-etl",
    on_exit="exit-handler",
    entrypoint="hello-dag",
    schedule="*/2 * * * *",
    workflow_template_ref=WorkflowTemplateRef(name="hello-world-dag-template"),
    workflows_service=WorkflowService()
)
# Create a workflow template with the DAG definition
with WorkflowTemplate(
    name="hello-world-dag-template",
    entrypoint="hello-dag",
) as workflow_template:
    with Steps(name="exit-handler") as exit_handler:
        notify(
            name="exit-handler",
            when="{{workflow.status}} != Succeeded"
        )
    with DAG(name="hello-dag"):
        A = task(name="A")
        B = task(name="B", arguments={"message": "B"})
        C = task(name="C", arguments={"message": "C"})
        D = task(name="D", arguments={"message": "D"})
        A >> [B, C] >> D
    workflow_template.on_exit = exit_handler
    # Compile to workflowtemplate YAML and submit to argo workflow
    print(workflow_template.to_yaml())
    workflow_template.lint()
    workflow_template.create()
# Compile the CronWorkflow that references the WorkflowTemplate
cron_workflow.lint()
cron_workflow.create()
