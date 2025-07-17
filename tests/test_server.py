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

"""Comprehensive tests for the Amazon Braket MCP Server."""

import os
import pytest
from unittest.mock import patch, MagicMock

from awslabs.amazon_braket_mcp_server.server import (
    create_quantum_circuit,
    create_bell_pair_circuit,
    list_devices,
    run_quantum_task,
    get_task_result,
    get_device_info,
    cancel_quantum_task,
    search_quantum_tasks,
    create_ghz_circuit,
    create_qft_circuit,
    visualize_circuit,
    visualize_results,
    get_default_device_arn,
)
from awslabs.amazon_braket_mcp_server.models import (
    QuantumCircuit, Gate, TaskResult, TaskStatus, DeviceInfo, DeviceType
)


@pytest.fixture
def mock_braket_service():
    """Create a mock BraketService for testing."""
    with patch('awslabs.amazon_braket_mcp_server.server.get_braket_service') as mock_get_service:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        yield mock_service


def test_create_quantum_circuit(mock_braket_service):
    """Test creating a quantum circuit."""
    # Mock the create_qiskit_circuit and visualize_circuit methods
    mock_braket_service.create_qiskit_circuit.return_value = MagicMock()
    mock_braket_service.visualize_circuit.return_value = "base64_image_data"
    
    # Call the function
    result = create_quantum_circuit(
        num_qubits=2,
        gates=[
            {"name": "h", "qubits": [0]},
            {"name": "cx", "qubits": [0, 1]},
        ],
    )
    
    # Check the result
    assert "circuit_def" in result
    assert "visualization" in result
    assert result["num_qubits"] == 2
    assert result["num_gates"] == 2
    assert mock_braket_service.create_qiskit_circuit.called
    assert mock_braket_service.visualize_circuit.called


def test_create_bell_pair_circuit(mock_braket_service):
    """Test creating a Bell pair circuit."""
    # Mock the create_bell_pair_circuit and visualize_circuit methods
    mock_braket_service.create_bell_pair_circuit.return_value = MagicMock()
    mock_braket_service.visualize_circuit.return_value = "base64_image_data"
    
    # Call the function
    result = create_bell_pair_circuit()
    
    # Check the result
    assert "circuit_def" in result
    assert "visualization" in result
    assert result["num_qubits"] == 2
    assert mock_braket_service.create_bell_pair_circuit.called
    assert mock_braket_service.visualize_circuit.called


def test_list_devices(mock_braket_service):
    """Test listing devices."""
    # Mock the list_devices method
    mock_braket_service.list_devices.return_value = [
        MagicMock(model_dump=lambda: {"device_arn": "arn1", "device_name": "Device 1"}),
        MagicMock(model_dump=lambda: {"device_arn": "arn2", "device_name": "Device 2"}),
    ]
    
    # Call the function
    result = list_devices()
    
    # Check the result
    assert len(result) == 2
    assert result[0]["device_arn"] == "arn1"
    assert result[1]["device_name"] == "Device 2"
    assert mock_braket_service.list_devices.called

