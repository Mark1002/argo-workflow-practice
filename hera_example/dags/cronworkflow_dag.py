from hera.workflows import DAG, script, CronWorkflow
from hera_example.service import WorkflowService


@script(image="python:3.11-alpine")
def task_a():
    print("Task A")


@script(image="python:3.11-alpine")
def task_b():
    import time

    print("Start Task B...")
    time.sleep(300)
    print("Task B completed")


@script(image="python:3.11-alpine")
def task_c():
    print("Task C")


with CronWorkflow(
    name="daily-dag",
    schedule="*/2 * * * *",
    timezone="UTC",
    concurrency_policy="Forbid",
    entrypoint="dag",
    workflows_service=WorkflowService()
) as cw:
    with DAG(name="dag"):
        a, b, c = task_a(), task_b(), task_c()
        a >> [b, c]  # type: ignore

    cw.lint()
    print(cw.to_yaml())
    cw.update()
