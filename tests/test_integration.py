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

"""Integration tests for the Amazon Braket MCP Server."""

import pytest
from unittest.mock import patch, MagicMock

from awslabs.amazon_braket_mcp_server.server import (
    create_quantum_circuit,
    run_quantum_task,
    get_task_result,
    list_devices,
    create_bell_pair_circuit,
)
from awslabs.amazon_braket_mcp_server.models import TaskStatus


@pytest.fixture
def mock_braket_service():
    """Create a comprehensive mock BraketService for integration testing."""
    with patch('awslabs.amazon_braket_mcp_server.server.get_braket_service') as mock_get_service:
        mock_service = MagicMock()
        
        # Configure mock service methods
        mock_service.create_qiskit_circuit.return_value = MagicMock()
        mock_service.visualize_circuit.return_value = 'mock_visualization'
        mock_service.run_quantum_task.return_value = 'integration-task-123'
        
        mock_get_service.return_value = mock_service
        yield mock_service


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""
    
    def test_complete_quantum_circuit_workflow(self, mock_braket_service):
        """Test complete workflow: create circuit -> run task -> get results."""
        # Mock circuit creation response
        mock_circuit_def = {
            'num_qubits': 2,
            'gates': [
                {'name': 'h', 'qubits': [0]},
                {'name': 'cx', 'qubits': [0, 1]},
                {'name': 'measure_all'}
            ],
            'metadata': None
        }
        
        mock_braket_service.create_circuit_visualization.return_value = {
            'circuit_def': mock_circuit_def,
            'description': {'summary': 'Test circuit'},
            'ascii_visualization': 'q0: ─H──●─\nq1: ────X─',
            'visualization_file': '/path/to/circuit.png',
            'num_qubits': 2,
            'num_gates': 3
        }
        
        # Step 1: Create a quantum circuit
        circuit_result = create_quantum_circuit(
            num_qubits=2,
            gates=[
                {'name': 'h', 'qubits': [0]},
                {'name': 'cx', 'qubits': [0, 1]},
                {'name': 'measure_all'}
            ]
        )
        
        assert 'circuit_def' in circuit_result
        assert circuit_result['num_qubits'] == 2
        assert circuit_result['num_gates'] == 3
        
        # Step 2: Run the quantum task
        task_result = run_quantum_task(
            circuit=circuit_result['circuit_def'],
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            shots=1000
        )
        
        assert task_result['task_id'] == 'integration-task-123'
        assert task_result['status'] == 'CREATED'
        
        # Step 3: Mock task completion and get results
        from awslabs.amazon_braket_mcp_server.models import TaskResult
        mock_completed_result = TaskResult(
            task_id='integration-task-123',
            status=TaskStatus.COMPLETED,
            measurements=[[0, 0], [0, 1], [1, 0], [1, 1]],
            counts={'00': 250, '01': 250, '10': 250, '11': 250},
            device='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            shots=1000,
            execution_time=2.5,
            metadata={}
        )
        mock_braket_service.get_task_result.return_value = mock_completed_result
        
        final_result = get_task_result('integration-task-123')
        
        assert final_result['task_id'] == 'integration-task-123'
        assert final_result['status'] == TaskStatus.COMPLETED
        assert final_result['shots'] == 1000
        assert len(final_result['counts']) == 4
    
    def test_bell_pair_circuit_workflow(self, mock_braket_service):
        """Test Bell pair circuit creation and execution workflow."""
        # Mock bell pair circuit creation response
        mock_circuit_def = {
            'num_qubits': 2,
            'gates': [
                {'name': 'h', 'qubits': [0]},
                {'name': 'cx', 'qubits': [0, 1]},
                {'name': 'measure_all'}
            ],
            'metadata': None
        }
        
        mock_braket_service.create_circuit_visualization.return_value = {
            'circuit_def': mock_circuit_def,
            'description': {'summary': 'Bell pair circuit'},
            'ascii_visualization': 'q0: ─H──●─\nq1: ────X─',
            'visualization_file': '/path/to/bell.png',
            'num_qubits': 2,
            'num_gates': 3
        }
        
        # Create Bell pair circuit
        bell_result = create_bell_pair_circuit()
        
        assert 'circuit_def' in bell_result
        assert bell_result['num_qubits'] == 2
        assert bell_result['num_gates'] == 3
        
        # Verify the circuit has the correct gates
        circuit_def = bell_result['circuit_def']
        gate_names = [gate['name'] for gate in circuit_def['gates']]
        assert 'h' in gate_names
        assert 'cx' in gate_names
        assert 'measure_all' in gate_names
        
        # Run the Bell pair circuit
        task_result = run_quantum_task(
            circuit=circuit_def,
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            shots=2000
        )
        
        assert task_result['task_id'] == 'integration-task-123'
        assert task_result['shots'] == 2000
    
    def test_device_discovery_workflow(self, mock_braket_service):
        """Test device discovery and selection workflow."""
        from awslabs.amazon_braket_mcp_server.models import DeviceInfo, DeviceType
        
        # Mock available devices
        mock_devices = [
            DeviceInfo(
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
            ),
            DeviceInfo(
                device_arn='arn:aws:braket:::device/quantum-simulator/amazon/tn1',
                device_name='TN1',
                device_type=DeviceType.SIMULATOR,
                provider_name='Amazon',
                status='ONLINE',
                qubits=50,
                connectivity='full',
                paradigm='gate-based',
                max_shots=100000,
                supported_gates=['h', 'x', 'y', 'z', 'cx']
            )
        ]
        mock_braket_service.list_devices.return_value = mock_devices
        
        # List available devices
        devices_result = list_devices()
        
        assert len(devices_result) == 2
        assert devices_result[0]['device_name'] == 'SV1'
        assert devices_result[1]['device_name'] == 'TN1'
        
        # Select a device and create a circuit for it
        selected_device_arn = devices_result[0]['device_arn']
        
        # Mock circuit creation for device discovery test
        mock_circuit_def = {
            'num_qubits': 3,
            'gates': [
                {'name': 'h', 'qubits': [0]},
                {'name': 'h', 'qubits': [1]},
                {'name': 'h', 'qubits': [2]},
                {'name': 'measure_all'}
            ],
            'metadata': None
        }
        
        mock_braket_service.create_circuit_visualization.return_value = {
            'circuit_def': mock_circuit_def,
            'description': {'summary': 'Device discovery test circuit'},
            'ascii_visualization': 'q0: ─H─\nq1: ─H─\nq2: ─H─',
            'visualization_file': '/path/to/device_test.png',
            'num_qubits': 3,
            'num_gates': 4
        }
        
        circuit_result = create_quantum_circuit(
            num_qubits=3,
            gates=[
                {'name': 'h', 'qubits': [0]},
                {'name': 'h', 'qubits': [1]},
                {'name': 'h', 'qubits': [2]},
                {'name': 'measure_all'}
            ]
        )
        
        # Run on selected device
        task_result = run_quantum_task(
            circuit=circuit_result['circuit_def'],
            device_arn=selected_device_arn,
            shots=5000
        )
        
        assert task_result['device_arn'] == selected_device_arn
        assert task_result['shots'] == 5000


