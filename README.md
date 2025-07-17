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

## 📚 MCP Usage Examples

These examples show how to interact with the Amazon Braket MCP server through natural language prompts and the expected tool calls and results.

### Example 1: Quantum Entanglement Experiment

**User Prompt:**
> "Create a Bell pair circuit and run it on a quantum simulator to demonstrate entanglement"

**MCP Tool Calls & Results:**

1. **Tool Call:** `create_bell_pair_circuit()`
   ```json
   {
     "circuit_def": {
       "num_qubits": 2,
       "gates": [
         {"name": "h", "qubits": [0]},
         {"name": "cx", "qubits": [0, 1]},
         {"name": "measure_all"}
       ]
     },
     "visualization": "iVBORw0KGgoAAAANSUhEUgAA...",
     "num_qubits": 2,
     "num_gates": 3
   }
   ```

2. **Tool Call:** `run_quantum_task(circuit=bell_circuit, shots=1000)`
   ```json
   {
     "task_id": "arn:aws:braket:us-east-1:123456789:quantum-task/abc-123",
     "status": "CREATED",
     "device_arn": "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
     "shots": 1000
   }
   ```

3. **Tool Call:** `get_task_result(task_id="arn:aws:braket:us-east-1:123456789:quantum-task/abc-123")`
   ```json
   {
     "task_id": "arn:aws:braket:us-east-1:123456789:quantum-task/abc-123",
     "status": "COMPLETED",
     "counts": {"00": 487, "11": 513},
     "measurements": [[0,0], [1,1], [0,0], [1,1], ...],
     "shots": 1000
   }
   ```

**Expected Response:**
> "Perfect! The Bell pair circuit demonstrates quantum entanglement beautifully. Out of 1000 measurements, we got 487 |00⟩ states and 513 |11⟩ states - notice we never see |01⟩ or |10⟩! This shows the qubits are perfectly correlated, which is the hallmark of quantum entanglement."

### Example 2: Device Comparison Study

**User Prompt:**
> "What quantum devices are available and show me their capabilities?"

**MCP Tool Calls & Results:**

1. **Tool Call:** `list_devices()`
   ```json
   [
     {
       "deviceArn": "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
       "deviceName": "SV1",
       "deviceType": "SIMULATOR",
       "deviceStatus": "ONLINE",
       "providerName": "Amazon Braket"
     },
     {
       "deviceArn": "arn:aws:braket:us-east-1::device/qpu/ionq/Harmony",
       "deviceName": "Harmony",
       "deviceType": "QPU",
       "deviceStatus": "ONLINE",
       "providerName": "IonQ"
     }
   ]
   ```

2. **Tool Call:** `get_device_info(device_arn="arn:aws:braket:::device/quantum-simulator/amazon/sv1")`
   ```json
   {
     "deviceArn": "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
     "deviceName": "SV1",
     "deviceType": "SIMULATOR",
     "deviceCapabilities": {
       "paradigm": {
         "qubitCount": 34,
         "nativeGateSet": ["ccnot", "cnot", "cphaseshift", "cswap", ...]
       }
     },
     "deviceStatus": "ONLINE"
   }
   ```

**Expected Response:**
> "You have access to several quantum devices:
> 
> **SV1 Simulator**: Perfect for development with up to 34 qubits, supports all gate operations, always available and free for testing.
> 
> **IonQ Harmony**: Real quantum hardware with trapped ion technology, currently online and available for production workloads."

### Example 3: Custom Algorithm Development

**User Prompt:**
> "Create a 3-qubit quantum circuit that puts the first qubit in superposition, entangles it with the second qubit, and applies a rotation to the third qubit"

**MCP Tool Calls & Results:**

1. **Tool Call:** `create_quantum_circuit(num_qubits=3, gates=[...])`
   ```json
   {
     "circuit_def": {
       "num_qubits": 3,
       "gates": [
         {"name": "h", "qubits": [0]},
         {"name": "cx", "qubits": [0, 1]},
         {"name": "ry", "qubits": [2], "params": [1.57]},
         {"name": "measure_all"}
       ]
     },
     "visualization": "iVBORw0KGgoAAAANSUhEUgAA...",
     "num_qubits": 3,
     "num_gates": 4
   }
   ```

2. **Tool Call:** `visualize_circuit(circuit=custom_circuit)`
   ```json
   {
     "visualization": "iVBORw0KGgoAAAANSUhEUgAA..."
   }
   ```

**Expected Response:**
> "I've created your custom 3-qubit circuit! Here's what it does:
> - Qubit 0: Hadamard gate creates superposition (|0⟩ + |1⟩)/√2
> - Qubit 1: CNOT gate entangles it with qubit 0
> - Qubit 2: RY rotation gate (π/2 rotation around Y-axis)
> 
> The circuit diagram shows the quantum operations in sequence. Would you like to run this on a simulator?"

### Example 4: Task Management and Analysis

**User Prompt:**
> "Show me my recent quantum computing jobs and their results"

**MCP Tool Calls & Results:**

