# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""Amazon Braket Service Interface Module.

This module provides a high-level interface for interacting with Amazon Braket service
through the Amazon Q framework. It supports creating quantum circuits, running quantum tasks,
and retrieving results.

The module implements classes for managing Braket connections and executing quantum tasks
using both Qiskit and Amazon Braket SDK.
"""

import io
import json
import base64
import boto3
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple

from braket.aws import AwsDevice, AwsQuantumTask
from braket.circuits import Circuit as BraketCircuit
from braket.tasks import QuantumTask
from braket.devices import LocalSimulator

from qiskit import QuantumCircuit as QiskitCircuit
from qiskit.visualization import circuit_drawer
from qiskit_braket_provider import BraketProvider

from loguru import logger

from awslabs.amazon_braket_mcp_server.models import (
    QuantumCircuit,
    Gate,
    TaskResult,
    TaskStatus,
    DeviceInfo,
    DeviceType,
)
from awslabs.amazon_braket_mcp_server.exceptions import (
    CircuitCreationError,
    TaskExecutionError,
    TaskResultError,
    DeviceError,
)
from awslabs.amazon_braket_mcp_server.visualization import VisualizationUtils


class BraketService:
    """A unified interface for interacting with Amazon Braket service.

    This class manages connections to Amazon Braket service, providing methods for
    creating quantum circuits, running quantum tasks, and retrieving results.

    Attributes:
        braket_client: Boto3 client for Amazon Braket service
        provider: Qiskit Braket provider for converting Qiskit circuits to Braket circuits
    """

    # Regions where Amazon Braket is available
    SUPPORTED_REGIONS = {
        'us-east-1',
        'us-west-1', 
        'us-west-2',
        'eu-west-2',
        'eu-north-1'
    }

    def __init__(self, region_name: Optional[str] = None, workspace_dir: Optional[str] = None):
        """Initialize a connection to Amazon Braket service.

        Args:
            region_name: AWS region name. If not provided, uses the default region from AWS configuration.
            workspace_dir: Directory to save visualization files. If None, uses temp directory.
            
        Raises:
            ValueError: If the specified region doesn't support Amazon Braket
        """
        # Get the actual region being used
        if region_name is None:
            # Try to get region from boto3 session
            session = boto3.Session()
            region_name = session.region_name
            
        self.region_name = region_name
        
        # Validate region support
        if region_name and region_name not in self.SUPPORTED_REGIONS:
            logger.warning(f'Region {region_name} may not support Amazon Braket. Supported regions: {sorted(self.SUPPORTED_REGIONS)}')
            
        try:
            self.braket_client = boto3.client('braket', region_name=region_name)
            self.provider = BraketProvider()
            
            # Initialize visualization utilities
            self.viz_utils = VisualizationUtils(workspace_dir)
            logger.debug(f'Initialized BraketService with region: {region_name}')
            
            # Test basic connectivity and permissions
            self._validate_service_access()
            
        except Exception as e:
            logger.error(f'Failed to initialize BraketService: {str(e)}')
            raise

    def _validate_service_access(self) -> None:
        """Validate that we can access Amazon Braket service.
        
        This method performs a basic connectivity test to ensure the service
        is accessible and the user has appropriate permissions.
        
        Raises:
            DeviceError: If service access validation fails
        """
        try:
            # Try to list devices as a basic connectivity test
            # This requires minimal permissions and validates both connectivity and auth
            response = self.braket_client.search_devices(maxResults=1)
            logger.debug("Successfully validated Amazon Braket service access")
        except Exception as e:
            error_msg = f"Failed to validate Amazon Braket service access: {str(e)}"
            logger.warning(error_msg)
            # Don't raise here - allow the service to initialize but log the warning
            # The actual operations will fail with more specific errors if needed

    def create_qiskit_circuit(self, circuit_def: QuantumCircuit) -> QiskitCircuit:
        """Create a Qiskit quantum circuit from the circuit definition.

        Args:
            circuit_def: Circuit definition containing number of qubits and gates

        Returns:
            QiskitCircuit: Created Qiskit quantum circuit

        Raises:
            CircuitCreationError: If there is an error creating the circuit
        """
        try:
            # Create a new Qiskit quantum circuit
            circuit = QiskitCircuit(circuit_def.num_qubits)
            
            # Add gates to the circuit
            for gate in circuit_def.gates:
                if gate.name == 'h':
                    circuit.h(gate.qubits)
                elif gate.name == 'x':
                    circuit.x(gate.qubits)
                elif gate.name == 'y':
                    circuit.y(gate.qubits)
                elif gate.name == 'z':
                    circuit.z(gate.qubits)
                elif gate.name == 's':
                    circuit.s(gate.qubits)
                elif gate.name == 't':
                    circuit.t(gate.qubits)
                elif gate.name == 'rx':
                    circuit.rx(gate.params[0], gate.qubits[0])
                elif gate.name == 'ry':
                    circuit.ry(gate.params[0], gate.qubits[0])
                elif gate.name == 'rz':
                    circuit.rz(gate.params[0], gate.qubits[0])
                elif gate.name == 'cx' or gate.name == 'cnot':
                    circuit.cx(gate.qubits[0], gate.qubits[1])
                elif gate.name == 'cy':
                    circuit.cy(gate.qubits[0], gate.qubits[1])
                elif gate.name == 'cz':
                    circuit.cz(gate.qubits[0], gate.qubits[1])
                elif gate.name == 'swap':
                    circuit.swap(gate.qubits[0], gate.qubits[1])
                elif gate.name == 'ccx' or gate.name == 'toffoli':
                    circuit.ccx(gate.qubits[0], gate.qubits[1], gate.qubits[2])
                elif gate.name == 'measure':
                    if len(gate.qubits) == 0:
                        circuit.measure_all()
                    else:
                        for qubit in gate.qubits:
                            circuit.measure(qubit, qubit)
                elif gate.name == 'measure_all':
                    circuit.measure_all()
                else:
                    raise CircuitCreationError(f"Unsupported gate: {gate.name}")
            
            return circuit
        except Exception as e:
            logger.exception(f"Error creating Qiskit circuit: {str(e)}")
            raise CircuitCreationError(f"Error creating Qiskit circuit: {str(e)}")

    def convert_to_braket_circuit(self, qiskit_circuit: QiskitCircuit) -> BraketCircuit:
        """Convert a Qiskit circuit to a Braket circuit.

        Args:
            qiskit_circuit: Qiskit quantum circuit

        Returns:
            BraketCircuit: Converted Braket circuit

        Raises:
            CircuitCreationError: If there is an error converting the circuit
        """
        try:
            # Use the Qiskit Braket provider to convert the circuit
            try:
                backend = self.provider.get_backend("braket_sv")
                braket_circuit = backend.convert_circuit(qiskit_circuit)
                return braket_circuit
            except Exception as provider_error:
                logger.warning(f"Provider conversion failed: {provider_error}. Attempting direct conversion.")
                
                # Fallback: Try direct conversion using Braket SDK
                # This is a simplified conversion for basic circuits
                braket_circuit = BraketCircuit()
                
                # Convert basic gates (this is a simplified implementation)
                for instruction in qiskit_circuit.data:
                    gate_name = instruction.operation.name.lower()
                    qubits = [qiskit_circuit.find_bit(qubit).index for qubit in instruction.qubits]
                    
                    if gate_name == 'h':
                        braket_circuit.h(qubits[0])
                    elif gate_name == 'x':
                        braket_circuit.x(qubits[0])
                    elif gate_name == 'y':
                        braket_circuit.y(qubits[0])
                    elif gate_name == 'z':
                        braket_circuit.z(qubits[0])
                    elif gate_name == 'cx' or gate_name == 'cnot':
                        braket_circuit.cnot(qubits[0], qubits[1])
                    elif gate_name == 'cz':
                        braket_circuit.cz(qubits[0], qubits[1])
                    elif gate_name == 'swap':
                        braket_circuit.swap(qubits[0], qubits[1])
                    else:
                        logger.warning(f"Unsupported gate in fallback conversion: {gate_name}")
                
                return braket_circuit
                
        except Exception as e:
            logger.exception(f"Error converting to Braket circuit: {str(e)}")
            raise CircuitCreationError(f"Error converting to Braket circuit: {str(e)}")

    def run_quantum_task(
        self, 
        circuit: Union[QiskitCircuit, BraketCircuit, QuantumCircuit],
        device_arn: str,
        shots: int = 1000,
        s3_bucket: Optional[str] = None,
        s3_prefix: Optional[str] = None,
    ) -> str:
        """Run a quantum task on an Amazon Braket device.

        Args:
            circuit: Quantum circuit to run (Qiskit, Braket, or circuit definition)
            device_arn: ARN of the device to run the task on
            shots: Number of shots to run
            s3_bucket: S3 bucket for storing results (optional)
            s3_prefix: S3 prefix for storing results (optional)

        Returns:
            str: Task ID of the created quantum task

        Raises:
            TaskExecutionError: If there is an error executing the task
        """
        try:
            # Convert circuit if needed
            braket_circuit = None
            if isinstance(circuit, QuantumCircuit):
                qiskit_circuit = self.create_qiskit_circuit(circuit)
                braket_circuit = self.convert_to_braket_circuit(qiskit_circuit)
            elif isinstance(circuit, QiskitCircuit):
                braket_circuit = self.convert_to_braket_circuit(circuit)
            elif isinstance(circuit, BraketCircuit):
                braket_circuit = circuit
            else:
                raise TaskExecutionError(f"Unsupported circuit type: {type(circuit)}")
            
            # Create the device
            device = AwsDevice(device_arn)
            
            # Run the task
            task = device.run(
                braket_circuit,
                shots=shots,
                s3_destination_folder=(s3_bucket, s3_prefix) if s3_bucket and s3_prefix else None,
            )
            
            return task.id
        except Exception as e:
            logger.exception(f"Error running quantum task: {str(e)}")
            raise TaskExecutionError(f"Error running quantum task: {str(e)}")

    def get_task_result(self, task_id: str) -> TaskResult:
        """Get the result of a quantum task.

        Args:
            task_id: ID of the quantum task

        Returns:
            TaskResult: Result of the quantum task

        Raises:
            TaskResultError: If there is an error retrieving the task result
        """
        try:
            # Retrieve the task
            task = AwsQuantumTask(task_id)
            
            # Get the task metadata
            metadata = task.metadata()
            
            # Determine the task status
            status_map = {
                'CREATED': TaskStatus.CREATED,
                'QUEUED': TaskStatus.QUEUED,
                'RUNNING': TaskStatus.RUNNING,
                'COMPLETED': TaskStatus.COMPLETED,
                'FAILED': TaskStatus.FAILED,
                'CANCELLED': TaskStatus.CANCELLED,
            }
            status = status_map.get(metadata.get('status'), TaskStatus.FAILED)
            
            # If the task is completed, get the results
            measurements = None
            counts = None
            execution_time = None
            
            if status == TaskStatus.COMPLETED:
                result = task.result()
                measurements = result.measurements.tolist() if hasattr(result, 'measurements') else None
                counts = result.measurement_counts if hasattr(result, 'measurement_counts') else None
                execution_time = metadata.get('endedAt', 0) - metadata.get('startedAt', 0) if metadata.get('startedAt') and metadata.get('endedAt') else None
            
            # Create the task result
            task_result = TaskResult(
                task_id=task_id,
                status=status,
                measurements=measurements,
                counts=counts,
                device=metadata.get('deviceArn', ''),
                shots=metadata.get('shots', 0),
                execution_time=execution_time,
                metadata=metadata,
            )
            
            return task_result
        except Exception as e:
            logger.exception(f"Error getting task result: {str(e)}")
            raise TaskResultError(f"Error getting task result: {str(e)}")

    def list_devices(self) -> List[DeviceInfo]:
        """List available quantum devices.

        Returns:
            List[DeviceInfo]: List of available quantum devices

        Raises:
            DeviceError: If there is an error retrieving the devices
        """
        try:
            # Get the list of devices
            response = self.braket_client.search_devices(filters=[])
            
            # Convert to DeviceInfo objects
            devices = []
            for device in response.get('devices', []):
                device_type = DeviceType.QPU if device.get('deviceType') == 'QPU' else DeviceType.SIMULATOR
                
                # Get the supported gates
                supported_gates = []
                paradigm = device.get('deviceCapabilities', {}).get('paradigm', {})
                if paradigm:
                    supported_gates = list(paradigm.get('supportedGates', []))
                
                # Create the device info
                device_info = DeviceInfo(
                    device_arn=device.get('deviceArn', ''),
                    device_name=device.get('deviceName', ''),
                    device_type=device_type,
                    provider_name=device.get('providerName', ''),
                    status=device.get('deviceStatus', ''),
                    qubits=device.get('deviceCapabilities', {}).get('paradigm', {}).get('qubitCount', 0),
                    connectivity=device.get('deviceCapabilities', {}).get('paradigm', {}).get('connectivity', ''),
                    paradigm=device.get('deviceCapabilities', {}).get('paradigm', {}).get('name', ''),
                    max_shots=device.get('deviceCapabilities', {}).get('service', {}).get('shotsRange', {}).get('max', 0),
                    supported_gates=supported_gates,
                )
                devices.append(device_info)
            
            return devices
        except Exception as e:
            logger.exception(f"Error listing devices: {str(e)}")
            raise DeviceError(f"Error listing devices: {str(e)}")

    def get_device_info(self, device_arn: str) -> DeviceInfo:
        """Get information about a specific quantum device.

        Args:
            device_arn: ARN of the device

        Returns:
            DeviceInfo: Information about the device

        Raises:
            DeviceError: If there is an error retrieving the device information
        """
        try:
            # Get the device information
            response = self.braket_client.get_device(deviceArn=device_arn)
            
            # Determine the device type
            device_type = DeviceType.QPU if response.get('deviceType') == 'QPU' else DeviceType.SIMULATOR
            
            # Get the supported gates
            supported_gates = []
            paradigm = response.get('deviceCapabilities', {}).get('paradigm', {})
            if paradigm:
                supported_gates = list(paradigm.get('supportedGates', []))
            
            # Create the device info
            device_info = DeviceInfo(
                device_arn=response.get('deviceArn', ''),
                device_name=response.get('deviceName', ''),
                device_type=device_type,
                provider_name=response.get('providerName', ''),
                status=response.get('deviceStatus', ''),
                qubits=response.get('deviceCapabilities', {}).get('paradigm', {}).get('qubitCount', 0),
                connectivity=response.get('deviceCapabilities', {}).get('paradigm', {}).get('connectivity', ''),
                paradigm=response.get('deviceCapabilities', {}).get('paradigm', {}).get('name', ''),
                max_shots=response.get('deviceCapabilities', {}).get('service', {}).get('shotsRange', {}).get('max', 0),
                supported_gates=supported_gates,
            )
            
            return device_info
        except Exception as e:
            logger.exception(f"Error getting device info: {str(e)}")
            raise DeviceError(f"Error getting device info: {str(e)}")

    def cancel_quantum_task(self, task_id: str) -> bool:
        """Cancel a quantum task.

        Args:
            task_id: ID of the quantum task to cancel

        Returns:
            bool: True if the task was cancelled successfully, False otherwise

        Raises:
            TaskExecutionError: If there is an error cancelling the task
        """
        try:
            # Cancel the task
            self.braket_client.cancel_quantum_task(quantumTaskArn=task_id)
            return True
        except Exception as e:
            logger.exception(f"Error cancelling quantum task: {str(e)}")
            raise TaskExecutionError(f"Error cancelling quantum task: {str(e)}")

    def search_quantum_tasks(
        self,
        device_arn: Optional[str] = None,
        state: Optional[str] = None,
        max_results: int = 10,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Search for quantum tasks.

        Args:
            device_arn: Filter by device ARN
            state: Filter by task state
            max_results: Maximum number of results to return
            created_after: Filter by creation time (after)
            created_before: Filter by creation time (before)

        Returns:
            List[Dict[str, Any]]: List of quantum tasks

        Raises:
            TaskExecutionError: If there is an error searching for tasks
        """
        try:
            # Build the filters
            filters = []
            if device_arn:
                filters.append({
                    'name': 'deviceArn',
                    'operator': 'EQUAL',
                    'values': [device_arn],
                })
            if state:
                filters.append({
                    'name': 'status',
                    'operator': 'EQUAL',
                    'values': [state],
                })
            if created_after:
                filters.append({
                    'name': 'createdAt',
                    'operator': 'GREATER_THAN',
                    'values': [created_after.isoformat()],
                })
            if created_before:
                filters.append({
                    'name': 'createdAt',
                    'operator': 'LESS_THAN',
                    'values': [created_before.isoformat()],
                })
            
            # Search for tasks
            response = self.braket_client.search_quantum_tasks(
                filters=filters,
                maxResults=max_results,
            )
            
            return response.get('quantumTasks', [])
        except Exception as e:
            logger.exception(f"Error searching quantum tasks: {str(e)}")
            raise TaskExecutionError(f"Error searching quantum tasks: {str(e)}")

    def visualize_circuit(self, circuit: Union[QiskitCircuit, QuantumCircuit]) -> str:
        """Visualize a quantum circuit.

        Args:
            circuit: Quantum circuit to visualize (Qiskit or circuit definition)

        Returns:
            str: Base64-encoded PNG image of the circuit

        Raises:
            CircuitCreationError: If there is an error visualizing the circuit
        """
        try:
            # Check if matplotlib is available
            try:
                import matplotlib.pyplot as plt
                import matplotlib
                matplotlib.use('Agg')
            except ImportError:
                raise CircuitCreationError("matplotlib is required for circuit visualization. Please install it with: pip install matplotlib")
            
            # Convert circuit if needed
            qiskit_circuit = None
            if isinstance(circuit, QuantumCircuit):
                qiskit_circuit = self.create_qiskit_circuit(circuit)
            elif isinstance(circuit, QiskitCircuit):
                qiskit_circuit = circuit
            else:
                raise CircuitCreationError(f"Unsupported circuit type for visualization: {type(circuit)}")
            
            # Draw the circuit
            img_data = io.BytesIO()
            circuit_drawer(qiskit_circuit, output='mpl', filename=img_data, interactive=False)
            img_data.seek(0)
            
            # Convert to base64
            base64_image = base64.b64encode(img_data.read()).decode('utf-8')
            
            return base64_image
        except Exception as e:
            logger.exception(f"Error visualizing circuit: {str(e)}")
            raise CircuitCreationError(f"Error visualizing circuit: {str(e)}")

    def create_bell_pair_circuit(self) -> QiskitCircuit:
        """Create a Bell pair circuit (entangled qubits).

        Returns:
            QiskitCircuit: Bell pair circuit
        """
        try:
            # Create a new Qiskit quantum circuit with 2 qubits
            circuit = QiskitCircuit(2, 2)
            
            # Apply Hadamard gate to the first qubit
            circuit.h(0)
            
            # Apply CNOT gate with control qubit 0 and target qubit 1
            circuit.cx(0, 1)
            
            # Measure both qubits
            circuit.measure([0, 1], [0, 1])
            
            return circuit
        except Exception as e:
            logger.exception(f"Error creating Bell pair circuit: {str(e)}")
            raise CircuitCreationError(f"Error creating Bell pair circuit: {str(e)}")

    def create_ghz_circuit(self, num_qubits: int = 3) -> QiskitCircuit:
        """Create a GHZ state circuit.

        Args:
            num_qubits: Number of qubits in the circuit (default: 3)

        Returns:
            QiskitCircuit: GHZ state circuit
        """
        try:
            # Create a new Qiskit quantum circuit
            circuit = QiskitCircuit(num_qubits, num_qubits)
            
            # Apply Hadamard gate to the first qubit
            circuit.h(0)
            
            # Apply CNOT gates to entangle all qubits
            for i in range(num_qubits - 1):
                circuit.cx(i, i + 1)
            
            # Measure all qubits
            circuit.measure(range(num_qubits), range(num_qubits))
            
            return circuit
        except Exception as e:
            logger.exception(f"Error creating GHZ circuit: {str(e)}")
            raise CircuitCreationError(f"Error creating GHZ circuit: {str(e)}")

    def create_qft_circuit(self, num_qubits: int = 3) -> QiskitCircuit:
        """Create a Quantum Fourier Transform circuit.

        Args:
            num_qubits: Number of qubits in the circuit (default: 3)

        Returns:
            QiskitCircuit: QFT circuit
        """
        try:
            # Create a new Qiskit quantum circuit
            circuit = QiskitCircuit(num_qubits, num_qubits)
            
            # Apply QFT
            for i in range(num_qubits):
                circuit.h(i)
                for j in range(i + 1, num_qubits):
                    circuit.cp(np.pi / float(2 ** (j - i)), i, j)
            
            # Swap qubits
            for i in range(num_qubits // 2):
                circuit.swap(i, num_qubits - i - 1)
            
            # Measure all qubits
            circuit.measure(range(num_qubits), range(num_qubits))
            
            return circuit
        except Exception as e:
            logger.exception(f"Error creating QFT circuit: {str(e)}")
            raise CircuitCreationError(f"Error creating QFT circuit: {str(e)}")

    def visualize_results(self, result: TaskResult) -> str:
        """Visualize the results of a quantum task.

        Args:
            result: Result of the quantum task

        Returns:
            str: Base64-encoded PNG image of the results visualization

        Raises:
            TaskResultError: If there is an error visualizing the results
        """
        try:
            # Check if matplotlib is available
            try:
                import matplotlib.pyplot as plt
                import matplotlib
                matplotlib.use('Agg')
            except ImportError:
                raise TaskResultError("matplotlib is required for results visualization. Please install it with: pip install matplotlib")
            
            # Check if we have counts
            if not result.counts:
                raise TaskResultError("No measurement counts available for visualization")
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Sort the counts by binary value
            sorted_counts = dict(sorted(result.counts.items()))
            
            # Plot the counts
            ax.bar(sorted_counts.keys(), sorted_counts.values())
            
            # Set the title and labels
            ax.set_title(f"Measurement Results (Task ID: {result.task_id})")
            ax.set_xlabel("Measurement Outcome")
            ax.set_ylabel("Count")
            
            # Rotate the x-axis labels for better readability
            plt.xticks(rotation=45)
            
            # Adjust the layout
            plt.tight_layout()
            
            # Save the plot to a BytesIO object
            img_data = io.BytesIO()
            plt.savefig(img_data, format='png')
            img_data.seek(0)
            
            # Convert to base64
            base64_image = base64.b64encode(img_data.read()).decode('utf-8')
            
            # Close the plot to free memory
            plt.close(fig)
            
            return base64_image
        except Exception as e:
            logger.exception(f"Error visualizing results: {str(e)}")
            raise TaskResultError(f"Error visualizing results: {str(e)}")
    
    def create_circuit_visualization(self,
                                     circuit: QuantumCircuit,
                                     circuit_type: str = "custom") -> Dict[str, Any]:
        """Create a visualization response for a quantum circuit.
        
        Args:
            circuit: The quantum circuit to visualize
            circuit_type: Type of circuit (e.g., "bell_pair", "ghz", "qft")
            
        Returns:
            Response dictionary with descriptions, ASCII art, and file paths
        """
        try:
            # Create the Qiskit circuit for visualization
            qiskit_circuit = self.create_qiskit_circuit(circuit)
            
            # Generate base64 visualization
            base64_viz = self.visualize_circuit(qiskit_circuit)
            
            # Create response
            return self.viz_utils.create_circuit_response(
                circuit, base64_viz, circuit_type
            )
            
        except Exception as e:
            logger.exception(f"Error creating circuit visualization: {str(e)}")
            raise CircuitCreationError(f"Error creating circuit visualization: {str(e)}")
    
    def create_results_visualization(self, result: TaskResult) -> Dict[str, Any]:
        """Create a visualization response for quantum results.
        
        Args:
            result: The quantum task result to visualize
            
        Returns:
            Response dictionary with descriptions, ASCII art, and file paths
        """
        try:
            # Generate base64 visualization
            base64_viz = self.visualize_results(result)
            
            # Create response
            return self.viz_utils.create_results_response(result, base64_viz)
            
        except Exception as e:
            logger.exception(f"Error creating results visualization: {str(e)}")
            raise TaskResultError(f"Error creating results visualization: {str(e)}")
    
    def describe_circuit(self, circuit: QuantumCircuit) -> Dict[str, Any]:
        """Generate a human-readable description of a quantum circuit.
        
        Args:
            circuit: The quantum circuit to describe
            
        Returns:
            Dictionary containing circuit description and analysis
        """
        return self.viz_utils.describe_circuit(circuit)
    
    def describe_results(self, result: TaskResult) -> Dict[str, Any]:
        """Generate a human-readable description of quantum results.
        
        Args:
            result: The quantum task result to describe
            
        Returns:
            Dictionary containing result description and analysis
        """
        return self.viz_utils.describe_results(result)