class TestErrorRecoveryWorkflows:
    """Test error handling and recovery in workflows."""
    
    def test_circuit_creation_error_recovery(self, mock_braket_service):
        """Test recovery from circuit creation errors."""
        # First attempt fails
        mock_braket_service.create_circuit_visualization.side_effect = Exception("Invalid gate")
        
        result = create_quantum_circuit(
            num_qubits=2,
            gates=[{'name': 'invalid_gate', 'qubits': [0]}]
        )
        
        assert 'error' in result
        assert 'Invalid gate' in result['error']
        
        # Second attempt succeeds
        mock_braket_service.create_circuit_visualization.side_effect = None
        mock_braket_service.create_circuit_visualization.return_value = {
            'circuit_def': {'num_qubits': 2, 'gates': [], 'metadata': None},
            'description': {'summary': 'Recovery test circuit'},
            'ascii_visualization': 'q0: ─H─',
            'visualization_file': '/path/to/recovery.png',
            'num_qubits': 2,
            'num_gates': 1
        }
        
        result = create_quantum_circuit(
            num_qubits=2,
            gates=[{'name': 'h', 'qubits': [0]}]
        )
        
        assert 'error' not in result
        assert result['num_qubits'] == 2
    
    def test_task_execution_error_recovery(self, mock_braket_service):
        """Test recovery from task execution errors."""
        # Mock circuit creation first
        mock_circuit_def = {
            'num_qubits': 1,
            'gates': [{'name': 'x', 'qubits': [0]}],
            'metadata': None
        }
        
        mock_braket_service.create_circuit_visualization.return_value = {
            'circuit_def': mock_circuit_def,
            'description': {'summary': 'Error recovery test circuit'},
            'ascii_visualization': 'q0: ─X─',
            'visualization_file': '/path/to/error_test.png',
            'num_qubits': 1,
            'num_gates': 1
        }
        
        # Create a valid circuit
        circuit_result = create_quantum_circuit(
            num_qubits=1,
            gates=[{'name': 'x', 'qubits': [0]}]
        )
        
        # First execution attempt fails
        mock_braket_service.run_quantum_task.side_effect = Exception("Device offline")
        
        task_result = run_quantum_task(
            circuit=circuit_result['circuit_def'],
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1'
        )
        
        assert 'error' in task_result
        assert 'Device offline' in task_result['error']
        
        # Second execution attempt succeeds
        mock_braket_service.run_quantum_task.side_effect = None
        mock_braket_service.run_quantum_task.return_value = 'recovery-task-456'
        
        task_result = run_quantum_task(
            circuit=circuit_result['circuit_def'],
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/tn1'
        )
        
        assert 'error' not in task_result
        assert task_result['task_id'] == 'recovery-task-456'


