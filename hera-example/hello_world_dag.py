from hera.workflows import Steps, Workflow, WorkflowsService, script

ARGO_SERVER = "http://localhost:2746"


@script()
def echo(message: str):
    print(message)


with Workflow(
    generate_name="hello-world-",
    entrypoint="steps",
    namespace="argo",
    workflows_service=WorkflowsService(host=ARGO_SERVER)
) as w:
    with Steps(name="steps"):
        echo(arguments={"message": "Hello world!"})

submitted_workflow = w.create()
print(f"Workflow at {ARGO_SERVER}/workflows/argo/{submitted_workflow.metadata.name}") # noqa
