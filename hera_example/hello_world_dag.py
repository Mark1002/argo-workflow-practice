import os
from hera.workflows import Steps, DAG, Workflow, WorkflowsService, script

from hera_example.utils import argo_lint_from_yaml

ARGO_SERVER = os.getenv("ARGO_SERVER", "http://localhost:2746")
ARGO_TOKEN = os.getenv("ARGO_TOKEN")


@script(image="python:3.11-alpine")
def echo(message: str):
    if message == "C":
        raise ValueError("Simulating a failure in task C")
    print(message)


@script(image="python:3.11-alpine")
def notify():
    print("Exiting workflow and sending notification.")


with Workflow(
    generate_name="hello-world-",
    entrypoint="hello-dag",
    namespace="argo",
    workflows_service=WorkflowsService(host=ARGO_SERVER, token=ARGO_TOKEN)
) as w:
    with Steps(name="exit-handler") as exit_handler:
        notify(name="exit-handler", when="{{workflow.status}} != Succeeded")

    with DAG(name="hello-dag") as hello_dag:
        A = echo(name="A", arguments={"message": "A"})
        B = echo(name="B", arguments={"message": "B"})
        C = echo(name="C", arguments={"message": "C"})
        D = echo(name="D", arguments={"message": "D"})

        A >> [B, C] >> D

    w.on_exit = exit_handler

# Compile Hera python code to Argo Workflow yaml
yaml = w.to_yaml()
print(yaml)
argo_lint_from_yaml(yaml)
# Create the workflow in the Argo server
submitted_workflow = w.create()
print(f"Workflow at {ARGO_SERVER}/workflows/argo/{submitted_workflow.metadata.name}") # noqa
