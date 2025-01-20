import json
import requests
import tempfile
import io

# Load the pipeline JSON data
with open('/Users/debelagemechu/projects/oAMF_dev/oamf/My_workflow.json', 'r') as f:
    data = json.load(f)

from collections import deque


# Function to extract HTTP nodes and their connections in order
def extract_http_nodes_and_order(pipeline_data):
    nodes = pipeline_data['nodes']
    connections = pipeline_data['connections']
    http_nodes = []

    # Extract HTTP nodes
    for node in nodes:
        if node['type'] == 'n8n-nodes-base.httpRequest':
            http_nodes.append(node)

    # Create a dictionary for easy lookup of nodes by their ID
    node_by_id = {node['id']: node for node in http_nodes}

    # Create a dictionary for connections by "node"
    connections_by_node = {}
    reverse_connections = {}  # To track incoming connections for each node
    for node_id, connection in connections.items():
        connections_by_node[node_id] = connection['main']
        # Track reverse connections (incoming to each node)
        for conn in connection['main']:
            # Ensure we're accessing a dictionary with the expected key
            if isinstance(conn, dict) and 'node' in conn:
                if conn['node'] not in reverse_connections:
                    reverse_connections[conn['node']] = []
                reverse_connections[conn['node']].append(node_id)

    # Identify the starting node (nodes with no incoming HTTP connections)
    starting_nodes = []
    for node in http_nodes:
        node_id = node['id']
        # If node has no incoming HTTP connection or its incoming connection is not an HTTP node
        if node_id not in reverse_connections or not any(
            reverse_connections[node_id][0] in node_by_id for node_id in reverse_connections[node_id]
        ):
            starting_nodes.append(node_id)

    # Now order the nodes based on the adjacency list
    ordered_nodes = []
    visited = set()

    print("===============================", connections_by_node)
    print("================================================")

    # Iterate over each starting node and traverse its connections
    
    for start_node_id in starting_nodes:
        print("start_node_id--------------------------", start_node_id)
        # Process each node, respecting the order of dependencies
        nodes_to_process = [start_node_id]

        while nodes_to_process:
            node_id = nodes_to_process.pop(0)  # Process nodes in a queue (or you can use a stack if you prefer)
            if node_id in visited:
                continue
            visited.add(node_id)
            ordered_nodes.append(node_by_id[node_id])

            # Add all connected nodes to the list
            if node_id in connections_by_node:
                for connection in connections_by_node[node_id]:
                    if isinstance(connection, dict) and 'node' in connection:  # Check the structure
                        if connection['node'] not in visited:
                            nodes_to_process.append(connection['node'])

    print("---------------", ordered_nodes)
    print("---------------")

    return ordered_nodes


# Function to extract HTTP nodes and their connections in order
def extract_http_nodes_and_order2(pipeline_data):
    nodes = pipeline_data['nodes']
    connections = pipeline_data['connections']
    http_nodes = []
    
    # Extract HTTP nodes
    for node in nodes:
        if node['type'] == 'n8n-nodes-base.httpRequest':
            http_nodes.append(node)
    
    # Create a dictionary for easy lookup of nodes by their ID
    node_by_id = {node['id']: node for node in http_nodes}


    
    # Create a dictionary for connections by "node"
    connections_by_node = {}
    for node_id, connection in connections.items():
        connections_by_node[node_id] = connection['main']
    
    # Now order the nodes based on the connections
    ordered_nodes = []
    visited = set()

    print("===============================",connections_by_node)
    print("================================================")

    # A helper function to perform a depth-first search (DFS) and maintain order
    def dfs(node_id):
        if node_id in visited:
            return
        visited.add(node_id)
        ordered_nodes.append(node_by_id[node_id])
        if node_id in connections_by_node:
            for connection in connections_by_node[node_id]:
                dfs(connection['node'])

    # Start DFS from all HTTP nodes (generic way without hardcoding the first node)
    for node in http_nodes:
        if node['id'] not in visited:
            dfs(node['id'])
    print("---------------", ordered_nodes)
    print("---------------")

    return ordered_nodes

# Extract HTTP nodes in the correct order based on connections
http_nodes = extract_http_nodes_and_order(data)

# If no HTTP nodes are found, exit
if not http_nodes:
    print("No HTTP nodes found in the pipeline.")
    exit()

# Print extracted HTTP nodes in the correct order
print("\nExtracted HTTP Nodes (Order of Input/Output):")
for i, node in enumerate(http_nodes):
    print(f"Node {i + 1}: {node['name']}")

# Function to identify the input type (file vs text) for a given HTTP node
def get_input_type(http_node):
    if 'sendBinaryData' in http_node['parameters'] and http_node['parameters']['sendBinaryData'] == True:
        return "file"
    else:
        return "text"

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

# Simulate the pipeline by making HTTP requests based on the nodes
def simulate_pipeline(http_nodes):
    data = {}
    
    # Initialize input for the first node based on the input type (dummy data)
    input_data = None
    first_http_node = http_nodes[0]  # Just pick the first node for the first input
    input_type = get_input_type(first_http_node)

    if input_type == "file":
        file_path = '/Users/debelagemechu/projects/oAMF_dev/oamf/file.json'
        input_data = {'file': ('file.json', open(file_path, 'rb'))}
    else:
        input_data = {'text': 'This is some sample text input.'}

    # Process each HTTP node in the correct order
    for i, node in enumerate(http_nodes):
        url = node['parameters']['url']
        method = node['parameters']['requestMethod']
        
        # Make HTTP request based on the input data type (file or text)
        if input_type == "file":
            response = requests.request(method, url, files=input_data)
        else:
            response = requests.request(method, url, json=input_data)

        print(f"Response from {node['name']} (HTTP {method} {url}): {response.status_code}")
        print(f"Response Data: {response.text}")
        
        # For the next node, handle the response
        if response.status_code == 200:
            response_data = response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
            
            if 'sendBinaryData' in node['parameters'] and node['parameters']['sendBinaryData'] == True:
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

# Simulate the pipeline and capture the result
pipeline_result = simulate_pipeline(http_nodes)

# Function to handle non-serializable objects (e.g., file-like objects)
def handle_non_serializable_objects(obj):
    if isinstance(obj, dict):
        return {k: handle_non_serializable_objects(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [handle_non_serializable_objects(v) for v in obj]
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, io.IOBase):  # Check for file-like objects
        return "File object - cannot serialize"
    return obj

# Ensure non-serializable objects are handled properly
pipeline_result = handle_non_serializable_objects(pipeline_result)

# Print the final pipeline results
print("\nPipeline Result:")
print(pipeline_result)