1. **Tool Call:** `search_quantum_tasks(state="COMPLETED", days_ago=7, max_results=5)`
   ```json
   [
     {
       "quantumTaskArn": "arn:aws:braket:us-east-1:123456789:quantum-task/task-1",
       "status": "COMPLETED",
       "deviceArn": "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
       "createdAt": "2024-01-15T10:30:00Z",
       "shots": 1000
     },
     {
       "quantumTaskArn": "arn:aws:braket:us-east-1:123456789:quantum-task/task-2",
       "status": "COMPLETED", 
       "deviceArn": "arn:aws:braket:us-east-1::device/qpu/ionq/Harmony",
       "createdAt": "2024-01-14T15:45:00Z",
       "shots": 100
     }
   ]
   ```

2. **Tool Call:** `get_task_result(task_id="arn:aws:braket:us-east-1:123456789:quantum-task/task-1")`
   ```json
   {
     "status": "COMPLETED",
     "counts": {"000": 234, "001": 251, "010": 243, "011": 272},
     "execution_time": "2.3s",
     "shots": 1000
   }
   ```

3. **Tool Call:** `visualize_results(result=task_results)`
   ```json
   {
     "visualization": "iVBORw0KGgoAAAANSUhEUgAA..."
   }
   ```

**Expected Response:**
> "Here are your recent quantum computing jobs:
> 
> **Task 1** (SV1 Simulator - Jan 15):
> - 1000 shots completed in 2.3 seconds
> - Results show fairly uniform distribution across all 3-qubit states
> - Histogram visualization shows the measurement probabilities
> 
> **Task 2** (IonQ Harmony - Jan 14):
> - Real quantum hardware execution with 100 shots
> - Results will show quantum noise and decoherence effects typical of NISQ devices"

### Example 5: Quantum Algorithm Learning

**User Prompt:**
> "I want to learn about quantum algorithms. Create a Quantum Fourier Transform and explain what it does"

**MCP Tool Calls & Results:**

1. **Tool Call:** `create_qft_circuit(num_qubits=3)`
   ```json
   {
     "circuit_def": {
       "num_qubits": 3,
       "gates": [
         {"name": "h", "qubits": [0]},
         {"name": "cp", "qubits": [1, 0], "params": [1.5708]},
         {"name": "cp", "qubits": [2, 0], "params": [0.7854]},
         {"name": "h", "qubits": [1]},
         {"name": "cp", "qubits": [2, 1], "params": [1.5708]},
         {"name": "h", "qubits": [2]},
         {"name": "swap", "qubits": [0, 2]},
         {"name": "measure_all"}
       ]
     },
     "visualization": "iVBORw0KGgoAAAANSUhEUgAA...",
     "num_qubits": 3,
     "num_gates": 8
   }
   ```

2. **Tool Call:** `run_quantum_task(circuit=qft_circuit, shots=1000)`
   ```json
   {
     "task_id": "arn:aws:braket:us-east-1:123456789:quantum-task/qft-demo",
     "status": "CREATED"
   }
   ```

**Expected Response:**
> "Great choice for learning! The Quantum Fourier Transform (QFT) is fundamental to many quantum algorithms. Here's what this 3-qubit QFT does:
> 
> **Circuit Structure:**
> - Hadamard gates create superposition
> - Controlled phase gates add quantum interference
> - SWAP gates reorder the qubits
> 
> **Applications:**
> - **Shor's Algorithm**: For factoring large numbers
> - **Phase Estimation**: Finding eigenvalues of quantum operators
> - **Period Finding**: Detecting periodic patterns in data
> 
> The QFT transforms computational basis states into frequency domain representations, similar to classical Fourier transforms but leveraging quantum parallelism. When we run this, you'll see how quantum interference creates specific measurement patterns!"

### Example 6: Error Handling and Troubleshooting

**User Prompt:**
> "My quantum task seems to be stuck. Can you help me check its status and cancel it if needed?"

**MCP Tool Calls & Results:**

1. **Tool Call:** `search_quantum_tasks(state="RUNNING", max_results=10)`
   ```json
   [
     {
       "quantumTaskArn": "arn:aws:braket:us-east-1:123456789:quantum-task/stuck-task",
       "status": "RUNNING",
       "createdAt": "2024-01-15T08:00:00Z",
       "deviceArn": "arn:aws:braket:us-east-1::device/qpu/ionq/Harmony"
     }
   ]
   ```

2. **Tool Call:** `cancel_quantum_task(task_id="arn:aws:braket:us-east-1:123456789:quantum-task/stuck-task")`
   ```json
   {
     "status": "CANCELLED",
     "message": "Quantum task successfully cancelled"
   }
   ```

**Expected Response:**
> "I found your stuck task! It's been running since 8:00 AM on the IonQ Harmony device. I've successfully cancelled it for you. 
> 
> **Troubleshooting Tips:**
> - Real quantum hardware can have queues and longer execution times
> - Consider using simulators for development and testing
> - Monitor task status regularly for long-running jobs
> - Set appropriate timeouts for production workflows"

## 🎯 MCP Integration Benefits

These examples demonstrate how the MCP server enables:

- **Natural Language Interface**: Ask questions in plain English
- **Contextual Responses**: Get explanations tailored to your quantum computing level
- **Automatic Tool Orchestration**: Multiple tools work together seamlessly
- **Educational Guidance**: Learn quantum concepts through hands-on examples
- **Error Recovery**: Built-in troubleshooting and task management
- **Visual Feedback**: Circuit diagrams and result visualizations included

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
