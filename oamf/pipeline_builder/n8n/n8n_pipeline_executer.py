import json
import requests
import tempfile
import io
import os
import networkx as nx  # For graph-based execution
from collections import defaultdict, deque

class N8NPipelineExecutor:
    def __init__(self, pipeline_path, input_file):
        with open(pipeline_path, 'r') as f:
            self.data = json.load(f)
        self.graph, self.http_nodes = self.extract_http_nodes_and_graph()
        self.input_file = input_file

        self.export_http_nodes = self.extract_http_nodes_and_order(self.data)
        if not self.export_http_nodes:
            print("No HTTP nodes found in the pipeline.")
            exit()       
    
    def extract_http_nodes_and_graph(self):
        nodes = self.data['nodes']
        connections = self.data['connections']
        
        G = nx.DiGraph()
        http_nodes = {node['name']: node for node in nodes if node['type'] == 'n8n-nodes-base.httpRequest'}

        for connection_node, connection_data in connections.items():
            for conn_list in connection_data['main']:
                for conn in conn_list:
                    if isinstance(conn, dict) and 'node' in conn:
                        G.add_edge(connection_node, conn['node'])
        
        if not nx.is_directed_acyclic_graph(G):
            print("Cycle detected! The graph has circular dependencies.")
            return None, None
        
        return G, http_nodes
    
    def save_response_to_temp_file(self, response_data):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file_path = temp_file.name
        
        with open(temp_file_path, 'w') as f:
            json.dump(response_data, f) if isinstance(response_data, dict) else f.write(response_data)
        
        return temp_file_path
    
    def get_input_type(self, http_node):
        return "file" if http_node['parameters'].get('sendBinaryData', False) else "text"
    
    def get_first_http_node(self):
        execution_order = list(nx.topological_sort(self.graph))
        for node_name in execution_order:
            if node_name in self.http_nodes:
                return self.http_nodes[node_name]
        return None
    
    def get_dependency_tuples(self):
        return list(self.graph.edges())
    
    def execute_pipeline(self):
        execution_order = list(nx.topological_sort(self.graph))
        print("Execution Order:", execution_order)
        print("Dependencies:", self.get_dependency_tuples())
        
        pipeline_result = {}
        pipeline_result_xaif = {}
        first_http_node = self.get_first_http_node()
        input_type = self.get_input_type(first_http_node) if first_http_node else "text"
        
        input_data = {'file': ('file.json', open(self.input_file, 'rb'))} \
            if input_type == "file" else {'text': 'This is some sample text input.'}
        
        for node_name in execution_order:
            if node_name not in self.http_nodes:
                continue
            
            node = self.http_nodes[node_name]
            url = node['parameters'].get('url')
            method = node['parameters'].get('requestMethod', 'GET')
            
            if not url:
                print(f"Skipping {node_name} as it has no URL.")
                continue
            
            response = requests.request(method, url, files=input_data if input_type == "file" else json==input_data)
            print(f"Response from {node_name} (HTTP {method} {url}): {response.status_code}")
            #print(response.text)
            
            if response.status_code == 200:
                response_data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
                input_data = {'file': ('response.json', open(self.save_response_to_temp_file(response_data), 'rb'))} if 'sendBinaryData' in node['parameters'] and node['parameters']['sendBinaryData'] else response_data
            else:
                input_data = response.text
            
            #pipeline_result[node_name] = input_data
            #pipeline_result_xaif[node_name] = response.text
            pipeline_result[node_name] = (input_data, response.text)

        #return pipeline_result.get(list(execution_graph.keys())[-1], input_file), module_outputs_json.get(list(execution_graph.keys())[-1], input_file)
        
        #return pipeline_result
        # Get the last executed node
        last_node = execution_order[-1] if execution_order else None
        path, xaif = pipeline_result.get(last_node, (None, None))
        return path, xaif


    def extract_http_nodes_and_order(self, pipeline_data):
        nodes = pipeline_data['nodes']
        connections = pipeline_data['connections']
        
        node_by_name_http = {node['name']: node for node in nodes if node['type'] == 'n8n-nodes-base.httpRequest'}
        node_by_name = {node['name']: node for node in nodes}
        node_names = list(node_by_name.keys())  # List of node names

        graph = defaultdict(list)
        in_degree = {node_name: 0 for node_name in node_names}

        for connection_node, connection_data in connections.items():
            for conn_list in connection_data['main']:
                for conn in conn_list:
                    if isinstance(conn, dict) and 'node' in conn:
                        source_node_name = connection_node
                        target_node_name = conn['node']
                        graph[source_node_name].append(target_node_name)
                        in_degree[target_node_name] += 1

        def detect_cycle(graph):
            visited = set()
            stack = set()

            def dfs(node):
                if node in stack:
                    return True
                if node in visited:
                    return False
                visited.add(node)
                stack.add(node)
                for neighbor in graph[node]:
                    if dfs(neighbor):
                        return True
                stack.remove(node)
                return False

            for node in node_names:
                if node not in visited:
                    if dfs(node):
                        return True
            return False

        if detect_cycle(graph):
            print("Cycle detected! The graph has circular dependencies.")
            return []

        queue = deque([node_name for node_name in node_names if in_degree[node_name] == 0])
        ordered_nodes = []

        while queue:
            node_name = queue.popleft()
            ordered_nodes.append(node_by_name[node_name])

            for neighbor in graph[node_name]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(ordered_nodes) != len(node_names):
            print("Cycle detected! The graph has circular dependencies.")
            return []

        filtered_http_nodes = [entry for entry in ordered_nodes if entry['type'] == 'n8n-nodes-base.httpRequest']
        
        return filtered_http_nodes


    def generate_run_script(self,destination_path=None):
        # Save HTTP nodes to a file

        #graph_path = 'oamf/pipeline_builder/n8n/http_nodes.json'
        graph_path = 'oAMF/oamf/pipeline_builder/n8n/http_nodes.json'

        with open(graph_path, 'w') as f:
            json.dump(self.export_http_nodes, f)
        # Write the execution part of the code to a separate file 'run_pipeline.py'
        run_pipeline_code = '''
import json
import requests
import tempfile
import io

# Load the saved HTTP nodes
with open('oamf/pipeline_builder/n8n/http_nodes.json', 'r') as f:
    http_nodes = json.load(f)

# Function to save response data to a temporary file and return the file path
def save_response_to_temp_file(response_data):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name

    if isinstance(response_data, dict):
        with open(temp_file_path, 'w') as f:
            json.dump(response_data, f)
    elif isinstance(response_data, str):
        with open(temp_file_path, 'w') as f:
            f.write(response_data)

    return temp_file_path

# Function to identify the input type (file vs text) for a given HTTP node
def get_input_type(http_node):
    if 'sendBinaryData' in http_node['parameters'] and http_node['parameters']['sendBinaryData'] == True:
        return "file"
    else:
        return "text"

# Simulate the pipeline by making HTTP requests based on the nodes
def simulate_pipeline(http_nodes,input_file=None):
    data = {}
    
    input_data = None
    first_http_node = http_nodes[0]
    input_type = get_input_type(first_http_node)

    if input_type == "file":
        file_path = "'''+self.input_file+'''"  # Path to the file
        input_data = {'file': ('file.json', open(file_path, 'rb'))}
    else:
        input_data = {'text': 'This is some sample text input.'}

    for i, node in enumerate(http_nodes):
        url = node['parameters'].get('url')
        if not url:
            print(f"Skipping non-HTTP node {node['name']} because it doesn't have a URL.")
            continue
        method = node['parameters']['requestMethod']
        
        if input_type == "file":
            response = requests.request(method, url, files=input_data)
        else:
            response = requests.request(method, url, json=input_data)

        print(f"Response from {node['name']} (HTTP {method} {url}): {response.status_code}")
        print(response.text)
        
        #if response.status_code == 200:
        # For the next node, handle the response
        if response.status_code == 200:
            response_data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            
            # Handle file-based responses for subsequent nodes
            if 'sendBinaryData' in node['parameters'] and node['parameters']['sendBinaryData'] == True:
                # Save response to a temporary file and pass it as input to the next node
                file_path = save_response_to_temp_file(response_data)
                input_data = {'file': ('response.json', open(file_path, 'rb'))}
            else:
                input_data = response_data
        else:
            input_data = response.text

        # If it's the last node, capture the final result
        if i == len(http_nodes) - 1:
            data[node['name']] = input_data
    
    return data

# Function to handle non-serializable objects (e.g., file-like objects)
def handle_non_serializable_objects(obj):
    if isinstance(obj, dict):
        return {k: handle_non_serializable_objects(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [handle_non_serializable_objects(v) for v in obj]
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, io.IOBase):
        return "File object - cannot serialize"
    return obj

# Simulate the pipeline and capture the result
pipeline_result = simulate_pipeline(http_nodes)

# Ensure non-serializable objects are handled properly
pipeline_result = handle_non_serializable_objects(pipeline_result)

# Print the final pipeline results
print("\\nPipeline Result:")
print(pipeline_result)
'''



        # Save the generated code to 'run_pipeline.py'
        if destination_path:
            script_file_name = os.path.join(destination_path, 'run_pipeline.py')
        else:
            script_file_name = 'run_pipeline.py'

        with open(script_file_name, 'w') as f:
            f.write(run_pipeline_code)

        print(f"{script_file_name} has been generated.")

