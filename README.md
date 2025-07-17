# Amazon Braket MCP Server

An Amazon Braket MCP server that allows for creating, running, and analyzing quantum circuits using Qiskit with Amazon Braket.

## Overview

This MCP server provides tools for working with Amazon Braket quantum computing service. It enables:

- Creating quantum circuits using Qiskit
- Converting Qiskit circuits to Amazon Braket circuits
- Running quantum tasks on Amazon Braket simulators and quantum devices
- Retrieving and analyzing results from quantum tasks
- Managing Amazon Braket resources

## Installation

```bash
pip install awslabs.amazon-braket-mcp-server
```

### Dependencies

This server requires the following key dependencies:
- `amazon-braket-sdk` - Amazon Braket SDK for Python
- `qiskit` - Quantum computing framework
- `qiskit-braket-provider` - Qiskit provider for Amazon Braket
- `matplotlib` - For circuit and result visualization
- `numpy` - For numerical operations

## Configuration

### AWS Credentials
The server requires AWS credentials with permissions to access Amazon Braket services. You can configure these using:

1. **Environment variables**: Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and optionally `AWS_SESSION_TOKEN`
2. **AWS credentials file**: Configure credentials using `aws configure` CLI command
3. **IAM roles**: If running on AWS services like EC2, ECS, or Lambda, use IAM roles

### Required AWS Permissions
Your AWS credentials need the following permissions:
- `braket:SearchDevices` - List available quantum devices
- `braket:GetDevice` - Get device information
- `braket:CreateQuantumTask` - Submit quantum tasks
- `braket:GetQuantumTask` - Retrieve task status and results
- `braket:CancelQuantumTask` - Cancel running tasks
- `braket:SearchQuantumTasks` - Search for tasks
- `s3:GetObject`, `s3:PutObject` - For result storage (if using S3)

### Supported AWS Regions
Amazon Braket is available in the following regions:
- `us-east-1` (US East - N. Virginia)
- `us-west-1` (US West - N. California)
- `us-west-2` (US West - Oregon)
- `eu-west-2` (Europe - London)
- `ap-southeast-1` (Asia Pacific - Singapore)

Set your region using the `AWS_REGION` environment variable or AWS configuration.

## Usage

### Starting the Server

```bash
awslabs.amazon-braket-mcp-server
```

### Available Tools

The server provides the following tools:

- `create_quantum_circuit`: Create a quantum circuit using Qiskit
- `run_quantum_task`: Run a quantum circuit on a Braket device
- `get_task_result`: Get the result of a quantum task
- `list_devices`: List available quantum devices
- `get_device_info`: Get information about a specific quantum device
- `cancel_quantum_task`: Cancel a running quantum task
- `search_quantum_tasks`: Search for quantum tasks
- `create_bell_pair_circuit`: Create a Bell pair circuit (entangled qubits)
- `create_ghz_circuit`: Create a GHZ state circuit
- `create_qft_circuit`: Create a Quantum Fourier Transform circuit
- `visualize_circuit`: Visualize a quantum circuit
- `visualize_results`: Visualize results from a quantum task

## Examples

### Creating and Running a Simple Quantum Circuit

```python
# Create a simple quantum circuit
circuit = create_quantum_circuit(
    num_qubits=2,
    gates=[
        {"name": "h", "qubits": [0]},
        {"name": "cx", "qubits": [0, 1]},
        {"name": "measure_all": {}}
    ]
)

# Run the circuit on a simulator
task_id = run_quantum_task(
    circuit=circuit,
    device_arn="arn:aws:braket:::device/quantum-simulator/amazon/sv1",
    shots=1000
)

# Get the results
results = get_task_result(task_id=task_id)
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
