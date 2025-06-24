from hera.workflows import DAG, Workflow, script


@script(image="python:3.11-alpine")
def print_message(message: str):
    print(message)


@script(image="python:3.11-alpine")
def generate_dates(
    start_date: str = "2025-01-01",
    end_date: str = "2025-01-10"
):
    import json
    import sys
    from datetime import datetime, timedelta

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    delta = (end_dt - start_dt).days
    dates = [
        {
            "execute_date": (start_dt + timedelta(days=i)).strftime('%Y-%m-%d')
        } for i in range(delta+1)
    ]
    json.dump(dates, sys.stdout)


with Workflow(
    generate_name="dynamic-dag-workflow-", entrypoint="dynamic-dag"
) as w:
    with DAG(name="dynamic-dag"):
        t1 = generate_dates(
            name="generate-dates",
            arguments={
                "start_date": "2025-01-01",
                "end_date": "2025-01-10"
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
        w.lint()
        print(w.to_yaml())
        w.create()
