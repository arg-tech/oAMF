from oamf import oAMF  # Import oAMF for pipeline execution
from xaif import AIF   # Import xaif for manipulating xAIF data

# Initialize the oAMF library
oamf = oAMF()

# Define file paths
input_file = "/Users/debelagemechu/projects/amf/caasr/example.json"  # Input xAIF data
workflow_file = "/Users/debelagemechu/projects/oAMF/example/workflow.json"  # Workflow downloaded from n8n

# Example: Initialize AIF with free text to generate xAIF format
# xaif_data = AIF("Sample input text.") 
# xaif_data.write_to_file(input_file)  # Optionally save xAIF to a file

# Modules to load: (URL, type ['repo' or 'ws'], deployment route, tag)
modules_to_load = [
    ("https://github.com/arg-tech/default_turninator.git", "repo", "turninator-01", "turninator"),
    ("https://github.com/arg-tech/default_segmenter.git", "repo", "segmenter-01", "segmenter"),
    ("http://bert-te.amfws.arg.tech/bert-te", "ws", "bert-te", "bert-te")
]

# Load and deploy the specified modules
oamf.load_modules(modules_to_load)

# Define the pipeline using module tags
pipeline_graph = [
    ("turninator", "segmenter"),   # "turninator" outputs to "segmenter"
    ("segmenter", "bert-te")      # "segmenter" outputs to "bert-te"
]

# Execute the pipeline using the defined workflow and input file in xAIF format
oamf.pipelineExecutor(pipeline_graph, input_file)

# Override the manually defined pipeline with one built using n8n (if applicable)
oamf.pipelineExecutor(pipeline_graph, input_file, workflow_file)

# Export the pipeline from n8n into an executable and editable Python script
oamf.export_n8n_workflow_to_python_script(workflow_file, input_file)
