import subprocess
import tempfile


def argo_lint_from_yaml(yaml_str: str):
    with tempfile.NamedTemporaryFile(
        "w+", suffix=".yaml", delete=False
    ) as tmp:
        tmp.write(yaml_str)
        tmp.flush()
        cmd = ["argo", "lint", tmp.name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise ValueError(result.stdout)
        print(result.stdout)
