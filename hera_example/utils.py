from hera.workflows import script


@script()
def monitor_external_workflow(external_workflow_name: str):
    """Monitor external workflow using Hera's native capabilities"""
    from hera.workflows import Workflow

    # Create a reference to the external workflow
    external_workflow = Workflow(name=external_workflow_name)

    try:
        # Wait for the external workflow to complete
        external_workflow.wait(poll_interval=30)
        print(f"External workflow {external_workflow_name} completed successfully") # noqa
        return "SUCCESS"
    except Exception as e:
        print(f"External workflow {external_workflow_name} failed: {e}")
        return "FAILED"
