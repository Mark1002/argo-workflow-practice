# Argo Workflow Practice
This repository is my practice of Aro Workflow.

## Set up Argo Workflow server
```bash
$ ./scripts/create-server.sh
```

## Set up Hera
1. create python virtual enviroment and install Hera
```python
$ uv venv --python 3.11 

$ uv pip install hera  
```

2. Submit Hera dag python file
```python
$ python -m hera_example.hello_world_dag
```