class TestPerformanceWorkflows:
    """Test performance-related workflows."""
    
    def test_large_circuit_workflow(self, mock_braket_service):
        """Test workflow with large quantum circuits."""
        # Create a large circuit (10 qubits, many gates)
        gates = []
        for i in range(10):
            gates.append({'name': 'h', 'qubits': [i]})
        
        for i in range(9):
            gates.append({'name': 'cx', 'qubits': [i, i + 1]})
        
        gates.append({'name': 'measure_all'})
        
        # Mock large circuit creation
        mock_circuit_def = {
            'num_qubits': 10,
            'gates': gates,
            'metadata': None
        }
        
        mock_braket_service.create_circuit_visualization.return_value = {
            'circuit_def': mock_circuit_def,
            'description': {'summary': 'Large 10-qubit circuit'},
            'ascii_visualization': 'q0-q9: Large circuit visualization',
            'visualization_file': '/path/to/large.png',
            'num_qubits': 10,
            'num_gates': len(gates)
        }
        
        circuit_result = create_quantum_circuit(
            num_qubits=10,
            gates=gates
        )
        
        assert circuit_result['num_qubits'] == 10
        assert circuit_result['num_gates'] == 20  # 10 H + 9 CNOT + 1 measure
        
        # Run with high shot count
        task_result = run_quantum_task(
            circuit=circuit_result['circuit_def'],
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            shots=10000
        )
        
        assert task_result['shots'] == 10000
    
    def test_batch_circuit_workflow(self, mock_braket_service):
        """Test workflow with multiple circuits."""
        circuits = []
        task_ids = []
        
        # Mock circuit creation for multiple circuits
        def mock_circuit_creation(*args, **kwargs):
            circuit_num = len(circuits)
            mock_circuit_def = {
                'num_qubits': 2,
                'gates': [
                    {'name': 'h', 'qubits': [0]},
                    {'name': 'rx', 'qubits': [1], 'params': [circuit_num * 0.5]},
                    {'name': 'cx', 'qubits': [0, 1]},
                    {'name': 'measure_all'}
                ],
                'metadata': None
            }
            return {
                'circuit_def': mock_circuit_def,
                'description': {'summary': f'Batch circuit {circuit_num}'},
                'ascii_visualization': f'q0: ─H──●─\nq1: ─RX──X─',
                'visualization_file': f'/path/to/batch_{circuit_num}.png',
                'num_qubits': 2,
                'num_gates': 4
            }
        
        mock_braket_service.create_circuit_visualization.side_effect = mock_circuit_creation
        
        # Create multiple circuits
        for i in range(3):
            circuit_result = create_quantum_circuit(
                num_qubits=2,
                gates=[
                    {'name': 'h', 'qubits': [0]},
                    {'name': 'rx', 'qubits': [1], 'params': [i * 0.5]},
                    {'name': 'cx', 'qubits': [0, 1]},
                    {'name': 'measure_all'}
                ]
            )
            circuits.append(circuit_result['circuit_def'])
        
        # Submit multiple tasks
        mock_braket_service.run_quantum_task.side_effect = [
            f'batch-task-{i}' for i in range(3)
        ]
        
        for i, circuit in enumerate(circuits):
            task_result = run_quantum_task(
                circuit=circuit,
                device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
                shots=1000
            )
            task_ids.append(task_result['task_id'])
        
        assert len(task_ids) == 3
        assert all('batch-task-' in task_id for task_id in task_ids)


