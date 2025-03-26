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
        Install and set up only the modules specified in the pipeline, using tag tracking.
        :param pipeline_graph_with_tags: List of tuples of tag-based edges (dependencies) in the pipeline.
        """
        # Convert tag-based pipeline to actual module-based pipeline
        tag_to_module = self.deployer.modules_to_load
        pipeline_graph = pipeline_graph_with_tags  # The graph is now entirely tag-based.

        # Create a set of tags that are explicitly part of the pipeline
        pipeline_tags = {tag for edge in pipeline_graph for tag in edge}

        execution_pipeline = {}  # Graph representation
        ordered_modules = self.resolve_dependencies(pipeline_graph)


        # Track which repositories have already been deployed
        deployed_repos = set()

        # Track which tags have been processed
        added_to_pipeline = set()

        def add_module(tag):
            """
            Process and add a module to the pipeline graph, maintaining dependencies.
            :param tag: The tag associated with this module.
            """
            if tag in added_to_pipeline:
                return  # Skip if the module (tag) is already processed

            # Only process tags that are part of the pipeline
            if tag not in pipeline_tags:
                return

            # Retrieve module details from the tag
            module = self.deployer.modules.get(tag)
            if not module:
                print(f"Warning: No module found for tag '{tag}'. Skipping...")
                return

            module_url = module['url']
            module_type = module['type']
            route = module['route']
            repo_name = module['repo_name']  # Unique repo name
            destination = os.path.join(self.deployer.modules_dir, repo_name)


            print(f"Processing module with tag '{tag}' -> Repo: '{repo_name}'")

            try:
                if module_type == "repo":
                    # Deploy the repository only once per repo_name
                    if repo_name not in deployed_repos:
                        print(f"Deploying repository '{repo_name}'...")
                        if not os.path.exists(destination):
                            self.deployer.clone_repository(module_url, destination)
                        else:
                            print(f"Repository '{repo_name}' already cloned. Skipping clone.")

                        if not self.deployer.is_container_running(repo_name):
                            self.deployer.ensure_docker_setup(destination)
                            self.deployer.build_docker_image(destination)
                            self.deployer.start_docker_container(destination)
                        else:
                            print(f"Container for repository '{repo_name}' is already running. Skipping setup.")

                        # Mark repository as deployed
                        deployed_repos.add(repo_name)

                    # Get the service port from the compose file
                    
                    service_name, cobtainer_name = self.deployer.get_service_and_container_name(destination)
                    print("service_name'''''''''''''''''''''''''''''''''''''''''''''''''''''''''", service_name)
                    port = self.deployer.get_service_port_from_compose(destination, service_name=service_name)
                    print("port'''''''''''''''''''''''''''''''''''''''''''''''''''''''''", port)
                    execution_pipeline[tag] = {
                        "name": tag,  # Keep using the tag in the pipeline
                        "url": f"http://localhost:{port}/{route}",
                        "dependencies": []  # Store dependencies in the graph
                    }

                elif module_type == "ws":
                    print(f"Module '{repo_name}' is of type 'ws'. No local setup needed.")
                    execution_pipeline[tag] = {
                        "name": tag,
                        "url": module_url,
                        "dependencies": []  # Store dependencies in the graph
                    }

                else:
                    print(f"Unsupported module type '{module_type}' for module '{tag}'. Skipping...")

            except Exception as e:
                print(f"Failed to set up module '{tag}': {str(e)}")

            # Mark tag as added to the pipeline
            added_to_pipeline.add(tag)

            execution_pipeline[tag]["tag"] = tag

        # Iterate over each tag and its dependencies in the resolved graph
        for tag, dependencies in ordered_modules.items():
            if tag not in pipeline_tags:
                continue  # Skip tags that are not part of the pipeline

            print(f"Processing module '{tag}' and its dependencies...")

            # First, process the module itself
            add_module(tag)

            # Then process each of its dependencies
            for dep in dependencies:
                if dep not in pipeline_tags:
                    continue  # Skip dependencies that are not part of the pipeline

                add_module(dep)

                # Add dependency relationship in the graph
                execution_pipeline[tag]["dependencies"].append(dep)

        print("Final Execution Pipeline:", execution_pipeline)
        return self._create_pipeline_executor(execution_pipeline, tag_to_module)

    

    def _create_pipeline_executor(self, execution_graph, tag_to_module):
        """
        Creates a pipeline execution function based on a dependency-aware execution order, with tag tracking.
        :param execution_graph: Dictionary representing the execution graph.
        :param tag_to_module: Dictionary mapping tags to module names.
        :return: Callable pipeline executor.
        """

        # Collect all tags, including those from dependencies
        all_tags = set(data["tag"] for data in execution_graph.values())  # Tags from execution_graph
        all_tags.update(dep for module in execution_graph.values() for dep in module["dependencies"])  # Tags from dependencies

        # Initialize reverse_graph correctly
        #reverse_graph = {tag: [] for tag in all_tags}

        # Ensure execution_graph contains all referenced modules, even if they have no dependencies
        for tag in all_tags:
            if tag not in execution_graph:
                execution_graph[tag] = {"name": tag, "url": "", "dependencies": [], "tag": tag}  # Default structure

        # Initialize reverse_graph correctly
        reverse_graph = {tag: [] for tag in all_tags}


        # Reverse dependencies graph: Find which modules depend on each module
        for module_name, module_data in execution_graph.items():
            for dep in module_data["dependencies"]:
                reverse_graph[dep].append(module_name)  # Correctly store dependents

        print("Reverse dependency graph:", reverse_graph)

        # Identify modules with no dependencies (entry points)
        executable_modules = [mod for mod, deps in reverse_graph.items() if not deps]
        module_outputs = {}
        module_outputs_json = {}

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

                # Identify the modules providing input for this module
                input_sources = [dep for dep in reverse_graph.get(module_name, []) if dep in module_outputs]
                #input_modules = [tag_to_module.get(dep, dep) for dep in input_sources]

                # Print execution details
                #input_details = " and ".join(input_modules) if input_modules else "Original input"
                print(f"Executing module '{module_name}' (tag: {module_tag})")

                self.deployer.wait_for_service(module['url'])

                input_files = [module_outputs[dep] for dep in input_sources if dep in module_outputs]
                if not input_files:
                    input_files = [input_file]  # Default to original input if no dependencies

                current_file_path = input_files[0]

                with open(current_file_path, "rb") as file_data:
                    file = {'file': (os.path.basename(current_file_path), file_data)}

                    try:
                        response = requests.post(module["url"], files=file)

                        if response.status_code == 200:
                            json_response = response.json()

                            with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.json') as temp_file:
                                json.dump(json_response, temp_file)
                                temp_file_path = temp_file.name
                                module_outputs[module_name] = temp_file_path
                                module_outputs_json[module_name] = json_response
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



            return module_outputs.get(list(execution_graph.keys())[-1], input_file), module_outputs_json.get(list(execution_graph.keys())[-1], input_file)

        return pipeline_executor





    



