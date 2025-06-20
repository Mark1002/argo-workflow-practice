import os
from hera.workflows import DAG, Workflow, WorkflowsService, script

ARGO_SERVER = os.getenv("ARGO_SERVER", "http://localhost:2746")
ARGO_TOKEN = os.getenv("ARGO_TOKEN")


@script(image="python:3.11-alpine")
def echo(message: str):
    print(message)


with Workflow(
    generate_name="hello-world-",
    entrypoint="hello-dag",
    namespace="argo",
    workflows_service=WorkflowsService(host=ARGO_SERVER, token=ARGO_TOKEN)
) as w:
    with DAG(name="hello-dag"):
        A = echo(name="A", arguments={"message": "A"})
        B = echo(name="B", arguments={"message": "B"})
        C = echo(name="C", arguments={"message": "C"})
        D = echo(name="D", arguments={"message": "D"})
        A >> [B, C] >> D

# Compile Hera python code to Argo Workflow yaml
print(w.to_yaml())
# Create the workflow in the Argo server
submitted_workflow = w.create()
print(f"Workflow at {ARGO_SERVER}/workflows/argo/{submitted_workflow.metadata.name}") # noqa
