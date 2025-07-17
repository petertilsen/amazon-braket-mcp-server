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

"""Tests for the BraketService class."""

import pytest
from unittest.mock import patch, MagicMock

from awslabs.amazon_braket_mcp_server.braket_service import BraketService
from awslabs.amazon_braket_mcp_server.models import QuantumCircuit, Gate, TaskResult, TaskStatus


@pytest.fixture
def mock_boto3_client():
    """Create a mock boto3 client for testing."""
    with patch('boto3.client') as mock_client:
        mock_braket = MagicMock()
        mock_client.return_value = mock_braket
        yield mock_braket


@pytest.fixture
def mock_qiskit_circuit():
    """Create a mock Qiskit circuit for testing."""
    with patch('qiskit.QuantumCircuit') as mock_circuit:
        yield mock_circuit.return_value


@pytest.fixture
def braket_service(mock_boto3_client):
    """Create a BraketService instance for testing."""
    return BraketService(region_name='us-west-2')


def test_create_qiskit_circuit(braket_service, mock_qiskit_circuit):
    """Test creating a Qiskit circuit."""
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
    
    # Check that the appropriate methods were called
    assert mock_qiskit_circuit.h.called
    assert mock_qiskit_circuit.cx.called
    assert mock_qiskit_circuit.measure_all.called
    assert result == mock_qiskit_circuit


@patch('awslabs.amazon_braket_mcp_server.braket_service.AwsDevice')
def test_run_quantum_task(mock_aws_device, braket_service, mock_qiskit_circuit):
    """Test running a quantum task."""
    # Mock the convert_to_braket_circuit method
    braket_service.convert_to_braket_circuit = MagicMock()
    braket_service.create_qiskit_circuit = MagicMock(return_value=mock_qiskit_circuit)
    
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
    assert braket_service.create_qiskit_circuit.called
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
    mock_result.measurements = [[0, 0], [0, 1], [1, 0], [1, 1]]
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