class TestQuantumTaskExecution:
    """Test quantum task execution endpoints."""
    
    def test_run_quantum_task_success(self, mock_braket_service):
        """Test successful quantum task execution."""
        mock_braket_service.run_quantum_task.return_value = 'task-123'
        
        circuit = {
            'num_qubits': 2,
            'gates': [
                {'name': 'h', 'qubits': [0]},
                {'name': 'cx', 'qubits': [0, 1]},
                {'name': 'measure_all'}
            ]
        }
        
        result = run_quantum_task(
            circuit=circuit,
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            shots=1000
        )
        
        assert result['task_id'] == 'task-123'
        assert result['status'] == 'CREATED'
        assert result['device_arn'] == 'arn:aws:braket:::device/quantum-simulator/amazon/sv1'
        assert result['shots'] == 1000
        
        mock_braket_service.run_quantum_task.assert_called_once()
    
    def test_run_quantum_task_with_s3_config(self, mock_braket_service):
        """Test quantum task execution with S3 configuration."""
        mock_braket_service.run_quantum_task.return_value = 'task-456'
        
        circuit = {
            'num_qubits': 1,
            'gates': [{'name': 'x', 'qubits': [0]}]
        }
        
        result = run_quantum_task(
            circuit=circuit,
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            shots=500,
            s3_bucket='my-bucket',
            s3_prefix='results/'
        )
        
        assert result['task_id'] == 'task-456'
        assert result['shots'] == 500
        
        # Verify S3 parameters were passed
        call_args = mock_braket_service.run_quantum_task.call_args
        assert call_args[1]['s3_bucket'] == 'my-bucket'
        assert call_args[1]['s3_prefix'] == 'results/'
    
    def test_run_quantum_task_error(self, mock_braket_service):
        """Test quantum task execution error handling."""
        mock_braket_service.run_quantum_task.side_effect = Exception("Device unavailable")
        
        circuit = {'num_qubits': 1, 'gates': []}
        
        result = run_quantum_task(
            circuit=circuit,
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1'
        )
        
        assert 'error' in result
        assert 'Device unavailable' in result['error']


class TestTaskResultRetrieval:
    """Test task result retrieval endpoints."""
    
    def test_get_task_result_success(self, mock_braket_service):
        """Test successful task result retrieval."""
        mock_result = TaskResult(
            task_id='task-123',
            status=TaskStatus.COMPLETED,
            measurements=[[0, 1], [1, 0]],
            counts={'01': 500, '10': 500},
            device='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            shots=1000,
            execution_time=5.5,
            metadata={'custom': 'data'}
        )
        mock_braket_service.get_task_result.return_value = mock_result
        
        result = get_task_result('task-123')
        
        assert result['task_id'] == 'task-123'
        assert result['status'] == TaskStatus.COMPLETED
        assert result['measurements'] == [[0, 1], [1, 0]]
        assert result['counts'] == {'01': 500, '10': 500}
        assert result['execution_time'] == 5.5
    
    def test_get_task_result_error(self, mock_braket_service):
        """Test task result retrieval error handling."""
        mock_braket_service.get_task_result.side_effect = Exception("Task not found")
        
        result = get_task_result('invalid-task')
        
        assert 'error' in result
        assert 'Task not found' in result['error']


class TestDeviceManagement:
    """Test device management endpoints."""
    
    def test_get_device_info_success(self, mock_braket_service):
        """Test successful device info retrieval."""
        mock_device = DeviceInfo(
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            device_name='SV1',
            device_type=DeviceType.SIMULATOR,
            provider_name='Amazon',
            status='ONLINE',
            qubits=34,
            connectivity='full',
            paradigm='gate-based',
            max_shots=100000,
            supported_gates=['h', 'x', 'y', 'z', 'cx']
        )
        mock_braket_service.get_device_info.return_value = mock_device
        
        result = get_device_info('arn:aws:braket:::device/quantum-simulator/amazon/sv1')
        
        assert result['device_arn'] == 'arn:aws:braket:::device/quantum-simulator/amazon/sv1'
        assert result['device_name'] == 'SV1'
        assert result['device_type'] == DeviceType.SIMULATOR
        assert result['qubits'] == 34
        assert result['max_shots'] == 100000
    
    def test_get_device_info_error(self, mock_braket_service):
        """Test device info retrieval error handling."""
        mock_braket_service.get_device_info.side_effect = Exception("Device not found")
        
        result = get_device_info('invalid-arn')
        
        assert 'error' in result
        assert 'Device not found' in result['error']


