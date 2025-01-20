from oamf import oAMF
print(oAMF)

# Path to metadata file
metadata_file = "/Users/debelagemechu/projects/oAMF/example/oamf_modules.yml"

# Initialize the library
manager = oAMF(metadata_file)

# Define the pipeline with module names (from metadata)
pipeline_modules = ["turninator", "segmenter"]

# Install and deploy the pipeline
manager.install_pipeline(pipeline_modules)

