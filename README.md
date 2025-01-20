
# AMF (Argument Mining Framework) 

![GitHub release (latest by date)](https://img.shields.io/github/v/release/arg-tech/amf) 
![PyPI](https://img.shields.io/pypi/v/argument-mining-framework) 
![License](https://img.shields.io/badge/License-GPL%203.0-blue)




AMF is a comprehensive toolkit designed to streamline and unify various argument mining modules into a single platform. By leveraging the Argument Interchange Format (AIF), AMF enables seamless communication between different components, including segmenters, turnators, argument relation identifiers, and argument scheme classifiers.

---

## 🚀 Features

- **Argument Segmentator**: Identifies and segments arguments within argumentative text.
- **Turninator**: Determines dialogue turns within conversations.
- **Argument Relation Identification**: Identifies argument relationships between argument units.
- **Argument Scheme Classification**: Classifies arguments based on predefined schemes.

## 📚 Resources

- [Documentation & Tutorials](https://wiki.arg.tech/books/amf)
- [Online Demo](https://n8n.arg.tech/workflow/2)
- [GitHub Source](https://github.com/arg-tech/amf)
- [PyPI Package](https://pypi.org/project/argument-mining-framework/)

## 📖 Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Components](#components)
    - [Argument Segmentor](#argument-segmentor)
    - [Turnator](#turnator)
    - [Argument Relation Identifier](#argument-relation-identifier)
    - [Argument Scheme Classifier](#argument-scheme-classifier)
4. [Usage](#usage)
    - [Predictor Example](#predictor-example)
    - [Full Workflow Example](#full-workflow-example)
5. [API Reference](#api-reference)
6. [License](#license)

## 📝 Overview

AMF provides a modular approach to argument mining, integrating various components into a cohesive framework. The main features include:

- **Argument Segmentator:** Identifies and segments arguments within argumentative text.
- **Turninator:** Determines dialogue turns within conversations.
- **Argument Relation Identification:** Identifies argument relationships between argument units.
- **Argument Scheme Classification:** Classifies arguments based on predefined schemes.




## 🛠 Installation
<details>
  <summary>Prerequisites & Setup</summary>

  <p>Ensure you have Python installed on your system. AMF is compatible with Python 3.6 and above.</p>

  <h3>Step 1: Create a Virtual Environment</h3>
  <p>It's recommended to create a virtual environment to manage dependencies:</p>
  <pre><code>python -m venv amf-env</code></pre>

  <p>Activate the virtual environment:</p>
  <ul>
    <li><strong>Windows:</strong>
      <pre><code>.\amf-env\Scripts\activate</code></pre>
    </li>
    <li><strong>macOS/Linux:</strong>
      <pre><code>source amf-env/bin/activate</code></pre>
    </li>
  </ul>

  <h3>Step 2: Install Dependencies</h3>
  <p>With the virtual environment activated, install AMF using pip:</p>
  <pre><code>pip install argument-mining-framework</code></pre>
  <p>This command will install the latest version of AMF along with its dependencies.</p>

  <h3>Additional Setup Instructions</h3>
  <p>After installing the <code>argument-mining-framework</code> package, make sure to download the necessary NLTK data and spaCy models:</p>
  <pre><code>python -m nltk.downloader stopwords
python -m nltk.downloader wordnet
python -m nltk.downloader averaged_perceptron_tagger_eng
python -m nltk.downloader omw-1.4

python -m spacy download en_core_web_lg
python -m spacy download en_core_web_sm</code></pre>
</details>





## 🧩 Components

### Argument Segmentor

The Argument Segmentor component is responsible for detecting and segmenting arguments within text. 

[Read More](http://default-segmenter.amfws.arg.tech/segmenter-01)

### Turnator

The Turnator identifies and segments dialogue turns, facilitating the analysis of conversations and interactions within texts. This module is particularly useful for dialogue-based datasets.

[Read More](http://default-turninator.amfws.arg.tech/turninator-01)

### Argument Relation Identifier

This component identifies and categorizes the relationships between argument units.

[Read More](http://bert-te.amfws.arg.tech/bert-te)

### Argument Scheme Classifier

The Argument Scheme Classifier categorizes arguments based on predefined schemes, enabling structured argument analysis.

[Read More](http://amf-schemes.amfws.arg.tech)

## 🧑‍💻 Usage

### Predictor Example

Below is an example of how to use the AMF Predictor class to generate an argument map using an input provided based on AIF:

```python
from argument_mining_framework.argument_relation.predictor import ArgumentRelationPredictor
import json

# Initialize Predictor
predictor = ArgumentRelationPredictor(model_type="dialogpt", variant="vanilla")

# Example XAIF structure
xaif = {
    "AIF": {
        "nodes": [
            {"nodeID": "1", "text": "THANK YOU", "type": "I", "timestamp": "2016-10-31 17:17:34"},
            {"nodeID": "2", "text": "COOPER : THANK YOU", "type": "L", "timestamp": "2016-11-10 18:34:23"},
            # Add more nodes as needed
        ],
        "edges": [
            {"edgeID": "1", "fromID": "1", "toID": "20", "formEdgeID": "None"},
            {"edgeID": "2", "fromID": "20", "toID": "3", "formEdgeID": "None"}
            # Add more edges as needed
        ],
        "locutions": [],
        "participants": []
    },
    "text": "people feel that they have been treated disrespectfully..."
}

# Convert XAIF structure to JSON string
xaif_json = json.dumps(xaif)

# Predict argument relations
result_map = predictor.argument_map(xaif_json)
print(result_map)
```


### Full Workflow Example

In this section, we demonstrate how to use multiple components of the AMF framework in a complete argument mining workflow. This example shows how to process a text input through the Turninator, Segmenter, Propositionalizer, and Argument Relation Predictor components and visualize the output.

```python
import logging
from argument_mining_framework.loader import Module

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_pipeline(input_data: str) -> None:
    """Process input data through the entire argument mining pipeline."""

    # Initialize components
    modules = {
        'turninator': Module('turninator'),
        'segmenter': Module('segmenter'),
        'propositionalizer': Module('propositionalizer'),
        'argument_relation': Module('argument_relation', "DAM", "01"),
        'hypothesis': Module('hypothesis', "roberta", "vanilla"),
        'scheme': Module('scheme', "roberta", "vanilla"), 
        'visualiser': Module('visualiser')
    }

    # Step 1: Turninator
    turninator_output = modules['turninator'].get_turns(input_data, True)
    logging.info('Turninator output: %s', turninator_output)

    # Step 2: Segmenter
    segmenter_output = modules['segmenter'].get_segments(turninator_output)
    logging.info('Segmenter output: %s', segmenter_output)

    # Step 3: Propositionalizer
    propositionalizer_output = modules['propositionalizer'].get_propositions(segmenter_output)
    logging.info('Propositionalizer output: %s', propositionalizer_output)

    # Step 4: Argument Relation Prediction
    argument_map_output = modules['argument_relation'].get_argument_map(propositionalizer_output)
    logging.info('Argument relation prediction output: %s', argument_map_output)

    # Additional Analysis
    claims = modules['argument_relation'].get_all_claims(argument_map_output)
    logging.info("Extracted claims: %s", claims)

    evidence = modules['argument_relation'].get_evidence_for_claim(
        "But this isn’t the time for vaccine nationalism", argument_map_output)
    logging.info("Evidence for claim: %s", evidence)

    # Hypothesis Prediction
    hypothesis_results = modules['hypothesis'].predict([
        "But this isn’t the time for vaccine nationalism",
        "Vaccine is useful to prevent infections."
    ])
    logging.info("Hypothesis prediction: %s", hypothesis_results)

    # Scheme Prediction
    scheme_results = modules['scheme'].predict([
        "But this isn’t the time for vaccine nationalism",
        "Vaccine is useful to prevent infections."
    ])
    logging.info("Scheme prediction: %s", scheme_results)

    # Visualize the argument map
    modules['visualiser'].visualise(argument_map_output)


def main() -> None:
    """Main function to run the argument mining pipeline."""
    input_data = (
        """Liam Halligan: Vaccines mark a major advance in human achievement since the """
        """enlightenment into the 19th Century and Britain’s been at the forefront of """
        """those achievements over the years and decades. But this isn’t the time for """
        """vaccine nationalism. I agree we should congratulate all the scientists, those """
        """in Belgium, the States, British scientists working in international teams here """
        """in the UK, with AstraZeneca.\n"""
        """Fiona Bruce: What about the logistical capabilities? They are obviously """
        """forefront now, now we’ve got a vaccine that’s been approved. It’s good -- I’m """
        """reassured that the British Army are going to be involved. They’re absolute world """
        """experts at rolling out things, complex logistic capabilities. This is probably """
        """going to be the biggest logistical exercise that our armed forces have undertaken """
        """since the Falklands War, which I’m old enough to remember, just about. So, as a """
        """neutral I’d like to see a lot of cross-party cooperation, and I’m encouraged with """
        """Sarah’s tone, everybody wants to see us getting on with it now. They don’t want """
        """to see competition on whose vaccine is best. There will be some instances where """
        """the Pfizer vaccine works better, another where you can’t have cold refrigeration, """
        """across the developing world as well, a cheaper vaccine like the AstraZeneca works """
        """better. Let’s keep our fingers crossed and hope we make a good job of this."""
    )

    process_pipeline(input_data)


if __name__ == "__main__":
    main()
```

#### Output

<details>
<summary>Click to expand the output in JSON format</summary>

```json
{
  "AIF": {
    "nodes": [
      {
        "text": "Vaccines mark a major advance in human achievement since the enlightenment into the 19th Century and Britain’s been at the forefront of those achievements over the years and decades",
        "type": "L",
        "nodeID": 2
      },
      {
        "text": "But this isn’t the time for vaccine nationalism",
        "type": "L",
        "nodeID": 3
      },
      {
        "text": "I agree we should congratulate all the scientists, those in Belgium, the States, British scientists working in international teams here in the UK, with AstraZeneca",
        "type": "L",
        "nodeID": 4
      },
      {
        "text": "What about the logistical capabilities",
        "type": "L",
        "nodeID": 5
      },
      {
        "text": "They are obviously forefront now, now we’ve got a vaccine that’s been approved",
        "type": "L",
        "nodeID": 6
      },
      {
        "text": "It’s good -- I’m reassured that the British Army are going to be involved",
        "type": "L",
        "nodeID": 7
      },
      {
        "text": "They’re absolute world experts at rolling out things, complex logistic capabilities",
        "type": "L",
        "nodeID": 8
      },
      {
        "text": "This is probably going to be the biggest logistical exercise that our armed forces have undertaken since the Falklands War, which I’m old enough to remember, just about",
        "type": "L",
        "nodeID": 9
      },
      {
        "text": "So, as a neutral I’d like to see a lot of cross-party cooperation, and I’m encouraged with Sarah’s tone, everybody wants to see us getting on with it now",
        "type": "L",
        "nodeID": 10
      },
      {
        "text": "They don’t want to see competition on whose vaccine is best",
        "type": "L",
        "nodeID": 11
      },
      {
        "text": "There will be some instances where the Pfizer vaccine works better, another where you can’t have cold refrigeration, across the developing world as well, a cheaper vaccine like the AstraZeneca works better",
        "type": "L",
        "nodeID": 12
      },
      {
        "text": "Let’s keep our fingers crossed and hope we make a good job of this",
        "type": "L",
        "nodeID": 13
      },
      {
        "text": "Vaccines mark a major advance in human achievement since the enlightenment into the 19th Century and Britain’s been at the forefront of those achievements over the years and decades",
        "type": "I",
        "nodeID": 14
      },
      {
        "text": "Default Illocuting",
        "type": "YA",
        "nodeID": 15
      },
      {
        "text": "But this isn’t the time for vaccine nationalism",
        "type": "I",
        "nodeID": 16
      },
      {
        "text": "Default Illocuting",
        "type": "YA",
        "nodeID": 17
      },
      {
        "text": "I agree we should congratulate all the scientists, those in Belgium, the States, British scientists working in international teams here in the UK, with AstraZeneca",
        "type": "I",
        "nodeID": 18
      },
      {
        "text": "Default Illocuting",
        "type": "YA",
        "nodeID": 19
      },
      {
        "text": "What about the logistical capabilities",
        "type": "I",
        "nodeID": 20
      },
      {
        "text": "Default Illocuting",
        "type": "YA",
        "nodeID": 21
      },
      {
        "text": "They are obviously forefront now, now we’ve got a vaccine that’s been approved",
        "type": "I",
        "nodeID": 22
      },
      {
        "text": "Default Illocuting",
        "type": "YA",
        "nodeID": 23
      },
      {
        "text": "It’s good -- I’m reassured that the British Army are going to be involved",
        "type": "I",
        "nodeID": 24
      },
      {
        "text": "Default Illocuting",
        "type": "YA",
        "nodeID": 25
      },
      {
        "text": "They’re absolute world experts at rolling out things, complex logistic capabilities",
        "type": "I",
       

 "nodeID": 26
      },
      {
        "text": "Default Illocuting",
        "type": "YA",
        "nodeID": 27
      },
      {
        "text": "This is probably going to be the biggest logistical exercise that our armed forces have undertaken since the Falklands War, which I’m old enough to remember, just about",
        "type": "I",
        "nodeID": 28
      },
      {
        "text": "Default Illocuting",
        "type": "YA",
        "nodeID": 29
      },
      {
        "text": "So, as a neutral I’d like to see a lot of cross-party cooperation, and I’m encouraged with Sarah’s tone, everybody wants to see us getting on with it now",
        "type": "I",
        "nodeID": 30
      },
      {
        "text": "Default Illocuting",
        "type": "YA",
        "nodeID": 31
      },
      {
        "text": "They don’t want to see competition on whose vaccine is best",
        "type": "I",
        "nodeID": 32
      },
      {
        "text": "Default Illocuting",
        "type": "YA",
        "nodeID": 33
      },
      {
        "text": "There will be some instances where the Pfizer vaccine works better, another where you can’t have cold refrigeration, across the developing world as well, a cheaper vaccine like the AstraZeneca works better",
        "type": "I",
        "nodeID": 34
      },
      {
        "text": "Default Illocuting",
        "type": "YA",
        "nodeID": 35
      },
      {
        "text": "Let’s keep our fingers crossed and hope we make a good job of this",
        "type": "I",
        "nodeID": 36
      },
      {
        "text": "Default Illocuting",
        "type": "YA",
        "nodeID": 37
      }
    ]
  }
}
```

</details>


## ⚙️ API Reference

For detailed API documentation, please refer to the [official documentation](https://wiki.arg.tech/books/amf) or 
check out the source code on [GitHub](https://github.com/arg-tech/amf).

## 🤝 Contributing

We welcome contributions to AMF! To get started:

1. **Fork the Repository**  
   Fork AMF to your GitHub account.

2. **Clone Your Fork**  
   ```bash
   git clone https://github.com/your-username/amf.git
   ```

3. **Create a Branch**  
   ```bash
   git checkout -b my-feature-branch
   ```

4. **Make Changes**  
   Implement your feature or fix. Follow our [guidelines](CONTRIBUTING.md).

5. **Test Your Changes**  
   Add and run tests to ensure everything works.

6. **Commit and Push**  
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin my-feature-branch
   ```

7. **Create a Pull Request**  
   Submit a PR on GitHub with details about your changes.

### Resources

- [Contributing Guidelines](CONTRIBUTING.md)
- [Issue Tracker](https://github.com/arg-tech/amf/issues)

Thank you for contributing!


## 📝 License

The AMF is licensed under the GNU General Public License (GPL) v3.0, with additional custom terms.

### Custom License Terms
- **Commercial Use**: To use this software for commercial purposes, please contact us for licensing arrangements.
- **Non-commercial Use**: You may use, modify, and distribute this software freely for non-commercial purposes, as long as you adhere to the GPL v3.0 terms.

For more detailed information about the GPL v3.0 license, visit the [GPL License](https://www.gnu.org/licenses/gpl-3.0.html) page.