class TestTaskManagement:
    """Test task management endpoints."""
    
    def test_cancel_quantum_task_success(self, mock_braket_service):
        """Test successful task cancellation."""
        mock_braket_service.cancel_quantum_task.return_value = True
        
        result = cancel_quantum_task('task-123')
        
        assert result['cancelled'] is True
        assert result['task_id'] == 'task-123'
        mock_braket_service.cancel_quantum_task.assert_called_once_with('task-123')
    
    def test_cancel_quantum_task_failure(self, mock_braket_service):
        """Test task cancellation failure."""
        mock_braket_service.cancel_quantum_task.return_value = False
        
        result = cancel_quantum_task('task-123')
        
        assert result['cancelled'] is False
        assert result['task_id'] == 'task-123'
    
    def test_cancel_quantum_task_error(self, mock_braket_service):
        """Test task cancellation error handling."""
        mock_braket_service.cancel_quantum_task.side_effect = Exception("Cannot cancel")
        
        result = cancel_quantum_task('task-123')
        
        assert 'error' in result
        assert 'Cannot cancel' in result['error']
    
    def test_search_quantum_tasks_success(self, mock_braket_service):
        """Test successful task search."""
        mock_tasks = [
            {
                'quantumTaskArn': 'task-123',
                'status': 'COMPLETED',
                'deviceArn': 'arn:aws:braket:::device/quantum-simulator/amazon/sv1'
            },
            {
                'quantumTaskArn': 'task-456',
                'status': 'RUNNING',
                'deviceArn': 'arn:aws:braket:::device/quantum-simulator/amazon/sv1'
            }
        ]
        mock_braket_service.search_quantum_tasks.return_value = mock_tasks
        
        result = search_quantum_tasks(
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            state='COMPLETED',
            max_results=10
        )
        
        assert result == mock_tasks
        
        mock_braket_service.search_quantum_tasks.assert_called_once_with(
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            state='COMPLETED',
            max_results=10,
            created_after=None
        )
    
    def test_search_quantum_tasks_error(self, mock_braket_service):
        """Test task search error handling."""
        mock_braket_service.search_quantum_tasks.side_effect = Exception("Search failed")
        
        result = search_quantum_tasks()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert 'error' in result[0]
        assert 'Search failed' in result[0]['error']


class TestCircuitCreation:
    """Test circuit creation endpoints."""
    
    def test_create_ghz_circuit_success(self, mock_braket_service):
        """Test successful GHZ circuit creation."""
        mock_braket_service.create_qiskit_circuit.return_value = MagicMock()
        mock_braket_service.visualize_circuit.return_value = 'base64_image'
        
        result = create_ghz_circuit(num_qubits=3)
        
        assert result['num_qubits'] == 3
        assert result['num_gates'] == 4  # H + 2 CNOT + measure_all
        assert result['visualization'] == 'base64_image'
        assert 'circuit_def' in result
        
        # The server creates the circuit directly, not via create_qiskit_circuit
        mock_braket_service.visualize_circuit.assert_called_once()
    
    def test_create_ghz_circuit_error(self, mock_braket_service):
        """Test GHZ circuit creation error handling."""
        mock_braket_service.visualize_circuit.side_effect = Exception("Circuit error")
        
        result = create_ghz_circuit(num_qubits=2)
        
        assert 'error' in result
        assert 'Circuit error' in result['error']
    
    def test_create_qft_circuit_success(self, mock_braket_service):
        """Test successful QFT circuit creation."""
        mock_braket_service.create_qiskit_circuit.return_value = MagicMock()
        mock_braket_service.visualize_circuit.return_value = 'base64_image'
        
        result = create_qft_circuit(num_qubits=4)
        
        assert result['num_qubits'] == 4
        assert result['description'] == 'Quantum Fourier Transform'
        assert result['visualization'] == 'base64_image'
        assert 'circuit_def' in result
        
        # The server creates the circuit directly, not via create_qiskit_circuit
        mock_braket_service.visualize_circuit.assert_called_once()
    
    def test_create_qft_circuit_error(self, mock_braket_service):
        """Test QFT circuit creation error handling."""
        mock_braket_service.visualize_circuit.side_effect = Exception("Visualization error")
        
        result = create_qft_circuit(num_qubits=3)
        
        assert 'error' in result
        assert 'Visualization error' in result['error']


