import json
import tempfile
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
    ("turninator1", "segmenter1"),   # "turninator" outputs to "segmenter"    
    ("segmenter1", "propositionUnitiser1"),  # "segmenter1" outputs to "propositionUnitiser1" 
    ("propositionUnitiser1", "bert-te2")     # "segmenter" outputs to "bert-te"
]

# Execute the pipeline using the defined workflow and input file in xAIF format

output_path, result = oamf.pipelineExecutor(pipeline_graph, input_file, workflow_file)

print(result)

"""
# Override the manually defined pipeline with one built using n8n (if applicable)
output_path, result  = oamf.pipelineExecutor(pipeline_graph, input_file, workflow_file)

# Export the pipeline from n8n into an executable and editable Python script
#oamf.export_n8n_workflow_to_python_script(workflow_file, input_file)
print(output_path, result)

# Using free inout text
xaif_data = AIF("Scotland can be really cold at times. However Dundee is the suniest city in Scotland.") 

# Write temporary JSON
def write_temp_json(data):
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_file:
        json.dump(data, temp_file, indent=4)
        temp_file_path = temp_file.name
    print(f"Temporary JSON file created at: {temp_file_path}")
    return temp_file_path
input_file_path = write_temp_json(xaif_data.xaif)  # save xAIF to a file


# Execute the pipeline with the specified graph and input file
# This returns the output path (where the result is saved) and the output data as JSON
output_path, output_json = oamf.pipelineExecutor(pipeline_graph, input_file_path)


print(output_path, output_json)

"""