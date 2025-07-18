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

"""Visualization utilities for quantum circuits and results.

This module provides model-friendly visualization including:
1. Descriptive text generation for circuits and results
2. File saving capabilities for visualizations
3. ASCII representations alongside binary data
"""

import os
import base64
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Union, Optional
from pathlib import Path

from ..models import QuantumCircuit, Gate, TaskResult
from .ascii_visualizer import ASCIICircuitVisualizer, ASCIIResultsVisualizer
from loguru import logger


class VisualizationUtils:
    """Utilities for quantum circuit and result visualization."""
    
    def __init__(self, workspace_dir: Optional[str] = None):
        """Initialize the visualization utils.
        
        Args:
            workspace_dir: Directory to save visualization files. If None, uses temp directory.
        """
        self.workspace_dir = workspace_dir or tempfile.gettempdir()
        self.ascii_circuit_visualizer = ASCIICircuitVisualizer()
        self.ascii_results_visualizer = ASCIIResultsVisualizer()
        
        # Create visualizations directory if it doesn't exist
        self.viz_dir = Path(self.workspace_dir) / "braket_visualizations"
        self.viz_dir.mkdir(exist_ok=True)
    
    def describe_circuit(self, circuit: QuantumCircuit) -> Dict[str, Any]:
        """Generate a human-readable description of a quantum circuit.
        
        Args:
            circuit: Quantum circuit to describe
            
        Returns:
            Dictionary containing circuit description and analysis
        """
        try:
            description = {
                "type": "quantum_circuit",
                "summary": self._generate_circuit_summary(circuit),
                "details": self._analyze_circuit_structure(circuit),
                "gate_sequence": self._describe_gate_sequence(circuit),
                "expected_behavior": self._predict_circuit_behavior(circuit),
                "complexity": self._assess_circuit_complexity(circuit)
            }
            
            return description
            
        except Exception as e:
            logger.exception(f"Error describing circuit: {str(e)}")
            return {"error": f"Failed to describe circuit: {str(e)}"}
    
    def describe_results(self, result: TaskResult) -> Dict[str, Any]:
        """Generate a human-readable description of quantum task results.
        
        Args:
            result: Task result to describe
            
        Returns:
            Dictionary containing result description and analysis
        """
        try:
            description = {
                "type": "quantum_results",
                "summary": self._generate_results_summary(result),
                "statistics": self._analyze_measurement_statistics(result),
                "distribution": self._describe_probability_distribution(result),
                "insights": self._extract_result_insights(result)
            }
            
            return description
            
        except Exception as e:
            logger.exception(f"Error describing results: {str(e)}")
            return {"error": f"Failed to describe results: {str(e)}"}
    
    def save_visualization_to_file(self, 
                                 base64_data: str, 
                                 filename: str, 
                                 description: str = "") -> str:
        """Save base64 visualization data to a file.
        
        Args:
            base64_data: Base64 encoded image data
            filename: Name for the saved file (without extension)
            description: Optional description to include in metadata
            
        Returns:
            Path to the saved file
        """
        try:
            # Generate timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{filename}_{timestamp}.png"
            file_path = self.viz_dir / safe_filename
            
            # Decode and save the image
            image_data = base64.b64decode(base64_data)
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            # Save metadata file
            metadata_path = self.viz_dir / f"{filename}_{timestamp}_metadata.txt"
            with open(metadata_path, 'w') as f:
                f.write(f"Visualization: {filename}\n")
                f.write(f"Created: {datetime.now().isoformat()}\n")
                f.write(f"Description: {description}\n")
                f.write(f"Image file: {safe_filename}\n")
            
            logger.info(f"Visualization saved to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.exception(f"Error saving visualization: {str(e)}")
            return f"Error saving file: {str(e)}"
    
    def create_circuit_response(self,
                                circuit: QuantumCircuit,
                                base64_viz: str,
                                circuit_type: str = "custom") -> Dict[str, Any]:
        """Create a response for circuit visualization.
        
        Args:
            circuit: The quantum circuit
            base64_viz: Base64 encoded visualization
            circuit_type: Type of circuit (e.g., "bell_pair", "ghz", "qft")
            
        Returns:
            Response dictionary
        """
        try:
            # Generate description
            description = self.describe_circuit(circuit)
            
            # Generate ASCII representation
            ascii_viz = self.ascii_circuit_visualizer.visualize_circuit(circuit)
            
            # Save visualization to file
            viz_filename = f"{circuit_type}_circuit"
            saved_path = self.save_visualization_to_file(
                base64_viz, 
                viz_filename, 
                description.get("summary", "")
            )
            
            return {
                "circuit_def": circuit.model_dump(),
                "description": description,
                "ascii_visualization": ascii_viz,
                "visualization_file": saved_path,
                "visualization_data": base64_viz,  # Keep original for compatibility
                "usage_note": f"Circuit visualization saved to {saved_path}. Use image viewer to see the detailed diagram.",
                "num_qubits": circuit.num_qubits,
                "num_gates": len(circuit.gates)
            }
            
        except Exception as e:
            logger.exception(f"Error creating circuit response: {str(e)}")
            return {"error": f"Failed to create response: {str(e)}"}
    
    def create_results_response(self,
                                result: TaskResult,
                                base64_viz: str) -> Dict[str, Any]:
        """Create a response for results visualization.
        
        Args:
            result: The task result
            base64_viz: Base64 encoded visualization
            
        Returns:
            Response dictionary
        """
        try:
            # Generate description
            description = self.describe_results(result)
            
            # Generate ASCII representation of results
            ascii_viz = self.ascii_results_visualizer.visualize_results(result)
            
            # Save visualization to file
            viz_filename = f"results_{result.task_id}"
            saved_path = self.save_visualization_to_file(
                base64_viz, 
                viz_filename, 
                description.get("summary", "")
            )
            
            return {
                "result": result.model_dump(),
                "description": description,
                "ascii_visualization": ascii_viz,
                "visualization_file": saved_path,
                "visualization_data": base64_viz,  # Keep original for compatibility
                "usage_note": f"Results visualization saved to {saved_path}. Use image viewer to see the detailed chart.",
            }
            
        except Exception as e:
            logger.exception(f"Error creating results response: {str(e)}")
            return {"error": f"Failed to create response: {str(e)}"}
    
    def _generate_circuit_summary(self, circuit: QuantumCircuit) -> str:
        """Generate a brief summary of the circuit."""
        gate_types = set(gate.name for gate in circuit.gates)
        
        if 'h' in gate_types and 'cx' in gate_types and len(circuit.gates) <= 4:
            if circuit.num_qubits == 2:
                return "Bell pair circuit creating quantum entanglement between 2 qubits"
            else:
                return f"GHZ state circuit creating multi-qubit entanglement across {circuit.num_qubits} qubits"
        elif 'qft' in gate_types:
            return f"Quantum Fourier Transform circuit on {circuit.num_qubits} qubits"
        elif len(gate_types) == 1 and 'h' in gate_types:
            return f"Superposition circuit applying Hadamard gates to {circuit.num_qubits} qubits"
        else:
            return f"Custom quantum circuit with {len(circuit.gates)} gates on {circuit.num_qubits} qubits"
    
    def _analyze_circuit_structure(self, circuit: QuantumCircuit) -> Dict[str, Any]:
        """Analyze the structure of the circuit."""
        gate_counts = {}
        for gate in circuit.gates:
            gate_counts[gate.name] = gate_counts.get(gate.name, 0) + 1
        
        return {
            "total_gates": len(circuit.gates),
            "gate_types": list(gate_counts.keys()),
            "gate_counts": gate_counts,
            "qubits_used": circuit.num_qubits,
            "has_measurements": any(gate.name.startswith('measure') for gate in circuit.gates),
            "has_entangling_gates": any(gate.name in ['cx', 'cy', 'cz', 'ccx'] for gate in circuit.gates)
        }
    
    def _describe_gate_sequence(self, circuit: QuantumCircuit) -> List[str]:
        """Describe the sequence of gates in human-readable form."""
        descriptions = []
        
        for i, gate in enumerate(circuit.gates):
            if gate.name == 'h':
                descriptions.append(f"Step {i+1}: Apply Hadamard gate to qubit {gate.qubits[0]} (creates superposition)")
            elif gate.name == 'x':
                descriptions.append(f"Step {i+1}: Apply Pauli-X gate to qubit {gate.qubits[0]} (bit flip)")
            elif gate.name == 'cx':
                descriptions.append(f"Step {i+1}: Apply CNOT gate from qubit {gate.qubits[0]} to qubit {gate.qubits[1]} (creates entanglement)")
            elif gate.name == 'measure_all':
                descriptions.append(f"Step {i+1}: Measure all qubits")
            elif gate.name.startswith('measure'):
                descriptions.append(f"Step {i+1}: Measure qubit {gate.qubits[0] if gate.qubits else 'unknown'}")
            else:
                descriptions.append(f"Step {i+1}: Apply {gate.name.upper()} gate to qubit(s) {gate.qubits}")
        
        return descriptions
    
    def _predict_circuit_behavior(self, circuit: QuantumCircuit) -> str:
        """Predict the expected behavior of the circuit."""
        gate_names = [gate.name for gate in circuit.gates]
        
        if 'h' in gate_names and 'cx' in gate_names:
            if circuit.num_qubits == 2:
                return "Creates Bell state |00⟩ + |11⟩, showing perfect correlation in measurements"
            else:
                return f"Creates GHZ state with {circuit.num_qubits} qubits showing multi-party entanglement"
        elif 'qft' in gate_names:
            return "Performs quantum Fourier transform, useful for period finding and Shor's algorithm"
        elif all(gate.name == 'h' for gate in circuit.gates if gate.name != 'measure_all'):
            return "Creates equal superposition of all computational basis states"
        else:
            return "Custom quantum computation with specific gate sequence"
    
    def _assess_circuit_complexity(self, circuit: QuantumCircuit) -> Dict[str, Any]:
        """Assess the complexity of the circuit."""
        return {
            "depth": len(circuit.gates),  # Simplified depth calculation
            "width": circuit.num_qubits,
            "complexity_level": "low" if len(circuit.gates) <= 5 else "medium" if len(circuit.gates) <= 20 else "high",
            "estimated_runtime": "fast" if len(circuit.gates) <= 10 else "moderate" if len(circuit.gates) <= 50 else "slow"
        }
    
    def _generate_results_summary(self, result: TaskResult) -> str:
        """Generate a summary of the results."""
        if not result.counts:
            return "No measurement results available"
        
        total_shots = sum(result.counts.values())
        num_outcomes = len(result.counts)
        most_frequent = max(result.counts.items(), key=lambda x: x[1])
        
        return f"Measured {num_outcomes} different outcomes over {total_shots} shots. Most frequent: {most_frequent[0]} ({most_frequent[1]} times, {most_frequent[1]/total_shots*100:.1f}%)"
    
    def _analyze_measurement_statistics(self, result: TaskResult) -> Dict[str, Any]:
        """Analyze measurement statistics."""
        if not result.counts:
            return {"error": "No measurement data"}
        
        total_shots = sum(result.counts.values())
        probabilities = {outcome: count/total_shots for outcome, count in result.counts.items()}
        
        return {
            "total_shots": total_shots,
            "unique_outcomes": len(result.counts),
            "probabilities": probabilities,
            "most_probable": max(probabilities.items(), key=lambda x: x[1]),
            "least_probable": min(probabilities.items(), key=lambda x: x[1]),
            "entropy": self._calculate_entropy(probabilities)
        }
    
    def _describe_probability_distribution(self, result: TaskResult) -> Dict[str, Any]:
        """Describe the probability distribution of results."""
        if not result.counts:
            return {"error": "No measurement data"}
        
        total_shots = sum(result.counts.values())
        probabilities = {outcome: count/total_shots for outcome, count in result.counts.items()}
        
        # Check for common patterns
        if len(probabilities) == 2 and all(abs(p - 0.5) < 0.1 for p in probabilities.values()):
            pattern = "uniform_binary"
            description = "Nearly equal probability between two outcomes (typical of Bell states)"
        elif len(probabilities) == 1:
            pattern = "deterministic"
            description = "Single outcome observed (deterministic result)"
        elif max(probabilities.values()) > 0.8:
            pattern = "highly_biased"
            description = "One outcome dominates (>80% probability)"
        else:
            pattern = "mixed"
            description = "Mixed probability distribution across multiple outcomes"
        
        return {
            "pattern": pattern,
            "description": description,
            "distribution_type": self._classify_distribution(probabilities)
        }
    
    def _extract_result_insights(self, result: TaskResult) -> List[str]:
        """Extract insights from the results."""
        insights = []
        
        if not result.counts:
            return ["No measurement data available for analysis"]
        
        total_shots = sum(result.counts.values())
        probabilities = {outcome: count/total_shots for outcome, count in result.counts.items()}
        
        # Check for entanglement signatures
        if len(probabilities) == 2:
            outcomes = list(probabilities.keys())
            if all(outcome in ['00', '11'] for outcome in outcomes):
                insights.append("Results suggest quantum entanglement (Bell state pattern)")
            elif all(outcome in ['01', '10'] for outcome in outcomes):
                insights.append("Results suggest anti-correlated entanglement")
        
        # Check for superposition
        if len(probabilities) > 2 and max(probabilities.values()) < 0.6:
            insights.append("Results suggest quantum superposition across multiple states")
        
        # Check for classical behavior
        if len(probabilities) == 1:
            insights.append("Deterministic result suggests classical computation or measurement")
        
        return insights
    
    def _calculate_entropy(self, probabilities: Dict[str, float]) -> float:
        """Calculate Shannon entropy of probability distribution."""
        import math
        return -sum(p * math.log2(p) for p in probabilities.values() if p > 0)
    
    def _classify_distribution(self, probabilities: Dict[str, float]) -> str:
        """Classify the type of probability distribution."""
        values = list(probabilities.values())
        
        if len(values) == 1:
            return "deterministic"
        elif len(values) == 2 and abs(values[0] - values[1]) < 0.1:
            return "uniform_binary"
        elif all(abs(p - 1/len(values)) < 0.1 for p in values):
            return "uniform"
        elif max(values) > 0.8:
            return "peaked"
        else:
            return "mixed"