class TestVisualization:
    """Test visualization endpoints."""
    
    def test_visualize_circuit_success(self, mock_braket_service):
        """Test successful circuit visualization."""
        mock_braket_service.visualize_circuit.return_value = 'base64_encoded_image'
        
        circuit = {
            'num_qubits': 2,
            'gates': [
                {'name': 'h', 'qubits': [0]},
                {'name': 'cx', 'qubits': [0, 1]}
            ]
        }
        
        result = visualize_circuit(circuit)
        
        assert result['visualization'] == 'base64_encoded_image'
        
        # The server creates a QuantumCircuit object and then visualizes it
        mock_braket_service.visualize_circuit.assert_called_once()
    
    def test_visualize_circuit_error(self, mock_braket_service):
        """Test circuit visualization error handling."""
        mock_braket_service.visualize_circuit.side_effect = Exception("Invalid circuit")
        
        circuit = {'num_qubits': 2, 'gates': [{'name': 'h', 'qubits': [0]}]}
        
        result = visualize_circuit(circuit)
        
        assert 'error' in result
        assert 'Invalid circuit' in result['error']
    
    def test_visualize_results_success(self, mock_braket_service):
        """Test successful results visualization."""
        mock_braket_service.visualize_results.return_value = 'base64_plot_image'
        
        results = {
            'task_id': 'test-task',
            'status': 'COMPLETED',
            'device': 'test-device',
            'shots': 1000,
            'counts': {'00': 250, '01': 250, '10': 250, '11': 250},
            'measurements': [[0, 0], [0, 1], [1, 0], [1, 1]]
        }
        
        result = visualize_results(results)
        
        assert result['visualization'] == 'base64_plot_image'
        
        mock_braket_service.visualize_results.assert_called_once()
    
    def test_visualize_results_error(self, mock_braket_service):
        """Test results visualization error handling."""
        mock_braket_service.visualize_results.side_effect = Exception("Plot error")
        
        results = {
            'task_id': 'test-task',
            'status': 'COMPLETED', 
            'device': 'test-device',
            'shots': 1000,
            'counts': {'00': 500, '11': 500}
        }
        
        result = visualize_results(results)
        
        assert 'error' in result
        assert 'Plot error' in result['error']


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_run_quantum_task_minimal_circuit(self, mock_braket_service):
        """Test running task with minimal circuit."""
        mock_braket_service.run_quantum_task.return_value = 'task-minimal'
        
        circuit = {'num_qubits': 1, 'gates': []}
        
        result = run_quantum_task(
            circuit=circuit,
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1'
        )
        
        assert result['task_id'] == 'task-minimal'
        assert result['shots'] == 1000  # default value
    
    def test_search_quantum_tasks_no_filters(self, mock_braket_service):
        """Test task search without filters."""
        mock_braket_service.search_quantum_tasks.return_value = []
        
        result = search_quantum_tasks()
        
        assert result == []
        
        # Verify called with default parameters
        mock_braket_service.search_quantum_tasks.assert_called_once_with(
            device_arn=None,
            state=None,
            max_results=10,
            created_after=None
        )
    
    def test_create_ghz_circuit_single_qubit(self, mock_braket_service):
        """Test GHZ circuit creation with single qubit."""
        mock_braket_service.create_qiskit_circuit.return_value = MagicMock()
        mock_braket_service.visualize_circuit.return_value = 'single_qubit_image'
        
        result = create_ghz_circuit(num_qubits=1)
        
        assert result['num_qubits'] == 1
        assert result['num_gates'] == 2  # H + measure_all
        
    def test_create_qft_circuit_single_qubit(self, mock_braket_service):
        """Test QFT circuit creation with single qubit."""
        mock_braket_service.create_qiskit_circuit.return_value = MagicMock()
        mock_braket_service.visualize_circuit.return_value = 'qft_single_image'
        
        result = create_qft_circuit(num_qubits=1)
        
        assert result['num_qubits'] == 1
        assert result['description'] == 'Quantum Fourier Transform'


