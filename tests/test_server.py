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

"""Tests for the Amazon Braket MCP Server."""

import pytest
from unittest.mock import patch, MagicMock

from awslabs.amazon_braket_mcp_server.server import (
    create_quantum_circuit,
    create_bell_pair_circuit,
    list_devices,
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
        MagicMock(dict=lambda: {"device_arn": "arn1", "device_name": "Device 1"}),
        MagicMock(dict=lambda: {"device_arn": "arn2", "device_name": "Device 2"}),
    ]
    
    # Call the function
    result = list_devices()
    
    # Check the result
    assert len(result) == 2
    assert result[0]["device_arn"] == "arn1"
    assert result[1]["device_name"] == "Device 2"
    assert mock_braket_service.list_devices.called
