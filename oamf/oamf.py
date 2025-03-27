
from oamf.pipeline_builder.n8n.n8n_pipeline_executer import N8NPipelineExecutor
from oamf.deployer.deploy import Deployer
from oamf.pipeline_builder.pipeline_builder import PipelineBuilder

class oAMF:
    def __init__(self):
        self.deployer = Deployer()
        self.pipe_builder = PipelineBuilder(self.deployer)
    def load_modules(self, modules_to_load):

        return self.deployer.load_modules(modules_to_load)
    
    def export_n8n_workflow_to_python_script(self,workflow_file, input_file,destination_path=None):
        #pipeline_simulator = HttpPipelineSimulator(workflow_file,input_file)
        pipeline_simulator = N8NPipelineExecutor(workflow_file, input_file)
        pipeline_simulator.generate_run_script(destination_path)

    def pipelineExecutor(self, pipeline_graph_with_tags,intput_file, workflow_file=None):
        if not workflow_file:
            pipeline_executor = self.pipe_builder.new_pipeline(pipeline_graph_with_tags)
            result_file_path, result_json = pipeline_executor(intput_file)
            return(f"Pipeline execution completed. Final result stored at: {result_file_path}", result_json)
        else:
            # Process the pipeline
            executor = N8NPipelineExecutor(workflow_file, intput_file)
            if executor.graph and executor.http_nodes:
                result_file_path, result_json = executor.execute_pipeline()                
                #return(f"Pipeline execution completed. Final result: {result}")
                return(f"Pipeline execution completed. Final result stored at: {result_file_path}", result_json)