# ============================================================================
# DEFAULT DEVICE ARN TESTS
# ============================================================================

class TestDefaultDeviceArn:
    """Test default device ARN functionality."""
    
    def test_get_default_device_arn_with_env_var(self):
        """Test getting default device ARN from environment variable."""
        test_arn = "arn:aws:braket:::device/quantum-simulator/amazon/tn1"
        
        with patch.dict(os.environ, {'BRAKET_DEFAULT_DEVICE_ARN': test_arn}):
            result = get_default_device_arn()
            assert result == test_arn
    
    def test_get_default_device_arn_without_env_var(self):
        """Test getting default device ARN when environment variable is not set."""
        with patch.dict(os.environ, {}, clear=True):
            result = get_default_device_arn()
            assert result == 'arn:aws:braket:::device/quantum-simulator/amazon/sv1'
    
    def test_get_default_device_arn_empty_env_var(self):
        """Test getting default device ARN when environment variable is empty."""
        with patch.dict(os.environ, {'BRAKET_DEFAULT_DEVICE_ARN': ''}):
            result = get_default_device_arn()
            assert result == 'arn:aws:braket:::device/quantum-simulator/amazon/sv1'


class TestRunQuantumTaskWithDefaultDevice:
    """Test run_quantum_task with default device ARN functionality."""
    
    @patch('awslabs.amazon_braket_mcp_server.server.get_braket_service')
    def test_run_quantum_task_with_explicit_device_arn(self, mock_get_service):
        """Test run_quantum_task with explicitly provided device ARN."""
        mock_service = MagicMock()
        mock_service.run_quantum_task.return_value = 'task-123'
        mock_get_service.return_value = mock_service
        
        circuit = {
            'num_qubits': 2,
            'gates': [
                {'name': 'h', 'qubits': [0]},
                {'name': 'cx', 'qubits': [0, 1]},
                {'name': 'measure_all'}
            ]
        }
        
        explicit_arn = "arn:aws:braket:::device/quantum-simulator/amazon/tn1"
        
        result = run_quantum_task(
            circuit=circuit,
            device_arn=explicit_arn,
            shots=1000
        )
        
        assert result['task_id'] == 'task-123'
        assert result['device_arn'] == explicit_arn
        
        # Verify the service was called with the explicit ARN
        mock_service.run_quantum_task.assert_called_once()
        call_args = mock_service.run_quantum_task.call_args
        assert call_args[1]['device_arn'] == explicit_arn
    
    @patch('awslabs.amazon_braket_mcp_server.server.get_braket_service')
    @patch('awslabs.amazon_braket_mcp_server.server.get_default_device_arn')
    def test_run_quantum_task_with_default_device_arn(self, mock_get_default_arn, mock_get_service):
        """Test run_quantum_task using default device ARN when none provided."""
        mock_service = MagicMock()
        mock_service.run_quantum_task.return_value = 'task-456'
        mock_get_service.return_value = mock_service
        
        default_arn = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"
        mock_get_default_arn.return_value = default_arn
        
        circuit = {
            'num_qubits': 1,
            'gates': [{'name': 'h', 'qubits': [0]}]
        }
        
        # Call without device_arn parameter
        result = run_quantum_task(
            circuit=circuit,
            shots=500
        )
        
        assert result['task_id'] == 'task-456'
        assert result['device_arn'] == default_arn
        
        # Verify the default ARN function was called
        mock_get_default_arn.assert_called_once()
        
        # Verify the service was called with the default ARN
        mock_service.run_quantum_task.assert_called_once()
        call_args = mock_service.run_quantum_task.call_args
        assert call_args[1]['device_arn'] == default_arn
    
    @patch('awslabs.amazon_braket_mcp_server.server.get_braket_service')
    def test_run_quantum_task_with_none_device_arn(self, mock_get_service):
        """Test run_quantum_task when device_arn is explicitly set to None."""
        mock_service = MagicMock()
        mock_service.run_quantum_task.return_value = 'task-789'
        mock_get_service.return_value = mock_service
        
        circuit = {
            'num_qubits': 1,
            'gates': [{'name': 'x', 'qubits': [0]}]
        }
        
        with patch.dict(os.environ, {'BRAKET_DEFAULT_DEVICE_ARN': 'arn:aws:braket:::device/quantum-simulator/amazon/dm1'}):
            result = run_quantum_task(
                circuit=circuit,
                device_arn=None,  # Explicitly None
                shots=100
            )
            
            assert result['task_id'] == 'task-789'
            assert result['device_arn'] == 'arn:aws:braket:::device/quantum-simulator/amazon/dm1'
            
            # Verify the service was called with the environment variable ARN
            mock_service.run_quantum_task.assert_called_once()
            call_args = mock_service.run_quantum_task.call_args
            assert call_args[1]['device_arn'] == 'arn:aws:braket:::device/quantum-simulator/amazon/dm1'


