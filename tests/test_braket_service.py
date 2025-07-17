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

"""Comprehensive tests for the BraketService class."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from awslabs.amazon_braket_mcp_server.braket_service import BraketService
from awslabs.amazon_braket_mcp_server.models import (
    QuantumCircuit, Gate, TaskResult, TaskStatus, DeviceInfo, DeviceType
)
from awslabs.amazon_braket_mcp_server.exceptions import (
    BraketMCPException, TaskExecutionError, TaskResultError, DeviceError
)


@pytest.fixture
def mock_boto3_client():
    """Create a mock boto3 client for testing."""
    with patch('boto3.client') as mock_client:
        mock_braket = MagicMock()
        mock_client.return_value = mock_braket
        yield mock_braket


@pytest.fixture
def braket_service(mock_boto3_client):
    """Create a BraketService instance for testing."""
    return BraketService(region_name='us-west-2')


@patch('awslabs.amazon_braket_mcp_server.braket_service.QiskitCircuit')
def test_create_qiskit_circuit(mock_qiskit_circuit_class, braket_service):
    """Test creating a Qiskit circuit."""
    # Mock the QiskitCircuit class and instance
    mock_circuit_instance = MagicMock()
    mock_qiskit_circuit_class.return_value = mock_circuit_instance
    
    # Create a circuit definition
    circuit_def = QuantumCircuit(
        num_qubits=2,
        gates=[
            Gate(name='h', qubits=[0]),
            Gate(name='cx', qubits=[0, 1]),
            Gate(name='measure_all'),
        ],
    )
    
    # Call the method
    result = braket_service.create_qiskit_circuit(circuit_def)
    
    # Check that the circuit was created with correct parameters
    mock_qiskit_circuit_class.assert_called_once_with(2)
    
    # Check that the appropriate methods were called on the circuit instance
    assert mock_circuit_instance.h.called
    assert mock_circuit_instance.cx.called
    assert mock_circuit_instance.measure_all.called
    assert result == mock_circuit_instance


@patch('awslabs.amazon_braket_mcp_server.braket_service.AwsDevice')
@patch('awslabs.amazon_braket_mcp_server.braket_service.QiskitCircuit')
def test_run_quantum_task(mock_qiskit_circuit_class, mock_aws_device, braket_service):
    """Test running a quantum task."""
    # Mock the QiskitCircuit instance
    mock_qiskit_circuit = MagicMock()
    mock_qiskit_circuit_class.return_value = mock_qiskit_circuit
    
    # Mock the convert_to_braket_circuit method
    braket_service.convert_to_braket_circuit = MagicMock()
    
    # Mock the AwsDevice.run method
    mock_task = MagicMock()
    mock_task.id = 'task-123'
    mock_device_instance = MagicMock()
    mock_device_instance.run.return_value = mock_task
    mock_aws_device.return_value = mock_device_instance
    
    # Create a circuit definition
    circuit_def = QuantumCircuit(
        num_qubits=2,
        gates=[
            Gate(name='h', qubits=[0]),
            Gate(name='cx', qubits=[0, 1]),
        ],
    )
    
    # Call the method
    result = braket_service.run_quantum_task(
        circuit=circuit_def,
        device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
        shots=1000,
    )
    
    # Check the result
    assert result == 'task-123'
    assert mock_qiskit_circuit_class.called
    assert braket_service.convert_to_braket_circuit.called
    assert mock_device_instance.run.called


@patch('awslabs.amazon_braket_mcp_server.braket_service.AwsQuantumTask')
def test_get_task_result(mock_aws_quantum_task, braket_service):
    """Test getting a task result."""
    # Mock the AwsQuantumTask
    mock_task_instance = MagicMock()
    mock_task_instance.metadata.return_value = {
        'status': 'COMPLETED',
        'deviceArn': 'arn:aws:braket:::device/quantum-simulator/amazon/sv1',
        'shots': 1000,
        'startedAt': 1000,
        'endedAt': 1100,
    }
    mock_result = MagicMock()
    # Fix: Create a numpy-like array mock that has tolist() method
    import numpy as np
    mock_measurements = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    mock_result.measurements = mock_measurements
    mock_result.measurement_counts = {'00': 250, '01': 250, '10': 250, '11': 250}
    mock_task_instance.result.return_value = mock_result
    mock_aws_quantum_task.return_value = mock_task_instance
    
    # Call the method
    result = braket_service.get_task_result('task-123')
    
    # Check the result
    assert result.task_id == 'task-123'
    assert result.status == TaskStatus.COMPLETED
    assert result.device == 'arn:aws:braket:::device/quantum-simulator/amazon/sv1'
    assert result.shots == 1000
    assert result.execution_time == 100
    assert mock_task_instance.metadata.called
    assert mock_task_instance.result.called

@patch('awslabs.amazon_braket_mcp_server.braket_service.QiskitCircuit')
def test_create_qiskit_circuit(mock_qiskit_circuit_class, braket_service):
    """Test creating a Qiskit circuit."""
    # Mock the QiskitCircuit class and instance
    mock_circuit_instance = MagicMock()
    mock_qiskit_circuit_class.return_value = mock_circuit_instance
    
    # Create a circuit definition
    circuit_def = QuantumCircuit(
        num_qubits=2,
        gates=[
            Gate(name='h', qubits=[0]),
            Gate(name='cx', qubits=[0, 1]),
            Gate(name='measure_all'),
        ],
    )
    
    # Call the method
    result = braket_service.create_qiskit_circuit(circuit_def)
    
    # Check that the circuit was created with correct parameters
    mock_qiskit_circuit_class.assert_called_once_with(2)
    
    # Check that the appropriate methods were called on the circuit instance
    assert mock_circuit_instance.h.called
    assert mock_circuit_instance.cx.called
    assert mock_circuit_instance.measure_all.called
    assert result == mock_circuit_instance


@patch('awslabs.amazon_braket_mcp_server.braket_service.AwsDevice')
@patch('awslabs.amazon_braket_mcp_server.braket_service.QiskitCircuit')
def test_run_quantum_task(mock_qiskit_circuit_class, mock_aws_device, braket_service):
    """Test running a quantum task."""
    # Mock the QiskitCircuit instance
    mock_qiskit_circuit = MagicMock()
    mock_qiskit_circuit_class.return_value = mock_qiskit_circuit
    
    # Mock the convert_to_braket_circuit method
    braket_service.convert_to_braket_circuit = MagicMock()
    
    # Mock the AwsDevice.run method
    mock_task = MagicMock()
    mock_task.id = 'task-123'
    mock_device_instance = MagicMock()
    mock_device_instance.run.return_value = mock_task
    mock_aws_device.return_value = mock_device_instance
    
    # Create a circuit definition
    circuit_def = QuantumCircuit(
        num_qubits=2,
        gates=[
            Gate(name='h', qubits=[0]),
            Gate(name='cx', qubits=[0, 1]),
        ],
    )
    
    # Call the method
    result = braket_service.run_quantum_task(
        circuit=circuit_def,
        device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
        shots=1000,
    )
    
    # Check the result
    assert result == 'task-123'
    assert mock_qiskit_circuit_class.called
    assert braket_service.convert_to_braket_circuit.called
    assert mock_device_instance.run.called


@patch('awslabs.amazon_braket_mcp_server.braket_service.AwsQuantumTask')
def test_get_task_result(mock_aws_quantum_task, braket_service):
    """Test getting a task result."""
    # Mock the AwsQuantumTask
    mock_task_instance = MagicMock()
    mock_task_instance.metadata.return_value = {
        'status': 'COMPLETED',
        'deviceArn': 'arn:aws:braket:::device/quantum-simulator/amazon/sv1',
        'shots': 1000,
        'startedAt': 1000,
        'endedAt': 1100,
    }
    mock_result = MagicMock()
    # Fix: Create a numpy-like array mock that has tolist() method
    mock_measurements = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    mock_result.measurements = mock_measurements
    mock_result.measurement_counts = {'00': 250, '01': 250, '10': 250, '11': 250}
    mock_task_instance.result.return_value = mock_result
    mock_aws_quantum_task.return_value = mock_task_instance
    
    # Call the method
    result = braket_service.get_task_result('task-123')
    
    # Check the result
    assert result.task_id == 'task-123'
    assert result.status == TaskStatus.COMPLETED
    assert result.device == 'arn:aws:braket:::device/quantum-simulator/amazon/sv1'
    assert result.shots == 1000
    assert result.execution_time == 100
    assert mock_task_instance.metadata.called
    assert mock_task_instance.result.called

class TestBraketServiceValidation:
    """Test service validation functionality."""
    
    def test_validate_service_access_success(self, mock_boto3_client):
        """Test successful service validation."""
        mock_boto3_client.search_devices.return_value = {'devices': []}
        
        # Create a fresh service instance to avoid call count issues
        braket_service = BraketService(region_name='us-west-2')
        
        # Should not raise an exception (method is private and doesn't raise on failure)
        braket_service._validate_service_access()
        
        # The method is called during init and then again in our test
        assert mock_boto3_client.search_devices.call_count >= 1
    
    def test_validate_service_access_failure(self, mock_boto3_client):
        """Test service validation failure."""
        mock_boto3_client.search_devices.side_effect = Exception("Access denied")
        
        # Create a fresh service instance
        braket_service = BraketService(region_name='us-west-2')
        
        # The method logs a warning but doesn't raise an exception
        braket_service._validate_service_access()
        
        # Should not raise an exception - it just logs a warning
        assert mock_boto3_client.search_devices.call_count >= 1


class TestCircuitConversion:
    """Test circuit conversion functionality."""
    
    @patch('awslabs.amazon_braket_mcp_server.braket_service.BraketCircuit')
    def test_convert_to_braket_circuit(self, mock_braket_circuit, braket_service):
        """Test converting Qiskit circuit to Braket circuit."""
        # Mock Qiskit circuit
        mock_qiskit_circuit = MagicMock()
        mock_qiskit_circuit.num_qubits = 2
        mock_qiskit_circuit.data = []
        
        # Mock Braket circuit
        mock_braket_instance = MagicMock()
        mock_braket_circuit.return_value = mock_braket_instance
        
        result = braket_service.convert_to_braket_circuit(mock_qiskit_circuit)
        
        assert result == mock_braket_instance
        mock_braket_circuit.assert_called_once()
    
    def test_create_qiskit_circuit_with_different_gates(self, braket_service):
        """Test creating Qiskit circuits with various gate types."""
        with patch('awslabs.amazon_braket_mcp_server.braket_service.QiskitCircuit') as mock_circuit_class:
            mock_circuit = MagicMock()
            mock_circuit_class.return_value = mock_circuit
            
            # Test with different gate types
            circuit_def = QuantumCircuit(
                num_qubits=3,
                gates=[
                    Gate(name='x', qubits=[0]),
                    Gate(name='y', qubits=[1]),
                    Gate(name='z', qubits=[2]),
                    Gate(name='rx', qubits=[0], params=[0.5]),
                    Gate(name='ry', qubits=[1], params=[1.0]),
                    Gate(name='rz', qubits=[2], params=[1.5]),
                    Gate(name='ccx', qubits=[0, 1, 2]),
                ],
            )
            
            result = braket_service.create_qiskit_circuit(circuit_def)
            
            # Verify circuit creation
            mock_circuit_class.assert_called_once_with(3)
            
            # Verify gate applications
            assert mock_circuit.x.called
            assert mock_circuit.y.called
            assert mock_circuit.z.called
            assert mock_circuit.rx.called
            assert mock_circuit.ry.called
            assert mock_circuit.rz.called
            assert mock_circuit.ccx.called
            
            assert result == mock_circuit


class TestDeviceManagement:
    """Test device management functionality."""
    
    def test_list_devices_success(self, braket_service, mock_boto3_client):
        """Test successful device listing."""
        mock_boto3_client.search_devices.return_value = {
            'devices': [
                {
                    'deviceArn': 'arn:aws:braket:::device/quantum-simulator/amazon/sv1',
                    'deviceName': 'SV1',
                    'deviceType': 'SIMULATOR',
                    'providerName': 'Amazon',
                    'deviceStatus': 'ONLINE',
                    'deviceCapabilities': {
                        'paradigm': {
                            'name': 'gate-based',
                            'qubitCount': 34,
                            'connectivity': 'full',
                            'supportedGates': ['h', 'x', 'y', 'z', 'cx']
                        },
                        'service': {
                            'shotsRange': {'max': 100000}
                        }
                    }
                }
            ]
        }
        
        devices = braket_service.list_devices()
        
        assert len(devices) == 1
        device = devices[0]
        assert device.device_arn == 'arn:aws:braket:::device/quantum-simulator/amazon/sv1'
        assert device.device_name == 'SV1'
        assert device.device_type == DeviceType.SIMULATOR
        assert device.provider_name == 'Amazon'
        assert device.status == 'ONLINE'
        assert device.qubits == 34
        assert device.max_shots == 100000
        assert 'h' in device.supported_gates
    
    def test_list_devices_failure(self, braket_service, mock_boto3_client):
        """Test device listing failure."""
        mock_boto3_client.search_devices.side_effect = Exception("API Error")
        
        with pytest.raises(DeviceError, match="Error listing devices"):
            braket_service.list_devices()
    
    def test_get_device_info_success(self, braket_service, mock_boto3_client):
        """Test successful device info retrieval."""
        device_arn = 'arn:aws:braket:::device/quantum-simulator/amazon/sv1'
        mock_boto3_client.get_device.return_value = {
            'deviceArn': device_arn,
            'deviceName': 'SV1',
            'deviceType': 'SIMULATOR',
            'providerName': 'Amazon',
            'deviceStatus': 'ONLINE',
            'deviceCapabilities': {
                'paradigm': {
                    'name': 'gate-based',
                    'qubitCount': 34,
                    'connectivity': 'full',
                    'supportedGates': ['h', 'x', 'y', 'z', 'cx']
                },
                'service': {
                    'shotsRange': {'max': 100000}
                }
            }
        }
        
        device_info = braket_service.get_device_info(device_arn)
        
        assert device_info.device_arn == device_arn
        assert device_info.device_name == 'SV1'
        assert device_info.device_type == DeviceType.SIMULATOR
        mock_boto3_client.get_device.assert_called_once_with(deviceArn=device_arn)
    
    def test_get_device_info_failure(self, braket_service, mock_boto3_client):
        """Test device info retrieval failure."""
        device_arn = 'arn:aws:braket:::device/quantum-simulator/amazon/sv1'
        mock_boto3_client.get_device.side_effect = Exception("Device not found")
        
        with pytest.raises(DeviceError, match="Error getting device info"):
            braket_service.get_device_info(device_arn)


class TestTaskManagement:
    """Test quantum task management functionality."""
    
    def test_cancel_quantum_task_success(self, braket_service, mock_boto3_client):
        """Test successful task cancellation."""
        # Mock the braket client's cancel method
        mock_boto3_client.cancel_quantum_task.return_value = None
        
        result = braket_service.cancel_quantum_task('task-123')
        
        assert result is True
        mock_boto3_client.cancel_quantum_task.assert_called_once_with(quantumTaskArn='task-123')
    
    def test_cancel_quantum_task_failure(self, braket_service, mock_boto3_client):
        """Test task cancellation failure."""
        # Mock the braket client to raise an exception
        mock_boto3_client.cancel_quantum_task.side_effect = Exception("Cannot cancel")
        
        with pytest.raises(TaskExecutionError, match="Error cancelling quantum task"):
            braket_service.cancel_quantum_task('task-123')
    
    def test_search_quantum_tasks_success(self, braket_service, mock_boto3_client):
        """Test successful task search."""
        mock_boto3_client.search_quantum_tasks.return_value = {
            'quantumTasks': [
                {
                    'quantumTaskArn': 'task-123',
                    'status': 'COMPLETED',
                    'deviceArn': 'arn:aws:braket:::device/quantum-simulator/amazon/sv1',
                    'shots': 1000,
                    'createdAt': '2023-01-01T00:00:00Z'
                }
            ]
        }
        
        tasks = braket_service.search_quantum_tasks(
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            state='COMPLETED',
            max_results=10
        )
        
        assert len(tasks) == 1
        task = tasks[0]
        assert task['quantumTaskArn'] == 'task-123'
        assert task['status'] == 'COMPLETED'
    
    def test_search_quantum_tasks_with_filters(self, braket_service, mock_boto3_client):
        """Test task search with filters."""
        mock_boto3_client.search_quantum_tasks.return_value = {'quantumTasks': []}
        
        braket_service.search_quantum_tasks(
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            state='RUNNING'
        )
        
        # Verify filters were applied
        call_args = mock_boto3_client.search_quantum_tasks.call_args
        filters = call_args[1]['filters']
        
        device_filter = next(f for f in filters if f['name'] == 'deviceArn')
        assert device_filter['values'] == ['arn:aws:braket:::device/quantum-simulator/amazon/sv1']
        
        state_filter = next(f for f in filters if f['name'] == 'status')
        assert state_filter['values'] == ['RUNNING']


class TestTaskResults:
    """Test task result handling."""
    
    @patch('awslabs.amazon_braket_mcp_server.braket_service.AwsQuantumTask')
    def test_get_task_result_incomplete(self, mock_aws_quantum_task, braket_service):
        """Test getting result for incomplete task."""
        mock_task = MagicMock()
        mock_task.metadata.return_value = {
            'status': 'RUNNING',
            'deviceArn': 'arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            'shots': 1000
        }
        mock_aws_quantum_task.return_value = mock_task
        
        result = braket_service.get_task_result('task-123')
        
        assert result.task_id == 'task-123'
        assert result.status == TaskStatus.RUNNING
        assert result.measurements is None
        assert result.counts is None
    
    @patch('awslabs.amazon_braket_mcp_server.braket_service.AwsQuantumTask')
    def test_get_task_result_failed(self, mock_aws_quantum_task, braket_service):
        """Test getting result for failed task."""
        mock_task = MagicMock()
        mock_task.metadata.return_value = {
            'status': 'FAILED',
            'deviceArn': 'arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            'shots': 1000
        }
        mock_aws_quantum_task.return_value = mock_task
        
        result = braket_service.get_task_result('task-123')
        
        assert result.task_id == 'task-123'
        assert result.status == TaskStatus.FAILED
    
    @patch('awslabs.amazon_braket_mcp_server.braket_service.AwsQuantumTask')
    def test_get_task_result_exception(self, mock_aws_quantum_task, braket_service):
        """Test task result retrieval with exception."""
        mock_aws_quantum_task.side_effect = Exception("Task not found")
        
        with pytest.raises(TaskResultError, match="Error getting task result"):
            braket_service.get_task_result('task-123')


class TestVisualization:
    """Test circuit visualization functionality."""
    
    def test_visualize_circuit_success(self, braket_service):
        """Test successful circuit visualization."""
        with patch('awslabs.amazon_braket_mcp_server.braket_service.circuit_drawer') as mock_circuit_drawer, \
             patch('awslabs.amazon_braket_mcp_server.braket_service.base64') as mock_base64, \
             patch('io.BytesIO') as mock_bytesio:
            
            # Create a proper Qiskit circuit mock
            from qiskit import QuantumCircuit as QiskitCircuit
            mock_qiskit_circuit = MagicMock(spec=QiskitCircuit)
            
            # Mock the image saving process
            mock_buffer = MagicMock()
            mock_buffer.read.return_value = b'fake_image_data'
            mock_bytesio.return_value = mock_buffer
            
            # Mock base64 encoding properly
            mock_encoded = MagicMock()
            mock_encoded.decode.return_value = 'encoded_image_string'
            mock_base64.b64encode.return_value = mock_encoded
            
            result = braket_service.visualize_circuit(mock_qiskit_circuit)
            
            assert result == 'encoded_image_string'
            mock_circuit_drawer.assert_called_once()
    
    def test_visualize_circuit_failure(self, braket_service):
        """Test circuit visualization failure."""
        with patch('awslabs.amazon_braket_mcp_server.braket_service.circuit_drawer') as mock_circuit_drawer:
            from qiskit import QuantumCircuit as QiskitCircuit
            mock_qiskit_circuit = MagicMock(spec=QiskitCircuit)
            mock_circuit_drawer.side_effect = Exception("Visualization error")
            
            with pytest.raises(Exception):
                braket_service.visualize_circuit(mock_qiskit_circuit)


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_run_quantum_task_unsupported_circuit_type(self, braket_service):
        """Test running task with unsupported circuit type."""
        unsupported_circuit = "invalid_circuit_type"
        
        with pytest.raises(TaskExecutionError, match="Unsupported circuit type"):
            braket_service.run_quantum_task(
                circuit=unsupported_circuit,
                device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1'
            )
    
    @patch('awslabs.amazon_braket_mcp_server.braket_service.AwsDevice')
    def test_run_quantum_task_execution_error(self, mock_aws_device, braket_service):
        """Test task execution error handling."""
        mock_device = MagicMock()
        mock_device.run.side_effect = Exception("Device error")
        mock_aws_device.return_value = mock_device
        
        circuit_def = QuantumCircuit(
            num_qubits=2,
            gates=[Gate(name='h', qubits=[0])]
        )
        
        with pytest.raises(TaskExecutionError, match="Error running quantum task"):
            braket_service.run_quantum_task(
                circuit=circuit_def,
                device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1'
            )
