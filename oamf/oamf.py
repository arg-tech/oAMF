import os
import yaml
import subprocess
import shutil


class oAMF:
    def __init__(self, metadata_file):
        self.metadata_file = metadata_file
        self.modules_dir = os.path.join(os.getcwd(), "modules")
        os.makedirs(self.modules_dir, exist_ok=True)  # Ensure the modules directory exists
        self.projects = self.load_metadata()
        self.default_ports = self.projects.get("default_ports", {"start": 5000, "increment": 10})

    def load_metadata(self):
        """Load global metadata from the specified YAML file."""
        if not os.path.exists(self.metadata_file):
            raise FileNotFoundError(f"Metadata file {self.metadata_file} not found!")

        with open(self.metadata_file, 'r') as file:
            return yaml.safe_load(file)

    def load_project_metadata(self, project_path):
        """Load project-specific metadata from the config/metadata.yaml file."""
        metadata_path = os.path.join(project_path, "config", "metadata.yaml")

        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Project metadata file {metadata_path} not found in {project_path}!")

        with open(metadata_path, 'r') as file:
            return yaml.safe_load(file)

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

        # Check if Dockerfile and docker-compose.yml exist
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
        version: '3.8'
        services:
          app:
            build: .
            ports:
              - "{self.default_ports['start']}:{self.default_ports['start']}"
        """

        with open(os.path.join(project_path, "docker-compose.yml"), "w") as docker_compose:
            docker_compose.write(docker_compose_content)

    def build_docker_image(self, project_path):
        """Build Docker image for the specified project."""
        subprocess.check_call(["docker-compose", "-f", os.path.join(project_path, "docker-compose.yml"), "build"])

    def start_docker_container(self, project_path, port):
        """Start Docker container for the specified project."""
        subprocess.check_call([
            "docker-compose",
            "-f",
            os.path.join(project_path, "docker-compose.yml"),
            "up",
            "-d",
        ])

    def install_pipeline(self, pipeline_tags):
        """Install and set up only the modules specified in the pipeline based on project tags."""
        current_port = self.default_ports['start']

        for repo in self.projects.get('repositories', []):
            repo_url = repo['url']
            destination = os.path.join(self.modules_dir, os.path.basename(repo_url).replace('.git', ''))

            print(f"Cloning repository from {repo_url}...")
            try:
                self.clone_repository(repo_url, destination)

                # Load project-specific metadata
                project_metadata = self.load_project_metadata(destination)
                project_tag = project_metadata.get("AMF_Tag")

                if project_tag not in pipeline_tags:
                    print(f"Skipping module {project_tag} (not in pipeline).")
                    continue

                print(f"Processing module {project_tag}...")
                self.ensure_docker_setup(destination)
                self.build_docker_image(destination)
                self.start_docker_container(destination, current_port)
                print(f"Successfully set up {project_tag} on port {current_port}.")
                current_port += self.default_ports['increment']
            except Exception as e:
                print(f"Failed to set up module from {repo_url}: {str(e)}")
