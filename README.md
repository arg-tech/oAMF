
## 📌 Open Argument Mining Framework (oAMF)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/arg-tech/amf) 
![PyPI](https://img.shields.io/pypi/v/argument-mining-framework) 
![License](https://img.shields.io/badge/License-GPL%203.0-blue)



oAMF is a modular **open-source framework** for **end-to-end argument mining (AM)**. It enables researchers and developers to build and run **customizable AM pipelines** using a diverse set of modules. With over 15 AM modules and oAMF-compatible extensions—including audio transcription, argument structure visualisation, and evaluation tools—the framework offers extensive functionality. Developers can integrate new AM modules or modify existing ones to fit their needs. Additionally, oAMF supports **multiple interfaces**, ensuring accessibility for users with varying technical expertise.  


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
7. [📜 License](#license)  
8. [📚 Resources](#resources)  
9. 📖 **Documentation & Tutorials**  
   - [GitHub Docs](https://github.com/arg-tech/oAMF/blob/main/docs/tutorial.md)  
   - [Jupyter Example](https://github.com/arg-tech/oAMF/blob/main/example/example_usage.ipynb)  

## 🛠️ Installation

To install the oAMF library, run:

```bash
pip install oamf
```

This package allows you to locally deploy and execute AM pipelines with integrated modules.

---

## 🚀 Usage

### 📂 Deploying and Loading Modules

Modules can be loaded from **GitHub repositories** (for local execution) or **web services** (for remote execution). See details of existing modules here [📚 Available Modules](#available-modules). Below is an example of loading and deploying modules:

```python
from oamf import oAMF

oamf = oAMF()



""" Modules to Load  

Specify the modules you want to load. You can do this in two ways:  

1. **Using a deployed web service** – Provide the module’s web service URL.  
2. **Deploying from a GitHub repository** – Provide the repository URL to deploy the module locally.  

To achieve this, define the module’s URL, specify its type (`repo` for repositories or `ws` for web services), and assign a unique tag.  

### Tags and Pipeline Construction  
Tags are used later to construct a pipeline. If you need to use the same module multiple times within a pipeline, specify it multiple times with different tags.  


Each module should be specified as:  


(URL, type ['repo' or 'ws'], deployment route, tag)
"""
modules_to_load = [
    ("https://github.com/arg-tech/default_turninator.git", "repo", "turninator-01", "turninator"),
    ("https://github.com/arg-tech/default_segmenter.git", "repo", "segmenter-01", "segmenter"),
    ("http://targer.amfws.arg.tech/targer-segmenter", "ws", "targer-segmenter", "targer"),
    ("http://default-proposition-unitiser.amfws.arg.tech/propositionUnitizer-01", "ws", "propositionUnitizer-01", "propositionUnitizer"),
    ("http://bert-te.amfws.arg.tech/bert-te", "ws", "bert-te", "bert-te")
]



# Load and deploy modules
oamf.load_modules(modules_to_load)
```

### 🔄 Creating and Running an AM Pipeline

An AM pipeline is defined as a directed graph where each module processes and passes data to the next module. The pipeline is created using the tags specified during module loading. Here's how you define and execute a pipeline:

```python
# Define the pipeline using module tags
pipeline_graph = [
    ("turninator", "segmenter"),   # "turninator" outputs to "segmenter"
    ("segmenter", "propositionUnitizer")      # "segmenter" outputs to "bert-te"
    ("propositionUnitizer", "bert-te")      # "segmenter" outputs to "bert-te"
]

# Execute the pipeline using the defined workflow and an input file in xAIF format
output_path, xaif_result = oamf.pipelineExecutor(pipeline_graph, "example_input_file.json") # It writes the output to a temp file and also returns the xaif output
```

### 🖱️ Drag-and-Drop Interface

Users can create AM pipelines visually in **n8n**, a workflow automation tool. In this interface, modules are represented as **nodes** that you can connect and execute. [Try it here](https://n8n-new.arg.tech/workflow/2)  


![n8n Drag-and-Drop Interface](assets/n8n.jpeg)


The workflow can also be exported as JSON and executed using the oAMF API. Example:

```python
# Override the manually defined pipeline with one created using n8n (if applicable)
oamf.pipelineExecutor(pipeline_graph, "example_input_file.json", "workflow_file.json")
```

### 🌐 Web Interface

The web interface allows users to provide **Input Text**, select pipelines, and execute AM tasks without writing any code. Access the web interface here: [oAMF Web Interface](https://arg-tech.github.io/oAMF/).

![Web Page](assets/site-design.png)

---

## 📝 xAIF (Extended Argument Interchange Format)

oAMF uses **xAIF** as a standard format for representing argument structures. xAIF ensures interoperability between AM modules. 
Check a quick xAIF Tutorial and the accompaning python library hereL  📖 **Tutorial**: [XAIF Tutorial](https://github.com/arg-tech/xaif/blob/main/docs/tutorial.md). Below is an example of xAIF in JSON format:

```json
# Sample xAIF JSON 
aif= {
  "AIF": {
    "descriptorfulfillments": null,
    "edges": [
      {
        "edgeID": 0,
        "fromID": 0,
        "toID": 4
      },
      {
        "edgeID": 1,
        "fromID": 4,
        "toID": 3
      },
      {
        "edgeID": 2,
        "fromID": 1,
        "toID": 6
      },
      {
        "edgeID": 3,
        "fromID": 6,
        "toID": 5
      },
      {
        "edgeID": 4,
        "fromID": 2,
        "toID": 8
      },
      {
        "edgeID": 5,
        "fromID": 8,
        "toID": 7
      },
      {
        "edgeID": 6,
        "fromID": 3,
        "toID": 9
      },
      {
        "edgeID": 7,
        "fromID": 9,
        "toID": 7
      }
    ],
    "locutions": [
      {
        "nodeID": 0,
        "personID": 0
      },
      {
        "nodeID": 1,
        "personID": 1
      },
      {
        "nodeID": 2,
        "personID": 2
      }
    ],
    "nodes": [
      {
        "nodeID": 0,
        "text": "disagreements between party members are entirely to be expected.",
        "type": "L"
      },
      {
        "nodeID": 1,
        "text": "the SNP has disagreements.",
        "type": "L"
      },
      {
        "nodeID": 2,
        "text": "it's not uncommon for there to be disagreements between party members.",
        "type": "L"
      },
      {
        "nodeID": 3,
        "text": "disagreements between party members are entirely to be expected.",
        "type": "I"
      },
      {
        "nodeID": 4,
        "text": "Default Illocuting",
        "type": "YA"
      },
      {
        "nodeID": 5,
        "text": "the SNP has disagreements.",
        "type": "I"
      },
      {
        "nodeID": 6,
        "text": "Default Illocuting",
        "type": "YA"
      },
      {
        "nodeID": 7,
        "text": "it's not uncommon for there to be disagreements between party members.",
        "type": "I"
      },
      {
        "nodeID": 8,
        "text": "Default Illocuting",
        "type": "YA"
      },
      {
        "nodeID": 9,
        "text": "Default Inference",
        "type": "RA"
      }
    ],
    "participants": [
      {
        "firstname": "Speaker",
        "participantID": 0,
        "surname": "1"
      },
      {
        "firstname": "Speaker",
        "participantID": 1,
        "surname": "2"
      }
    ],
    "schemefulfillments": null
  },
  "dialog": true,
  "ova": [],
  "text": {
    "txt": " Speaker 1 <span class=\"highlighted\" id=\"0\">disagreements between party members are entirely to be expected.</span>.<br><br> Speaker 2 <span class=\"highlighted\" id=\"1\">the SNP has disagreements.</span>.<br><br> Speaker 1 <span class=\"highlighted\" id=\"2\">it's not uncommon for there to be disagreements between party members. </span>.<br><br>"
  }
}
```

oAMF includes the `xaif` library, which allows you to create, load, and manipulate xAIF data structures. Example usage:

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
### 🔗 XAIF Library Resources  

- 🛠️ **GitHub Repository**: [XAIF Library Repo](https://github.com/arg-tech/xaif)  
- 📦 **PyPI Package**: [XAIF on PyPI](https://pypi.org/project/xaif/)  
- 📖 **Tutorial**: [XAIF Tutorial](https://github.com/arg-tech/xaif/blob/main/docs/tutorial.md)  
- 📓 **Jupyter Example**: [How to Use XAIF in Jupyter](https://github.com/arg-tech/xaif/blob/main/docs/xaif_example.ipynb)  

---

## 📚 Available Modules

oAMF includes a variety of argument mining modules, each designed for different tasks:

| **Module**       | **Task**                                      | **Input**                                            | **Output**                                                   | **URL**                                                    |
|------------------|-----------------------------------------------|------------------------------------------------------|--------------------------------------------------------------|------------------------------------------------------------|
| **DTSG**         | Text Segmentation                              | Unsegmented text and no structure.                   | Text segmented into turns (e.g., contiguous text from one speaker or NOOP in case of monologue). | [Link](http://default-turninator.amfws.arg.tech/turninator-01) |
| **DSG**          | Text Segmentation & Structuring               | Unsegmented text or text segmented into turns.       | Text segmented using the <SPAN> tag into segments; structure containing L-nodes with IDs cross-referencing those in SPAN tags. | [Link](default-segmenter.amfws.arg.tech/segmenter-01) |
| **DARJ**         | Co-reference Resolution                       | Segmented locutions.                                 | Resolve co-references (mostly speaker names) in locution nodes. | [Link](cascading-propositionUnitiser.amfws.arg.tech/anaphora-01) |
| **SPG**          | Segmentation and Proposition Structuring      | Text segmented using the <SPAN> tag into segments; structure with L-nodes. | Text segmented using <SPAN> tag into segments; structure with L-nodes anchoring YA-nodes connected to I-nodes. | [Link](default-proposition-unitiser.amfws.arg.tech/propositionUnitizer-01) |
| **CPJ**          | Cascading Proposition Structuring             | Text segmented using the <SPAN> tag into segments; structure with L-nodes. | Text segmented using <SPAN> tag into segments; structure with L-nodes anchoring YA-nodes connected to I-nodes. | [Link](cascading-propositionUnitiser.amfws.arg.tech/propositionaliser-cascading) |
| **DAMG**         | Argument Graph Generation                     | Segmented text; structure with I-nodes.              | Segmented text; structure with I-nodes connected with RA and CA nodes. | [Link](http://dam.amfws.arg.tech/dam-03) |
| **DTERG**        | Argument Component Classification             | Segmented text; structure with I-nodes.              | Segmented text; structure with I-nodes connected with RA nodes. | [Link](bert-te.amfws.arg.tech/bert-te) |
| **PDSCZ**        | Scheme-Based Classification                   | Segmented text; structure with I-nodes connected with RA nodes. | Segmented text; structure with I-nodes connected with RA nodes specified by pragma-dialectical scheme type. | [Link](http://amfws-schemeclassifier.arg.tech/schemes_clsf) |
| **SARIM**        | xAIF File Processing                          | xAIF file containing proposition nodes.              | xAIF file containing input and new nodes (RA, CA) with related relations between nodes. | [Link](http://amfws-rp.arg.tech/somaye) |
| **ARIR**         | Argument Graph Completion                     | xAIF file containing segmented propositional nodes.  | xAIF file with complete propositional argument graph, including RA, CA, and MA nodes, along with new edges. | [Link](http://amfws-ari.arg.tech/) |
| **DRIG**         | Argumentation Graph Generation                | xAIF file containing I-nodes.                         | Segmented text; structure with I-nodes connected with RA, MA, and CA nodes. | [Link](vanilla-am-caasr.amfws.arg.tech/caasra) |
| **WSCR**         | Scheme Replacement in Argumentation           | xAIF file containing propositional nodes (I) and RA relations. | xAIF file where "Default Inference" relations are replaced by specific argumentation schemes (e.g., Argument From Analogy). | [Link](http://amf-schemes.amfws.arg.tech) |
| **PTCR**         | Proposition Classification                    | xAIF file containing propositional nodes (I).         | xAIF file with the "propositionClassifier" key containing list of propositions (I) classified into Value, Policy, and Fact types. | [Link](http://amf-ptc.amfws.arg.tech) |
| **CASS-Moslemnejad-2025** | Evaluation Metrics                | Two comprehensive xAIF files with all information nodes and text segments. | F1 Macro/Accuracy/CASS/Text Similarity/Kappa/U-Alpha. | [Link](https://github.com/arg-tech/AMF-Evaluation-Scores) |
| **whisper-speech-to-text-2025** | Speech-to-Text Transformation   | Audio file.                                          | xAIF with the text field populated with transcription. | [Link](realtime-backend.amfws.arg.tech/transcribe_whisper-0) |




---



## 📦 Module Development

To develop a custom oAMF module, you need to create a web service that is **dockerized** for portability and scalability. 
The module is built using the **Flask** framework. It accepts and outputs **xAIF** data, making it compatible with oAMF's argument mining tasks.

### Key Features of an oAMF Module:
- **Web Service**: The module exposes a set of HTTP endpoints to interact with the module through HTTP requests.
- **Dockerized**: The module is encapsulated in a Docker container, ensuring easy deployment and scalability. The container is configured using `Dockerfile` and `docker-compose.yaml`.

### Project Structure

The project follows a standard web application structure, with the following key components:

- **`config/metadata.yaml`**: This file contains essential metadata about the module, including the module name, license, version, and input/output specifications. It serves as the module's configuration and is key for integration with other systems.

- **`project_source_dir/`**: This directory holds the core application code. It includes the Flask routes and the main logic of the module that handles requests, processing, and responses.

- **`boot.sh`**: A shell script responsible for activating the virtual environment and launching the application. It simplifies the setup and ensures that the application runs in the correct environment.

- **`docker-compose.yaml`**: Defines the Docker service and how the application is built and run within a containerized environment. The `docker-compose.yaml` file should be configured to reflect the project’s repository name. For example, in the case of the **bert-te** module, the service name in the Docker Compose file should match the repository name.

  Example Docker Compose service configuration:
  ```yaml
  services:
    bert-te:
      container_name: bert_te
      build:
        context: . # Specify the build context
        dockerfile: Dockerfile # Specify the Dockerfile if it's not named 'Dockerfile'
      ports:
        - "5002:5002" # Map port 5002 on the host to port 5002 in the container


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

- 📖 **Documentation & Tutorials**: [Read Docs](https://docs.arg.tech/oAMF) | [GitHub Docs](https://github.com/arg-tech/oAMF/blob/main/docs/tutorial.md) | [Jupyter Example](https://github.com/arg-tech/oAMF/blob/main/example/example_usage.ipynb)  
- 🖥️ **Web Page**: [Try it here](https://arg-tech.github.io/oAMF/)  
- 🖥️ **n8n Demo**: [Try it here](https://n8n-new.arg.tech/workflow/2)  
- 🛠️ **GitHub Source**: [oAMF GitHub](https://github.com/arg-tech/amf)  
- 📦 **PyPI Package**: [oAMF on PyPI](https://pypi.org/project/oamf/)  
---

### 🚀 Happy Argument Mining with oAMF!

---

