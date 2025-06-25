from hera.workflows import (
    DAG, WorkflowTemplate, script, CronWorkflow, Steps
)
from hera.workflows.models import WorkflowTemplateRef

from hera_example.service import WorkflowService


W_NAME = "dynamic-backfill-dag"
W_TEMPLATE = f"{W_NAME}-template"
EXECUTE_DATE = '{{=sprig.date("2006-01-02", sprig.dateModify("-24h", sprig.now()))}}' # noqa


@script(image="python:3.11-alpine")
def print_message(message: str):
    print(message)


@script(image="python:3.11-alpine")
def notify():
    print("Exiting workflow and sending notification.")


@script(image="python:3.11-alpine")
def generate_dates(start_date: str, end_date: str):
    import json
    import sys
    from datetime import datetime, timedelta

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    if start_dt > end_dt:
        raise ValueError("Start date must be before or equal to end date.")
    delta = (end_dt - start_dt).days
    dates = [
        {
            "execute_date": (start_dt + timedelta(days=i)).strftime('%Y-%m-%d')
        } for i in range(delta+1)
    ]
    json.dump(dates, sys.stdout)


cw = CronWorkflow(
    name=W_NAME,
    entrypoint="dynamic-dag",
    schedule="*/3 * * * *",
    on_exit="exit-handler",
    workflow_template_ref=WorkflowTemplateRef(name=W_TEMPLATE),
    workflows_service=WorkflowService(),
    arguments={"start_date": EXECUTE_DATE, "end_date": EXECUTE_DATE}
)

with WorkflowTemplate(
    name=W_TEMPLATE, entrypoint="dynamic-dag"
) as w:
    with Steps(name="exit-handler") as exit_handler:
        notify(
            name="exit-handler",
            when="{{workflow.status}} != Succeeded"
        )
    with DAG(
        name="dynamic-dag",
        inputs=[
            {"start_date": "2025-01-01"},
            {"end_date": "2025-01-10"}
        ]
    ) as dag:
        t1 = generate_dates(
            name="generate-dates",
            arguments={
                "start_date": dag.get_parameter("start_date"),
                "end_date": dag.get_parameter("end_date")
            }
        )
        t2 = print_message(
            name="daily-task",
            with_param=t1.result,
            arguments={"message": "{{item.execute_date}}"}
        )
        t3 = print_message(
            name="final-task",
            arguments={"message": "All tasks completed successfully!"}
        )
        t1 >> t2 >> t3
        w.on_exit = exit_handler
        w.create()
cw.create()
