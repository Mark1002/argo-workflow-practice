from typing import Optional
from urllib.parse import urljoin

from hera.workflows.models import (
    LintCronWorkflowRequest,
    CreateCronWorkflowRequest,
    UpdateCronWorkflowRequest,
    CronWorkflow
)
from hera.workflows.service import (
    WorkflowsService,
    valid_host_scheme
)
from hera.exceptions import exception_from_server_response


class WorkflowService(WorkflowsService):
    """Overrdie these methods due to Argo Workflow v3.5.x API schema error."""

    def create_cron_workflow(self, req: CreateCronWorkflowRequest, namespace: Optional[str] = None) -> CronWorkflow:
        """API documentation."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = self._request(
            method="post",
            url=urljoin(self.host, "api/v1/cron-workflows/{namespace}").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": self.token, "Content-Type": "application/json"},
            data=req.json(exclude_none=True, by_alias=True, exclude_unset=True, exclude_defaults=True),
            verify=self.verify_ssl,
            cert=self.client_certs,
        )
        if resp.ok:
            # Add 3 missing fields to the response
            kwargs = resp.json()
            kwargs["status"].update({"failed": 0, "phase": "", "succeeded": 0})
            return CronWorkflow(**kwargs)

        raise exception_from_server_response(resp)

    def lint_cron_workflow(self, req: LintCronWorkflowRequest, namespace: Optional[str] = None) -> CronWorkflow:
        """API documentation."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = self._request(
            method="post",
            url=urljoin(self.host, "api/v1/cron-workflows/{namespace}/lint").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": self.token, "Content-Type": "application/json"},
            data=req.json(exclude_none=True, by_alias=True, exclude_unset=True, exclude_defaults=True),
            verify=self.verify_ssl,
            cert=self.client_certs,
        )
        if resp.ok:
            # Add 3 missing fields to the response
            kwargs = resp.json()
            kwargs["status"].update({"failed": 0, "phase": "", "succeeded": 0})
            return CronWorkflow(**kwargs)

        raise exception_from_server_response(resp)

    def get_cron_workflow(
        self, name: str, namespace: Optional[str] = None, resource_version: Optional[str] = None
    ) -> CronWorkflow:
        """API documentation."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = self._request(
            method="get",
            url=urljoin(self.host, "api/v1/cron-workflows/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params={"getOptions.resourceVersion": resource_version},
            headers={"Authorization": self.token},
            data=None,
            verify=self.verify_ssl,
            cert=self.client_certs,
        )

        if resp.ok:
            # Add 3 missing fields to the response
            kwargs = resp.json()
            kwargs["status"].update({"failed": 0, "phase": "", "succeeded": 0})
            return CronWorkflow(**kwargs)

        raise exception_from_server_response(resp)

    def update_cron_workflow(
        self, name: str, req: UpdateCronWorkflowRequest, namespace: Optional[str] = None
    ) -> CronWorkflow:
        """API documentation."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = self._request(
            method="put",
            url=urljoin(self.host, "api/v1/cron-workflows/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": self.token, "Content-Type": "application/json"},
            data=req.json(exclude_none=True, by_alias=True, exclude_unset=True, exclude_defaults=True),
            verify=self.verify_ssl,
            cert=self.client_certs,
        )

        if resp.ok:
            # Add 3 missing fields to the response
            kwargs = resp.json()
            kwargs["status"].update({"failed": 0, "phase": "", "succeeded": 0})
            return CronWorkflow(**kwargs)

        raise exception_from_server_response(resp)