class TestDefaultDeviceArnIntegration:
    """Test default device ARN integration with different scenarios."""
    
    @patch('awslabs.amazon_braket_mcp_server.server.get_braket_service')
    def test_multiple_tasks_with_mixed_device_specification(self, mock_get_service):
        """Test multiple tasks with mixed device ARN specification."""
        mock_service = MagicMock()
        mock_service.run_quantum_task.side_effect = ['task-1', 'task-2', 'task-3']
        mock_get_service.return_value = mock_service
        
        circuit = {'num_qubits': 1, 'gates': [{'name': 'h', 'qubits': [0]}]}
        
        custom_arn = "arn:aws:braket:::device/quantum-simulator/amazon/tn1"
        default_arn = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"
        
        with patch.dict(os.environ, {'BRAKET_DEFAULT_DEVICE_ARN': default_arn}):
            # Task 1: Explicit device ARN
            result1 = run_quantum_task(circuit=circuit, device_arn=custom_arn)
            
            # Task 2: No device ARN (should use default)
            result2 = run_quantum_task(circuit=circuit)
            
            # Task 3: Explicit None (should use default)
            result3 = run_quantum_task(circuit=circuit, device_arn=None)
            
            # Verify results
            assert result1['device_arn'] == custom_arn
            assert result2['device_arn'] == default_arn
            assert result3['device_arn'] == default_arn
            
            # Verify service calls
            assert mock_service.run_quantum_task.call_count == 3
            
            # Check each call's device ARN
            calls = mock_service.run_quantum_task.call_args_list
            assert calls[0][1]['device_arn'] == custom_arn
            assert calls[1][1]['device_arn'] == default_arn
            assert calls[2][1]['device_arn'] == default_arn
    
    def test_environment_variable_precedence(self):
        """Test that environment variable takes precedence over hardcoded default."""
        env_arn = "arn:aws:braket:::device/quantum-simulator/amazon/dm1"
        
        # Test with environment variable set
        with patch.dict(os.environ, {'BRAKET_DEFAULT_DEVICE_ARN': env_arn}):
            result = get_default_device_arn()
            assert result == env_arn
        
        # Test without environment variable (should use hardcoded default)
        with patch.dict(os.environ, {}, clear=True):
            result = get_default_device_arn()
            assert result == 'arn:aws:braket:::device/quantum-simulator/amazon/sv1'
    
    def test_empty_string_environment_variable(self):
        """Test behavior when environment variable is set to empty string."""
        with patch.dict(os.environ, {'BRAKET_DEFAULT_DEVICE_ARN': ''}):
            result = get_default_device_arn()
            # Empty string should fall back to hardcoded default
            assert result == 'arn:aws:braket:::device/quantum-simulator/amazon/sv1'
