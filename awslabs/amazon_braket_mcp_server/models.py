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

"""Data Models Module for Amazon Braket.

This module defines the core data structures and types used throughout the Amazon Braket
interface. It includes models for quantum circuits, gates, and task results.

The models use Python's dataclass decorator for clean, type-safe data structures
that represent both the quantum circuit structure and its contents.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any


class GateType(str, Enum):
    """Enumeration of supported quantum gates."""

    # Single-qubit gates
    H = "h"  # Hadamard
    X = "x"  # Pauli-X
    Y = "y"  # Pauli-Y
    Z = "z"  # Pauli-Z
    S = "s"  # S gate (sqrt(Z))
    T = "t"  # T gate (sqrt(S))
    RX = "rx"  # Rotation around X-axis
    RY = "ry"  # Rotation around Y-axis
    RZ = "rz"  # Rotation around Z-axis
    
    # Two-qubit gates
    CX = "cx"  # Controlled-X (CNOT)
    CY = "cy"  # Controlled-Y
    CZ = "cz"  # Controlled-Z
    SWAP = "swap"  # SWAP gate
    
    # Three-qubit gates
    CCX = "ccx"  # Toffoli gate (Controlled-Controlled-X)
    
    # Measurement
    MEASURE = "measure"  # Measurement
    MEASURE_ALL = "measure_all"  # Measure all qubits


class Gate(BaseModel):
    """Represents a quantum gate in a circuit.
    
    Attributes:
        name: The name of the gate (from GateType)
        qubits: List of qubit indices the gate acts on
        params: Optional parameters for parameterized gates (e.g., rotation angles)
    """
    
    name: str
    qubits: List[int] = []
    params: Optional[List[float]] = None


class QuantumCircuit(BaseModel):
    """Represents a quantum circuit.
    
    Attributes:
        num_qubits: Number of qubits in the circuit
        gates: List of gates in the circuit
        metadata: Optional metadata about the circuit
    """
    
    num_qubits: int
    gates: List[Gate]
    metadata: Optional[Dict[str, Any]] = None


class TaskStatus(str, Enum):
    """Enumeration of possible quantum task statuses."""
    
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskResult(BaseModel):
    """Represents the result of a quantum task.
    
    Attributes:
        task_id: The ID of the quantum task
        status: The status of the task
        measurements: The measurement results (if available)
        counts: Counts of each measurement outcome
        device: The device the task ran on
        shots: Number of shots used
        execution_time: Time taken to execute the task (in seconds)
        metadata: Additional metadata about the task
    """
    
    task_id: str
    status: TaskStatus
    measurements: Optional[List[List[int]]] = None
    counts: Optional[Dict[str, int]] = None
    device: str
    shots: int
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class DeviceType(str, Enum):
    """Enumeration of device types."""
    
    QPU = "QPU"  # Quantum Processing Unit (physical quantum computer)
    SIMULATOR = "SIMULATOR"  # Quantum simulator


class DeviceInfo(BaseModel):
    """Information about a quantum device.
    
    Attributes:
        device_arn: The ARN of the device
        device_name: The name of the device
        device_type: The type of the device (QPU or SIMULATOR)
        provider_name: The provider of the device
        status: The current status of the device
        qubits: Number of qubits supported by the device
        connectivity: Description of qubit connectivity
        paradigm: The quantum computing paradigm (gate-based, annealing, etc.)
        max_shots: Maximum number of shots supported
        supported_gates: List of gates supported by the device
    """
    
    device_arn: str
    device_name: str
    device_type: DeviceType
    provider_name: str
    status: str
    qubits: int
    connectivity: Optional[str] = None
    paradigm: str
    max_shots: int
    supported_gates: List[str] = []
