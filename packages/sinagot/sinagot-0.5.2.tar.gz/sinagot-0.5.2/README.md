# Sinagot

<p align="center">
<a href="https://pypi.org/project/fastapi" target="_blank">
    <img src="https://img.shields.io/pypi/v/sinagot?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/fastapi" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/sinagot.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

---

**Source Code**: <a href="https://gitlab.com/YannBeauxis/sinagot" target="_blank">https://gitlab.com/YannBeauxis/sinagot</a>

---

Sinagot is a Python lightweight workflow management framework using [Ray](https://www.ray.io/) as distributed computing engine.

The key features are:

- **Easy to use**: Design workflow with simple Python classes and functions without external configuration files.
- **Data exploration**: Access to computed data directly with object attributes, including complex type as pandas DataFrame.
- **Scalable**: The [Ray](https://www.ray.io/) engine enable seamless scaling of workflows to external clusters.

## Installation

```bash
pip install sinagot
```

## Getting started

```python
import pandas as pd
import sinagot as sg

# Decorate functions to use them as workflow step
@sg.step
def multiply(df: pd.DataFrame, factor: int) -> pd.DataFrame:
    return df * factor


@sg.step
def get_single_data(df: pd.DataFrame) -> int:
    return int(df.iloc[0, 0])


# Design a workflow
class TestWorkflow(sg.Workflow):
    raw_data: pd.DataFrame = sg.seed() # seed is input data
    factor: int = sg.seed()
    multiplied_data: pd.DataFrame = multiply.step(raw_data, factor=factor)
    final_data: int = get_single_data.step(multiplied_data)


# Create a workspace on top of workflow for storage policy of data produced
class TestWorkspace(sg.Workspace[TestWorkflow]):
    raw_data = sg.LocalStorage("raw_data/data-{workflow_id}.csv")
    factor = sg.LocalStorage("params/factor")
    multiplied_data = sg.LocalStorage(
        "computed/multiplied_data-{workflow_id}.csv", write_kwargs={"index": False}
    )
    # In this example final_data is not stored and computed on demand


# Create a workspace with local storage folder root path parameter
ws = TestWorkspace("/path/to/local_storage")

# Access to a single workflow with its ID
wf = ws["001"]

# Access to item data, computed automatically if it does not exist in storage
display(wf.multiplied_data)
print(wf.final_data)
```

In this example, the storage dataset is structured as follows :

```
├── params/
│   └── factor
├── raw_data/
│   ├── data-{item_id}.csv
│   └── ...
└── computed/
    ├── step-1-{item_id}.csv
    └── ...
```

And the workflow is :

<img src="docs/workflow.png" width="500">

## Development Roadmap

Sinagot is at an early development stage but ready to be tested on actual datasets for workflows prototyping.

Features development roadmap will be prioritized depending on usage feedbacks, so feel free to post an issue if you have any requirement.
