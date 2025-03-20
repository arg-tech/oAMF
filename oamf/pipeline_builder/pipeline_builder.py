import requests
import os
import tempfile
import json
import logging
from collections import deque


class PipelineBuilder:
    def __init__(self,Deployer):
        self.deployer = Deployer

    def _build_dependency_graph(self, pipeline_graph):
        """Build the dependency graph from the pipeline specification."""
        # Initialize an empty list for each module to hold dependencies
        module_dependencies = {module: [] for module in self.deployer.modules.keys()}
        for dependency in pipeline_graph:
            # Check if the dependency is a tuple where the second element is a list of dependencies
            if isinstance(dependency[1], list):
                for dep in dependency[1]:
                    module_dependencies[dependency[0]].append(dep)
            else:
                module_dependencies[dependency[0]].append(dependency[1])

        return module_dependencies
    def resolve_dependencies(self, pipeline_graph):
        # Create a dictionary to track dependencies
        module_dependencies = self._build_dependency_graph(pipeline_graph)
        #print("the whole row module dependencies", module_dependencies)
        # List to track the visited modules
        visited = set()

        def visit(module, stack):
            if module in stack:
                raise ValueError(f"Circular dependency detected: {' -> '.join(stack + [module])}")
            if module in visited:
                return
            visited.add(module)
            stack.append(module)
            for dep in module_dependencies.get(module, []):
                visit(dep, stack)
            stack.pop()

        # Check each module
        for module in module_dependencies:
            visit(module, [])
        return module_dependencies



    def new_pipeline(self, pipeline_graph_with_tags):
        """
        Install and set up only the modules specified in the pipeline, with tag tracking.
        :param pipeline_graph: List of module names and edges (dependencies) in the pipeline.
        :param tag_to_module: Dictionary mapping tags to module names.
        """

        # Convert tag-based pipeline to actual module-based pipeline
        tag_to_module = self.deployer.modules_to_load
        pipeline_graph = [(tag_to_module[src], tag_to_module[dst]) for src, dst in pipeline_graph_with_tags]       
        execution_pipeline = {}  # Graph representation
        ordered_modules = self.resolve_dependencies(pipeline_graph)


        # To track modules that have been added to the execution pipeline
        added_to_pipeline = set()

        def add_module(module_name, tag=None):
            """
            Process and add a module to the pipeline graph, maintaining dependencies.
            :param module_name: The name of the module to add.
            :param tag: The tag associated with this module (for tracking).
            """
            if module_name in added_to_pipeline:
                return  # Skip if the module is already processed

            module = self.deployer.modules.get(module_name)
            if module:
                module_url = module['url']
                module_type = module['type']
                route = module['route']
                destination = os.path.join(self.deployer.modules_dir, module_name)
                try:
                    if module_type == "repo":
                        print(f"Processing module '{module_name}' of type '{module_type}'...")
                        # Check if the module is already cloned
                        if not os.path.exists(destination):
                            self.deployer.clone_repository(module_url, destination)
                        else:
                            print(f"Module '{module_name}' already cloned. Skipping clone.")
                        # Check if the container is already running
                        if not self.deployer.is_container_running(module_name):
                            self.deployer.ensure_docker_setup(destination)
                            self.deployer.build_docker_image(destination)
                            self.deployer.start_docker_container(destination)
                        else:
                            print(f"Container for module '{module_name}' is already running. Skipping Docker setup.")
                        # Get the service port from the compose file
                        port = self.deployer.get_service_port_from_compose(destination, service_name=module_name)
                        execution_pipeline[module_name] = {
                            "name": module_name,
                            "url": f"http://localhost:{port}/{route}",
                            "dependencies": []  # Store dependencies in the graph
                        }
                    elif module_type == "ws":
                        print(f"Module '{module_name}' is of type 'ws'. No local setup needed.")
                        execution_pipeline[module_name] = {
                            "name": module_name,
                            "url": module_url,
                            "dependencies": []  # Store dependencies in the graph
                        }
                    else:
                        print(f"Unsupported module type '{module_type}' for module '{module_name}'. Skipping...")
                except Exception as e:
                    print(f"Failed to set up module '{module_name}': {str(e)}")

                # Mark module as added to the pipeline
                added_to_pipeline.add(module_name)

                # If a tag was passed, associate it in the execution pipeline
                if tag:
                    execution_pipeline[module_name]["tag"] = tag
        # Iterate over each module and its dependencies in the resolved graph
        for module_name, dependencies in ordered_modules.items():
            print(f"Processing module '{module_name}' and its dependencies...")

            # First, process the module itself (if it hasn't been processed already)
            # We need to ensure that we fetch the correct tag for this particular module
            tags_for_module = [tag for tag, mod_name in tag_to_module.items() if mod_name == module_name]
            
            # If there are multiple tags for the same module, we associate all of them in the execution pipeline
            for tag in tags_for_module:
                add_module(module_name, tag)

            # Then process each of its dependencies
            for dep in dependencies:
                tags_for_module = [tag for tag, mod_name in tag_to_module.items() if mod_name == dep]
                for tag in tags_for_module:
                    add_module(dep,tag)
                # Add dependency relationship in the graph
                execution_pipeline[module_name]["dependencies"].append(dep)



        return self._create_pipeline_executor(execution_pipeline, tag_to_module)


    def _create_pipeline_executor(self, execution_graph, tag_to_module):
        """
        Creates a pipeline execution function based on a dependency-aware execution order, with tag tracking.
        :param execution_graph: Dictionary representing the execution graph.
        :param tag_to_module: Dictionary mapping tags to module names.
        :return: Callable pipeline executor.
        """

        reverse_graph = {module: [] for module in execution_graph}

        # Reverse dependencies graph: Find which modules depend on each module
        for prerequisite, dependents in execution_graph.items():
            for dependent in dependents["dependencies"]:
                reverse_graph[dependent].append(prerequisite)

        print("Reverse dependency graph:", reverse_graph)

        executable_modules = [mod for mod, deps in reverse_graph.items() if not deps]
        module_outputs = {}
        print("executable_modules==========", executable_modules)
        def pipeline_executor(input_file):
            """Executes the pipeline following the dependency graph."""
            processed_modules = set()
            execution_queue = deque(executable_modules)
            module_outputs.update({mod: input_file for mod in executable_modules})
            previous_module = None

            while execution_queue:
                module_name = execution_queue.popleft()  # Process one module at a time
                module = execution_graph[module_name]

          

                # Get the tag for the current module
                module_tag = module.get("tag", "Unknown")

                # Identify the module providing the input for this module
                input_sources = [dep for dep in reverse_graph[module_name] if dep in module_outputs]
                input_modules = [tag_to_module.get(dep, dep) for dep in input_sources]

                # Print execution details, including the module that provides the input
                input_details = " and ".join(input_modules) if input_modules else "Original input"
                print(f"Executing module '{module_name}' (tag: {module_tag}), input provided by {module['url']}...")

                self.deployer.wait_for_service(module['url'])

                input_files = [module_outputs[dep] for dep in reverse_graph[module_name] if dep in module_outputs]
                if not input_files:
                    input_files = [input_file]  # Default to original input if no dependencies

                current_file_path = input_files[0]

                with open(current_file_path, "rb") as file_data:
                    file = {'file': (os.path.basename(current_file_path), file_data)}

                    try:
                        response = requests.post(module["url"], files=file)

                        if response.status_code == 200:
                            json_response = response.json()
                            #print(f"Module '{module_name}' output: {json_response}")

                            with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.json') as temp_file:
                                json.dump(json_response, temp_file)
                                temp_file_path = temp_file.name
                                module_outputs[module_name] = temp_file_path
                            print(f"Successfully processed '{module_name}'. Output saved at {temp_file_path}")

                            processed_modules.add(module_name)

                            # Add dependent modules to the execution queue
                            for dependent in execution_graph[module_name]["dependencies"]:
                                if all(dep in processed_modules for dep in reverse_graph[dependent]):
                                    execution_queue.append(dependent)

                        else:
                            print(f"Failed at '{module_name}' with status {response.status_code}: {response.text}")
                            break

                    except Exception as e:
                        logging.error(f"Error processing module '{module_name}': {str(e)}")
                        break
                previous_module = module_tag

            return module_outputs.get(list(execution_graph.keys())[-1], input_file)

        return pipeline_executor


    