class TestConfigurationWorkflows:
    """Test different configuration scenarios."""
    
    def test_s3_storage_workflow(self, mock_braket_service):
        """Test workflow with S3 result storage."""
        # Mock circuit creation
        mock_circuit_def = {
            'num_qubits': 2,
            'gates': [
                {'name': 'h', 'qubits': [0]},
                {'name': 'cx', 'qubits': [0, 1]},
                {'name': 'measure_all'}
            ],
            'metadata': None
        }
        
        mock_braket_service.create_circuit_visualization.return_value = {
            'circuit_def': mock_circuit_def,
            'description': {'summary': 'S3 storage test circuit'},
            'ascii_visualization': 'q0: ─H──●─\nq1: ────X─',
            'visualization_file': '/path/to/s3_test.png',
            'num_qubits': 2,
            'num_gates': 3
        }
        
        circuit_result = create_quantum_circuit(
            num_qubits=2,
            gates=[
                {'name': 'h', 'qubits': [0]},
                {'name': 'cx', 'qubits': [0, 1]},
                {'name': 'measure_all'}
            ]
        )
        
        # Run with S3 configuration
        task_result = run_quantum_task(
            circuit=circuit_result['circuit_def'],
            device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
            shots=1000,
            s3_bucket='quantum-results-bucket',
            s3_prefix='experiments/bell-states/'
        )
        
        assert task_result['task_id'] == 'integration-task-123'
        
        # Verify S3 parameters were passed to the service
        call_args = mock_braket_service.run_quantum_task.call_args
        assert call_args[1]['s3_bucket'] == 'quantum-results-bucket'
        assert call_args[1]['s3_prefix'] == 'experiments/bell-states/'
    
    def test_different_shot_counts_workflow(self, mock_braket_service):
        """Test workflow with different shot counts."""
        # Mock circuit creation
        mock_circuit_def = {
            'num_qubits': 1,
            'gates': [
                {'name': 'h', 'qubits': [0]},
                {'name': 'measure_all'}
            ],
            'metadata': None
        }
        
        mock_braket_service.create_circuit_visualization.return_value = {
            'circuit_def': mock_circuit_def,
            'description': {'summary': 'Shot count test circuit'},
            'ascii_visualization': 'q0: ─H─M─',
            'visualization_file': '/path/to/shot_test.png',
            'num_qubits': 1,
            'num_gates': 2
        }
        
        circuit_result = create_quantum_circuit(
            num_qubits=1,
            gates=[
                {'name': 'h', 'qubits': [0]},
                {'name': 'measure_all'}
            ]
        )
        
        shot_counts = [100, 1000, 10000]
        
        for shots in shot_counts:
            mock_braket_service.run_quantum_task.return_value = f'shots-{shots}-task'
            
            task_result = run_quantum_task(
                circuit=circuit_result['circuit_def'],
                device_arn='arn:aws:braket:::device/quantum-simulator/amazon/sv1',
                shots=shots
            )
            
            assert task_result['shots'] == shots
            assert task_result['task_id'] == f'shots-{shots}-task'
