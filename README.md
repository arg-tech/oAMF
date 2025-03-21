
## 📌 Open Argument Mining Framework (oAMF)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/arg-tech/amf) 
![PyPI](https://img.shields.io/pypi/v/argument-mining-framework) 
![License](https://img.shields.io/badge/License-GPL%203.0-blue)


oAMF is a **modular, open-source framework** designed for **end-to-end argument mining (AM)**. It empowers researchers and developers to construct, execute, and extend **customizable AM pipelines** using a variety of modules. The framework supports **multiple interfaces**, making it highly accessible to users with different technical backgrounds.

## ✨ Key Features

- **🔗 15+ Open-Source AM Modules**: Covering a broad range of argument mining tasks.
- **🖥️ Multiple Interfaces**:
  - **Web Interface**: Execute predefined pipelines directly from your browser.
  - **Drag-and-Drop Interface**: Create pipelines visually with **n8n**.
  - **Python API**: Define and execute pipelines programmatically.
- **🛠️ Modular & Extendable**: Easily add new modules that interact via the standardized **xAIF format**.
- **📡 Local & Remote Execution**: Modules can be deployed locally or accessed as remote services.

---

## 📖 Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
   - [Deploying and Loading Modules](#deploying-and-loading-modules)
   - [Creating and Running an AM Pipeline](#creating-and-running-an-am-pipeline)
   - [Drag-and-Drop Interface](#drag-and-drop-interface)
   - [Web Interface](#web-interface)
3. [📝 xAIF (Extended Argument Interchange Format)](#xaif-extended-argument-interchange-format)
4. [📚 Available Modules](#available-modules)
5. [📦 Module Development](#module-development)
6. [📌 Release Information](#release-information)
7. [📜 License](#license)
8. [📚 Resources](#resources)

---

## 🛠️ Installation

To install the oAMF library, run:

```bash
pip install oamf
```

This package allows you to locally deploy and execute AM pipelines with integrated modules.

---

## 🚀 Usage

### 📂 Deploying and Loading Modules

Modules can be loaded from **GitHub repositories** (for local execution) or **web services** (for remote execution). Below is an example of loading and deploying modules:

```python
from oamf import oAMF

oamf = oAMF()

# Modules to load: (URL, type ['repo' or 'ws'], deployment route, tag)
modules_to_load = [
    ("https://github.com/arg-tech/default_turninator.git", "repo", "turninator-01", "turninator"),
    ("https://github.com/arg-tech/default_segmenter.git", "repo", "segmenter-01", "segmenter"),
    ("http://bert-te.amfws.arg.tech/bert-te", "ws", "bert-te", "bert-te")
]

# Load and deploy modules
oamf.load_modules(modules_to_load)
```

### 🔄 Creating and Running an AM Pipeline

An AM pipeline is defined as a directed graph where each module processes and passes data to the next module. Here's how you define and execute a pipeline:

```python
# Define the pipeline using module tags
pipeline_graph = [
    ("turninator", "segmenter"),   # "turninator" outputs to "segmenter"
    ("segmenter", "bert-te")      # "segmenter" outputs to "bert-te"
]

# Execute the pipeline using the defined workflow and an input file in xAIF format
oamf.pipelineExecutor(pipeline_graph, input_file)
```

### 🖱️ Drag-and-Drop Interface

Users can create AM pipelines visually in **n8n**, a workflow automation tool. In this interface, modules are represented as **nodes** that you can connect and execute. 


![n8n Drag-and-Drop Interface](assets/n8n.jpeg)


The workflow can also be exported as JSON and executed using the oAMF API. Example:

```python
# Override the manually defined pipeline with one created using n8n (if applicable)
oamf.pipelineExecutor(pipeline_graph, input_file, workflow_file)
```

### 🌐 Web Interface

The web interface allows users to upload **text/xAIF files**, select pipelines, and execute AM tasks without writing any code. Access the web interface here: [oAMF Web Interface](https://arg-tech.github.io/oAMF/).

![Web Page](assets/home.jpeg)

---

## 📝 xAIF (Extended Argument Interchange Format)

oAMF uses **xAIF** as a standard format for representing argument structures. Below is an example of xAIF in JSON format:

```json
{
  "nodes": [
    { "id": "n1", "text": "Climate change is real.", "type": "claim" },
    { "id": "n2", "text": "Scientists have provided evidence.", "type": "premise" }
  ],
  "edges": [
    { "from": "n2", "to": "n1", "relation": "supports" }
  ]
}
```

xAIF ensures interoperability between AM modules. oAMF includes the `xaif` library, which allows you to create, load, and manipulate xAIF data structures. Example usage:

```python
# Ensure you have the latest version of xaif (pip install xaif)
from xaif import AIF

# Sample xAIF JSON with 2 L nodes and 2 I nodes
aif_data = {"AIF": {"nodes": [
      {"nodeID": 0, "text": "Example L node 1", "type": "L"},
      {"nodeID": 1, "text": "Example L node 2", "type": "L"},
      {"nodeID": 2, "text": "Example I node 1", "type": "I"},
      {"nodeID": 3, "text": "Example I node 2", "type": "I"},
      {"nodeID": 4, "text": "Default Inference", "type": "RA"}
    ],
    "edges": [
      {"edgeID": 0, "fromID": 0, "toID": 2},
      {"edgeID": 1, "fromID": 1, "toID": 3},
      {"edgeID": 2, "fromID": 2, "toID": 4},
      {"edgeID": 4, "fromID": 2, "toID": 3}
    ],
    "locutions": [{"nodeID": 0, "personID": 0}],
    "participants": [{"firstname": "Speaker", "participantID": 0, "surname": "Name"}]
  },
   "dialog": True
}

aif = AIF(aif_data)  # Initialize AIF object with xAIF data
# Or create an xAIF structure from raw text:
# aif = AIF("here is the text.")

# 1. Adding components
aif.add_component(component_type="locution", text="Example L node 3.", speaker="Another Speaker")  # ID 5 assigned
aif.add_component(component_type="proposition", Lnode_ID=5, proposition="Example I node 3.")  # ID 6 assigned to I-Node
aif.add_component(component_type="argument_relation", relation_type="RA", iNode_ID2=3, iNode_ID1=6)  # Creating relation

print(aif.xaif)  # Print the generated xAIF data
print(aif.get_csv("argument-relation"))  # Export to CSV format
```

---

## 📚 Available Modules

oAMF includes a variety of argument mining modules, each designed for different tasks:

| Module          | Task                                   | URL                                                   |
|-----------------|----------------------------------------|-------------------------------------------------------|
| **Turninator**  | Segmentation                           | [Repo](https://github.com/arg-tech/default_turninator) |
| **BERT-TE**     | Argument Component Classification      | [Service](http://bert-te.amfws.arg.tech/bert-te)      |
| **ToulminMapper**| Identifies Toulmin Model Components    | [Repo](https://github.com/arg-tech/ToulminMapper)     |
| **ArgumenText** | Argument Quality Assessment            | [Repo](https://github.com/arg-tech/ArgumentQuality)   |

For a full list of available modules, refer to the [official documentation](#resources).

---



## 📦 Module Development

To develop a custom oAMF module, you need to create a web service that is **dockerized** for portability and scalability. 
The module is built using the **Flask** framework. It accepts and outputs **xAIF** data, making it compatible with oAMF's argument mining tasks.

### Key Features of an oAMF Module:
- **Web Service**: The module exposes a set of HTTP endpoints to interact with the module through HTTP requests.
- **Dockerized**: The module is encapsulated in a Docker container, ensuring easy deployment and scalability. The container is configured using `Dockerfile` and `docker-compose.yaml`.

### Project Structure
The module project follows a standard web application structure, with the following key components:
- **`config/metadata.yaml`**: Contains essential metadata about the module (e.g., name, license, version, and input/output details).
- **`project_source_dir/`**: Contains the core application code, including the Flask routes and module logic.
- **`boot.sh`**: A shell script to activate the virtual environment and launch the application.
- **`docker-compose.yaml`**: Defines the Docker service and how the application is built and run.
- **`Dockerfile`**: Specifies the Docker image, environment, and installation of dependencies.
- **`requirements.txt`**: Lists all the Python dependencies required by the project.

### Metadata Configuration (`config/metadata.yaml`)
The `metadata.yaml` file provides essential information about the module, such as:
```yaml
Name: "Name of the Module"
Date: "2024-10-01"
Originator: "Author"
License: "Your License"
AMF_Tag: Your_tag_name
Domain: "Dialog"
Training Data: "Annotated corpus X"
Citation: ""
Variants:
  - name: 0 version: null
  - name: 1 version: null
Requires: text
Outputs: segments
```

### Flask Application Routes
The Flask application defines the following routes:
- **Index Route (`/`)**: Displays the contents of the `README.md` file as documentation.
- **AMF Module Route**: This route can be named according to the module's function.
  - **POST requests**: Used to upload an **xAIF** file and process it with the module logic. The response is a JSON object containing the updated **xAIF** data.
  - **GET requests**: Provides access to documentation and metadata.

### How to Develop an oAMF Module
To create a custom oAMF module, follow these general steps:

1. **Clone the NOOP Template**: Start by cloning the [NOOP template](https://github.com/arg-tech/AMF_NOOP).
2. **Modify Metadata**: Update `metadata.yaml` with details such as the module's name, license, inputs/outputs, and other relevant information.
3. **Implement Core Logic**: Modify `routes.py` to define the core functionality of the module.
4. **Integrate with xAIF**: Use the `xaif` library to manipulate **xAIF** data according to your module's needs.
5. **Configure Docker**: Set up the `Dockerfile` and `docker-compose.yaml` to ensure the module is dockerized for easy deployment.
6. **Documentation**: Update the `README.md` file with instructions for using the module.

---



## 📜 License

oAMF is licensed under the **Apache 2.0 License**, allowing free use, modification, and distribution. For more details, see the [LICENSE](https://github.com/arg-tech/oAMF/blob/main/LICENSE) file.

---

## 📚 Resources

- 📖 **Documentation & Tutorials**: [Read Docs](https://docs.arg.tech/oAMF)
- 🖥️ **Web Page**: [Try it here](https://arg-tech.github.io/oAMF/)
- 🖥️ **n8n Demo**: [Try it here](https://n8n.arg.tech/workflow/2)
- 🛠️ **GitHub Source**: [oAMF GitHub](https://github.com/arg-tech/amf)
- 📦 **PyPI Package**: [oAMF on PyPI](https://pypi.org/project/oamf/)

---

### 🚀 Happy Argument Mining with oAMF!

---

