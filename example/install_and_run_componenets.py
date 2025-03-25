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
    ("https://github.com/arg-tech/default_turninator.git", "repo", "turninator-01", "turninator1"),
    ("https://github.com/arg-tech/default_turninator.git", "repo", "turninator-01", "turninator2"),
    ("https://github.com/arg-tech/proposition-unitizer.git", "repo", "propositionUnitizer-01", "propositionUnitiser1"),
     ("https://github.com/arg-tech/proposition-unitizer.git", "repo", "propositionUnitizer-01", "propositionUnitiser2"),
    #("http://default-proposition-unitiser.amfws.arg.tech/propositionUnitizer-01", "ws", "propositionUnitizer-01", "propositionUnitiser1"),
     #("http://default-proposition-unitiser.amfws.arg.tech/propositionUnitizer-01", "ws", "propositionUnitizer-01", "propositionUnitiser2"),
    ("http://bert-te.amfws.arg.tech/bert-te", "ws", "bert-te", "bert-te3"),
    ("https://github.com/arg-tech/bert-te.git", "repo", "bert-te", "bert-te1"),
    ("https://github.com/arg-tech/bert-te.git", "repo", "bert-te", "bert-te2"),
    ("https://github.com/arg-tech/default_segmenter.git", "repo", "segmenter-01", "segmenter1"),
    ("https://github.com/arg-tech/default_segmenter.git", "repo", "segmenter-01", "segmenter2")
    
]

# Load and deploy the specified modules
oamf.load_modules(modules_to_load)

# Define the pipeline using module tags
pipeline_graph = [
    ("turninator1", "propositionUnitiser1"),   # "turninator" outputs to "segmenter"
    ("turninator2", "propositionUnitiser2"),      # "segmenter" outputs to "bert-te"
    ("propositionUnitiser1", "segmenter1"),      # "segmenter" outputs to "bert-te"
    ("propositionUnitiser2", "segmenter2"),      # "segmenter" outputs to "bert-te"
    ("segmenter2", "bert-te2"),      # "segmenter" outputs to "bert-te"
    ("bert-te2", "bert-te3")      # "segmenter" outputs to "bert-te"
]







# Execute the pipeline using the defined workflow and input file in xAIF format

output_path, result = oamf.pipelineExecutor(pipeline_graph, input_file)



# Override the manually defined pipeline with one built using n8n (if applicable)
oamf.pipelineExecutor(pipeline_graph, input_file, workflow_file)

# Export the pipeline from n8n into an executable and editable Python script
#oamf.export_n8n_workflow_to_python_script(workflow_file, input_file)
