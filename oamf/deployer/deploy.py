import time
import requests
import subprocess
import os
import shutil
import yaml
import urllib.parse
from requests.exceptions import ConnectionError


class Deployer:
    def __init__(self):
        self.modules_dir = os.path.join(os.getcwd(), "modules")
        os.makedirs(self.modules_dir, exist_ok=True)  # Ensure the modules directory exists
        self.modules = {}  # Dictionary to store module information dynamically
        self.edges = []  # List to store dependencies between modules
        self.modules_to_load = None

    def get_repo_name_from_url_(self, url):
        """Extract the repository name from the GitHub URL."""
        parsed_url = urllib.parse.urlparse(url)
        repo_name = parsed_url.path.split("/")[-1].replace(".git", "")
        return repo_name


    def get_service_and_container_name(self, project_path):
        """Extract the service name and container name from docker-compose.yml."""
        docker_compose_path = os.path.join(project_path, "docker-compose.yml")

        # Read the docker-compose.yml file
        with open(docker_compose_path, "r") as f:
            compose_data = yaml.safe_load(f)
        
        services = compose_data.get('services', {})
        
        if not services:
            raise ValueError("No services found in docker-compose.yml")
        
        service_name, service_details = next(iter(services.items()))  # Get the first (and only) service
        container_name = service_details.get('container_name', service_name)  # Default to service name if container_name not set
        
        return service_name, container_name




    def _loadmodule(self, name, url, module_type, route, tag):
        """
        Dynamically load a module by specifying its name, repository URL, and type.
        :param name: The name or tag for the module.
        :param url: The URL of the module's repository.
        :param module_type: The type of module (e.g., "repo" or "ws").
        :param route: The route or path to be used with the module.
        """
        repo_name = self.get_repo_name_from_url_(url)
        self.modules[tag] = {
            "url": url,
            "type": module_type,
            'route': route,
            "name": name,
            "repo_name": repo_name
        }
        print(f"Module '{name}' of type '{module_type}' loaded from {url}.")

    def add_edge(self, start, end):
        """Add an edge (dependency) between two modules."""
        self.edges.append((start, end))


    
    def _build_dependency_graph(self, pipeline_graph):
        """Build the dependency graph from the pipeline specification."""
        # Initialize an empty list for each module to hold dependencies
        module_dependencies = {module: [] for module in self.modules.keys()}

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



 
    def wait_for_service(self, url, timeout=600, retry_interval=15):
        """
        Wait until the service is up and accepting requests.
        :param url: The URL of the service.
        :param timeout: The maximum time to wait (in seconds).
        :param retry_interval: The time between each retry (in seconds).
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    print(f"Service at {url} is up and running!")
                    return True
            except ConnectionError:
                pass

            print(f"Waiting for service at {url} to be available...")
            time.sleep(retry_interval)

        raise TimeoutError(f"Service at {url} did not start within {timeout} seconds.")

    def clone_repository(self, repo_url, destination):
        """Clone a GitHub repository to the specified destination."""
        if os.path.exists(destination):
            shutil.rmtree(destination)  # Remove existing directory to avoid conflicts
        subprocess.check_call(["git", "clone", repo_url, destination])

    def ensure_docker_setup(self, project_path):
        """Ensure Docker setup exists or create it based on requirements.txt."""
        dockerfile_path = os.path.join(project_path, "Dockerfile")
        docker_compose_path = os.path.join(project_path, "docker-compose.yml")
        requirements_path = os.path.join(project_path, "requirements.txt")

        if os.path.exists(dockerfile_path) and os.path.exists(docker_compose_path):
            print(f"Found Dockerfile and docker-compose.yml for {project_path}.")
        elif os.path.exists(requirements_path):
            print(f"Creating Dockerfile and docker-compose.yml for {project_path} based on requirements.txt.")
            self.create_dockerfile(project_path, requirements_path)
        else:
            raise FileNotFoundError(
                f"Neither Dockerfile, docker-compose.yml, nor requirements.txt found in {project_path}."
            )

    def create_dockerfile(self, project_path, requirements_path):
        """Generate Dockerfile and docker-compose.yml based on requirements.txt."""
        dockerfile_content = f"""
        FROM python:3.9-slim
        WORKDIR /app
        COPY requirements.txt /app/requirements.txt
        RUN pip install --no-cache-dir -r /app/requirements.txt
        COPY . /app
        CMD ["python", "app.py"]
        """
        with open(os.path.join(project_path, "Dockerfile"), "w") as dockerfile:
            dockerfile.write(dockerfile_content)

        docker_compose_content = f"""
        version: '3.7'
        services:
          {project_path.split('/')[-1]}:
            build: .
            ports:
              - "5005:5005"
            volumes:
              - .:/app
        """

        with open(os.path.join(project_path, "docker-compose.yml"), "w") as docker_compose:
            docker_compose.write(docker_compose_content)

    def build_docker_image(self, project_path):
        """Build the Docker image using Docker Compose."""
        subprocess.check_call(["docker-compose", "-f", os.path.join(project_path, "docker-compose.yml"), "build"])

    def start_docker_container(self, project_path):
        """Start the Docker container for the project."""
        subprocess.check_call(["docker-compose", "-f", os.path.join(project_path, "docker-compose.yml"), "up", "-d"])

    def is_container_running(self, module_name):
        """Check if a container is already running."""
        try:
            result = subprocess.check_output(["docker", "ps", "--filter", f"ancestor={module_name}", "--format", "{{.Names}}"])
            return bool(result.strip())  # If a container name is found, it means it's running
        except subprocess.CalledProcessError:
            return False

    def get_service_port_from_compose(self, project_path, service_name="default_turninator"):
        """Get the service port from docker-compose.yml."""
        docker_compose_path = os.path.join(project_path, "docker-compose.yml")

        # Read the docker-compose.yml file
        with open(docker_compose_path, "r") as f:
            compose_data = yaml.safe_load(f)

        # Check if the service exists in the compose file
        service = compose_data.get('services', {}).get(service_name)

        if service and 'ports' in service:
            ports = service['ports']
            # Extract the first port mapping (e.g., "5006:5006")
            for port_mapping in ports:
                host_port, container_port = port_mapping.split(":")
                return host_port.strip()  # Return the host port
        else:
            raise ValueError(f"Service '{service_name}' or port mapping not found in {docker_compose_path}")

    # Function to extract repo name from URL
    def get_repo_name_from_url(self, url):
        """parse urls"""
        parsed_url = urllib.parse.urlparse(url)
        repo_name = parsed_url.path.split("/")[-1].replace(".git", "")
        return repo_name

    def load_modules(self, modules_to_load):
        # Dictionary to map tags to their corresponding module names
        tag_to_module = {}
        # Load modules dynamically, avoiding redundant deployments
        # Dictionary to track deployed modules (ensuring each module is deployed only once)
        deployed_modules = {}
        
        for url, module_type, route, tag in modules_to_load:
            module_name = f'{self.get_repo_name_from_url(url)}'
            '''
            if module_type == 'repo':
                repo_path = os.path.join(self.modules_dir, module_name)
                module_name, container_name = self.get_service_and_container_name(repo_path)
                module_name = f'{module_name}{container_name}'
            print("module_name --------------------------------------", module_name)
            #module_name = tag
            '''
            # Deploy the module only if it hasn't been deployed before
            
            if tag not in deployed_modules:
                deployed_modules[tag] = route  # Store deployed module with its assigned route
                self._loadmodule(module_name, url, module_type, route,tag)
            
            # Associate the tag with the actual module name
            tag_to_module[tag] = module_name  
        self.modules_to_load = tag_to_module
        return tag_to_module
    



