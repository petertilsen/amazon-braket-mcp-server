# Amazon Braket MCP Server

A comprehensive Model Context Protocol (MCP) server that provides quantum computing capabilities through Amazon Braket. This server enables you to create, execute, and analyze quantum circuits directly from your command line interface, making quantum computing accessible and integrated into your development workflow.

> **⚠️ Important Notice**: This is an **unofficial project** and is not officially supported by Amazon Web Services. However, it follows the implementation patterns and architectural structure of the official Amazon MCP servers available at [https://github.com/awslabs/mcp](https://github.com/awslabs/mcp), ensuring consistency with AWS MCP server standards and best practices.

## 🚀 Overview

This MCP server provides a complete quantum computing toolkit through Amazon Braket, enabling:

- **Circuit Creation**: Build quantum circuits using intuitive gate operations
- **Pre-built Algorithms**: Access common quantum circuits (Bell pairs, GHZ states, QFT)
- **Multi-Device Support**: Run on simulators and real quantum hardware
- **Result Analysis**: Visualize and analyze quantum measurement outcomes
- **Task Management**: Monitor, search, and manage quantum computing jobs
- **Educational Tools**: Perfect for learning quantum computing concepts

## 📦 Installation

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

## ⚙️ Configuration

### AWS Credentials
The server requires AWS credentials with permissions to access Amazon Braket services. Configure using:

1. **Environment variables**: 
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=us-east-1
   ```

2. **AWS credentials file**: 
   ```bash
   aws configure
   ```

3. **IAM roles**: Use IAM roles when running on AWS services

### Required AWS Permissions
Your AWS credentials need these permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "braket:SearchDevices",
                "braket:GetDevice",
                "braket:CreateQuantumTask",
                "braket:GetQuantumTask",
                "braket:CancelQuantumTask",
                "braket:SearchQuantumTasks",
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "*"
        }
    ]
}
```

### Supported AWS Regions
- `us-east-1` (US East - N. Virginia) - **Recommended**
- `us-west-1` (US West - N. California)
- `us-west-2` (US West - Oregon)
- `eu-west-2` (Europe - London)
- `ap-southeast-1` (Asia Pacific - Singapore)

## 🛠️ Available Tools

### Circuit Creation Tools

#### `create_quantum_circuit`
Create custom quantum circuits with specific gates and operations.

**Parameters:**
- `num_qubits` (int): Number of qubits in the circuit
- `gates` (list): List of gate operations to apply

**Example:**
```python
# Create a 3-qubit circuit with Hadamard and CNOT gates
circuit = create_quantum_circuit(
    num_qubits=3,
    gates=[
        {"name": "h", "qubits": [0]},           # Hadamard on qubit 0
        {"name": "cx", "qubits": [0, 1]},      # CNOT from qubit 0 to 1
        {"name": "ry", "qubits": [2], "params": [1.57]},  # Y-rotation on qubit 2
        {"name": "measure_all"}                 # Measure all qubits
    ]
)
```

**Supported Gates:**
- `h` - Hadamard gate (creates superposition)
- `x`, `y`, `z` - Pauli gates
- `cx`, `cy`, `cz` - Controlled gates
- `rx`, `ry`, `rz` - Rotation gates (require `params`)
- `s`, `t` - Phase gates
- `measure_all` - Measure all qubits

#### `create_bell_pair_circuit`
Create a Bell pair (maximally entangled two-qubit state).

**Example:**
```python
# Creates |00⟩ + |11⟩ state (50% chance each)
bell_circuit = create_bell_pair_circuit()
```

**Use Cases:**
- Quantum entanglement demonstrations
- Quantum teleportation protocols
- Bell inequality tests

#### `create_ghz_circuit`
Create a GHZ (Greenberger-Horne-Zeilinger) state for multi-qubit entanglement.

**Parameters:**
- `num_qubits` (int, default=3): Number of qubits to entangle

**Example:**
```python
# Create 4-qubit GHZ state: |0000⟩ + |1111⟩
ghz_circuit = create_ghz_circuit(num_qubits=4)
```

**Use Cases:**
- Multi-party quantum communication
- Quantum error correction studies
- Quantum sensing applications

#### `create_qft_circuit`
Create a Quantum Fourier Transform circuit.

**Parameters:**
- `num_qubits` (int, default=3): Number of qubits for QFT

**Example:**
```python
# Create 3-qubit QFT circuit
qft_circuit = create_qft_circuit(num_qubits=3)
```

**Use Cases:**
- Shor's factoring algorithm
- Quantum phase estimation
- Period finding problems

### Execution Tools

#### `run_quantum_task`
Execute quantum circuits on Braket devices.

**Parameters:**
- `circuit` (dict): Circuit definition from creation tools
- `device_arn` (str, optional): Specific device ARN
- `shots` (int, default=1000): Number of measurements
- `s3_bucket` (str, optional): S3 bucket for results
- `s3_prefix` (str, optional): S3 prefix for organization

**Example:**
```python
# Run on state vector simulator
task = run_quantum_task(
    circuit=bell_circuit,
    device_arn="arn:aws:braket:::device/quantum-simulator/amazon/sv1",
    shots=1000
)

# Run on real quantum hardware (when available)
task = run_quantum_task(
    circuit=my_circuit,
    device_arn="arn:aws:braket:us-east-1::device/qpu/rigetti/Aspen-M-3",
    shots=100,
    s3_bucket="my-quantum-results",
    s3_prefix="experiments/2024/"
)
```

#### `get_task_result`
Retrieve results from completed quantum tasks.

**Parameters:**
- `task_id` (str): ARN of the quantum task

**Example:**
```python
# Get results and analyze
results = get_task_result(task_id="arn:aws:braket:us-east-1:123456789:quantum-task/abc-123")

# Results include:
# - measurement counts: {"00": 487, "11": 513}
# - raw measurements: [[0,0], [1,1], [0,0], ...]
# - task metadata and timing
```

### Device Management Tools

#### `list_devices`
List all available quantum devices and simulators.

**Example:**
```python
devices = list_devices()

# Returns information about:
# - AWS simulators (SV1, TN1, DM1)
# - IonQ quantum computers
# - Rigetti quantum processors
# - Oxford Quantum Computing devices
# - Device status and availability
```

#### `get_device_info`
Get detailed information about a specific quantum device.

**Parameters:**
- `device_arn` (str): ARN of the device

**Example:**
```python
device_info = get_device_info(
    device_arn="arn:aws:braket:::device/quantum-simulator/amazon/sv1"
)

# Returns:
# - Device capabilities and limitations
# - Supported gate sets
# - Connectivity topology
# - Pricing information
# - Current availability status
```

### Task Management Tools

#### `search_quantum_tasks`
Search and filter quantum tasks by various criteria.

**Parameters:**
- `device_arn` (str, optional): Filter by device
- `state` (str, optional): Filter by task state (CREATED, RUNNING, COMPLETED, FAILED, CANCELLED)
- `max_results` (int, default=10): Maximum results to return
- `days_ago` (int, optional): Filter by creation time

**Example:**
```python
# Find recent completed tasks
recent_tasks = search_quantum_tasks(
    state="COMPLETED",
    days_ago=7,
    max_results=20
)

# Find all tasks on a specific device
device_tasks = search_quantum_tasks(
    device_arn="arn:aws:braket:::device/quantum-simulator/amazon/sv1",
    max_results=50
)
```

#### `cancel_quantum_task`
Cancel a running quantum task.

**Parameters:**
- `task_id` (str): ARN of the task to cancel

**Example:**
```python
# Cancel a long-running task
cancel_result = cancel_quantum_task(
    task_id="arn:aws:braket:us-east-1:123456789:quantum-task/long-running-task"
)
```

### Visualization Tools

#### `visualize_circuit`
Generate visual representations of quantum circuits.

**Parameters:**
- `circuit` (dict): Circuit definition to visualize

**Example:**
```python
# Visualize any circuit
visualization = visualize_circuit(circuit=qft_circuit)
# Returns base64-encoded PNG image of the circuit diagram
```

#### `visualize_results`
Create histograms and charts from quantum measurement results.

**Parameters:**
- `result` (dict): Results from get_task_result

**Example:**
```python
# Visualize measurement outcomes
chart = visualize_results(result=task_results)
# Returns histogram showing measurement probabilities
```

## 📚 Complete Examples

### Example 1: Quantum Entanglement Experiment
```python
# Create Bell pair circuit
bell_circuit = create_bell_pair_circuit()

# Visualize the circuit
circuit_diagram = visualize_circuit(circuit=bell_circuit)

# Run on simulator
task = run_quantum_task(
    circuit=bell_circuit,
    shots=1000
)

# Get and analyze results
results = get_task_result(task_id=task["task_id"])
print(f"Measurement counts: {results['counts']}")
# Expected: {"00": ~500, "11": ~500} - perfect correlation!

# Visualize results
results_chart = visualize_results(result=results)
```

### Example 2: Quantum Algorithm Development
```python
# Create custom quantum algorithm
algorithm_circuit = create_quantum_circuit(
    num_qubits=4,
    gates=[
        # Initialize superposition
        {"name": "h", "qubits": [0]},
        {"name": "h", "qubits": [1]},
        
        # Apply quantum operations
        {"name": "cx", "qubits": [0, 2]},
        {"name": "cx", "qubits": [1, 3]},
        
        # Add phase rotation
        {"name": "rz", "qubits": [2], "params": [0.785]},  # π/4 rotation
        
        # Measure all qubits
        {"name": "measure_all"}
    ]
)

# Test on different devices
devices = list_devices()
for device in devices[:2]:  # Test on first 2 available devices
    task = run_quantum_task(
        circuit=algorithm_circuit,
        device_arn=device["deviceArn"],
        shots=500
    )
    
    results = get_task_result(task_id=task["task_id"])
    print(f"Device {device['deviceName']}: {results['counts']}")
```

### Example 3: Quantum Fourier Transform Analysis
```python
# Create and run QFT
qft_circuit = create_qft_circuit(num_qubits=3)

# Run multiple times for statistical analysis
task_ids = []
for i in range(5):
    task = run_quantum_task(
        circuit=qft_circuit,
        shots=1000,
        s3_bucket="my-qft-experiments",
        s3_prefix=f"run_{i}/"
    )
    task_ids.append(task["task_id"])

# Analyze all results
all_results = []
for task_id in task_ids:
    result = get_task_result(task_id=task_id)
    all_results.append(result)
    
# Compare measurement distributions
for i, result in enumerate(all_results):
    print(f"Run {i+1}: {result['counts']}")
```

## 🎓 Learning Quantum Computing

This MCP server is perfect for learning quantum computing concepts:

### Basic Concepts
- **Superposition**: Use Hadamard gates to create equal probability states
- **Entanglement**: Create Bell pairs and GHZ states
- **Measurement**: Observe quantum state collapse
- **Interference**: Use QFT to see quantum interference patterns

### Advanced Topics
- **Quantum Algorithms**: Implement Grover's search, quantum walks
- **Error Analysis**: Compare ideal vs. real device results
- **Optimization**: Use variational quantum algorithms
- **Cryptography**: Implement quantum key distribution protocols

## 🔧 Troubleshooting

### Common Issues

1. **AWS Credentials Error**
   ```
   Solution: Ensure AWS credentials are properly configured
   Check: aws sts get-caller-identity
   ```

2. **Device Unavailable**
   ```
   Solution: Check device status with list_devices()
   Use simulators for development and testing
   ```

3. **Task Timeout**
   ```
   Solution: Reduce shot count or circuit complexity
   Use cancel_quantum_task() for stuck tasks
   ```

4. **Permission Denied**
   ```
   Solution: Verify IAM permissions for Braket services
   Check S3 permissions if using custom buckets
   ```

## 📈 Best Practices

1. **Start with Simulators**: Test circuits on simulators before using real hardware
2. **Optimize Shot Counts**: Use fewer shots for testing, more for production
3. **Monitor Costs**: Real quantum hardware can be expensive
4. **Save Results**: Use S3 buckets to store important experimental data
5. **Version Control**: Keep track of circuit versions and parameters

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details on:
- Reporting bugs
- Suggesting enhancements
- Submitting pull requests
- Code style guidelines

## 📄 License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## 🔗 Additional Resources

- [Amazon Braket Documentation](https://docs.aws.amazon.com/braket/)
- [Qiskit Textbook](https://qiskit.org/textbook/)
- [Quantum Computing Explained](https://aws.amazon.com/quantum-computing/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
