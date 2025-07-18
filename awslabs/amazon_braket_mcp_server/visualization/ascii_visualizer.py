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

"""ASCII Visualization utilities for quantum circuits and results.

This module provides ASCII-based visualizations that are more model-friendly
than base64 encoded images, making it easier for AI models to understand
and reason about quantum circuits and their results.
"""

from typing import Dict, List, Any, Union
from ..models import QuantumCircuit, Gate, TaskResult


class ASCIICircuitVisualizer:
    """Generate ASCII representations of quantum circuits."""
    
    # Gate symbols for ASCII representation
    GATE_SYMBOLS = {
        'h': 'H',
        'x': 'X', 
        'y': 'Y',
        'z': 'Z',
        's': 'S',
        't': 'T',
        'cx': '●─X',
        'cy': '●─Y', 
        'cz': '●─Z',
        'ccx': '●─●─X',
        'swap': 'x─x',
        'rx': 'RX',
        'ry': 'RY',
        'rz': 'RZ',
        'measure': 'M',
        'measure_all': 'M',
        'barrier': '║',
    }
    
    def __init__(self):
        """Initialize the ASCII visualizer."""
        pass
    
    def visualize_circuit(self, circuit: QuantumCircuit) -> str:
        """Main method to visualize a circuit as ASCII.
        
        Args:
            circuit: The quantum circuit to visualize
            
        Returns:
            ASCII string representation of the circuit
        """
        result = self.circuit_to_ascii(circuit)
        return result["ascii_circuit"]
    
    def circuit_to_ascii(self, circuit: QuantumCircuit) -> Dict[str, Any]:
        """Convert a quantum circuit to ASCII representation.
        
        Args:
            circuit: The quantum circuit to visualize
            
        Returns:
            Dictionary containing ASCII representation and metadata
        """
        num_qubits = circuit.num_qubits
        gates = circuit.gates
        
        # Initialize circuit lines
        lines = []
        for i in range(num_qubits):
            lines.append(f"q{i}: ")
        
        # Track current position for each qubit line
        positions = [len(f"q{i}: ") for i in range(num_qubits)]
        max_pos = max(positions)
        
        # Pad all lines to same length
        for i in range(num_qubits):
            lines[i] += "─" * (max_pos - positions[i])
        
        # Process each gate
        gate_descriptions = []
        for gate in gates:
            if gate.name == 'measure_all':
                # Add measurement to all qubits
                for i in range(num_qubits):
                    lines[i] += "─M─"
                gate_descriptions.append("Measure all qubits")
                continue
                
            if gate.name in ['h', 'x', 'y', 'z', 's', 't']:
                # Single qubit gates
                qubit = gate.qubits[0] if gate.qubits else 0
                symbol = self.GATE_SYMBOLS.get(gate.name, gate.name.upper())
                
                # Pad other lines
                for i in range(num_qubits):
                    if i == qubit:
                        lines[i] += f"─{symbol}─"
                    else:
                        lines[i] += "─" * (len(symbol) + 2)
                        
                gate_descriptions.append(f"{symbol} gate on qubit {qubit}")
                
            elif gate.name in ['rx', 'ry', 'rz']:
                # Rotation gates with parameters
                qubit = gate.qubits[0] if gate.qubits else 0
                symbol = self.GATE_SYMBOLS.get(gate.name, gate.name.upper())
                param = gate.params[0] if gate.params else 0
                
                # Format parameter
                param_str = f"({param:.2f})" if isinstance(param, (int, float)) else f"({param})"
                full_symbol = f"{symbol}{param_str}"
                
                # Pad other lines
                for i in range(num_qubits):
                    if i == qubit:
                        lines[i] += f"─{full_symbol}─"
                    else:
                        lines[i] += "─" * (len(full_symbol) + 2)
                        
                gate_descriptions.append(f"{symbol} rotation gate on qubit {qubit} with parameter {param}")
                
            elif gate.name == 'cx':
                # CNOT gate
                control = gate.qubits[0] if len(gate.qubits) > 0 else 0
                target = gate.qubits[1] if len(gate.qubits) > 1 else 1
                
                for i in range(num_qubits):
                    if i == control:
                        lines[i] += "─●─"
                    elif i == target:
                        lines[i] += "─X─"
                    else:
                        lines[i] += "─│─"
                        
                gate_descriptions.append(f"CNOT gate: control qubit {control}, target qubit {target}")
                
            elif gate.name == 'swap':
                # SWAP gate
                qubit1 = gate.qubits[0] if len(gate.qubits) > 0 else 0
                qubit2 = gate.qubits[1] if len(gate.qubits) > 1 else 1
                
                for i in range(num_qubits):
                    if i == qubit1 or i == qubit2:
                        lines[i] += "─x─"
                    else:
                        lines[i] += "─│─"
                        
                gate_descriptions.append(f"SWAP gate between qubits {qubit1} and {qubit2}")
                
            else:
                # Generic gate representation
                symbol = gate.name.upper()[:3]  # Truncate to 3 chars
                affected_qubits = gate.qubits if gate.qubits else [0]
                
                for i in range(num_qubits):
                    if i in affected_qubits:
                        lines[i] += f"─{symbol}─"
                    else:
                        lines[i] += "─" * (len(symbol) + 2)
                        
                gate_descriptions.append(f"{gate.name} gate on qubits {affected_qubits}")
        
        # Join lines
        ascii_circuit = "\n".join(lines)
        
        return {
            "ascii_circuit": ascii_circuit,
            "gate_sequence": gate_descriptions,
            "num_qubits": num_qubits,
            "num_gates": len(gates),
            "description": self._generate_circuit_description(circuit)
        }
    
    def _generate_circuit_description(self, circuit: QuantumCircuit) -> str:
        """Generate a human-readable description of the circuit.
        
        Args:
            circuit: The quantum circuit
            
        Returns:
            String description of the circuit
        """
        descriptions = []
        
        # Analyze circuit structure
        has_superposition = any(gate.name == 'h' for gate in circuit.gates)
        has_entanglement = any(gate.name in ['cx', 'cy', 'cz'] for gate in circuit.gates)
        has_measurement = any(gate.name in ['measure', 'measure_all'] for gate in circuit.gates)
        
        if has_superposition:
            descriptions.append("creates superposition")
        if has_entanglement:
            descriptions.append("creates entanglement")
        if has_measurement:
            descriptions.append("includes measurements")
            
        if not descriptions:
            descriptions.append("applies quantum operations")
            
        base_desc = f"{circuit.num_qubits}-qubit circuit that " + ", ".join(descriptions)
        
        # Add specific circuit type detection
        if self._is_bell_pair(circuit):
            return f"Bell pair circuit: {base_desc}"
        elif self._is_ghz_state(circuit):
            return f"GHZ state circuit: {base_desc}"
        elif any(gate.name == 'qft' for gate in circuit.gates):
            return f"Quantum Fourier Transform: {base_desc}"
        else:
            return base_desc.capitalize()
    
    def _is_bell_pair(self, circuit: QuantumCircuit) -> bool:
        """Check if circuit creates a Bell pair."""
        if circuit.num_qubits != 2:
            return False
        gate_names = [gate.name for gate in circuit.gates if gate.name != 'measure_all']
        return gate_names == ['h', 'cx']
    
    def _is_ghz_state(self, circuit: QuantumCircuit) -> bool:
        """Check if circuit creates a GHZ state."""
        if circuit.num_qubits < 3:
            return False
        gate_names = [gate.name for gate in circuit.gates if gate.name != 'measure_all']
        expected = ['h'] + ['cx'] * (circuit.num_qubits - 1)
        return gate_names == expected


class ASCIIResultsVisualizer:
    """Generate ASCII representations of quantum measurement results."""
    
    def __init__(self):
        """Initialize the ASCII results visualizer."""
        pass
    
    def visualize_results(self, result: TaskResult) -> str:
        """Main method to visualize results as ASCII.
        
        Args:
            result: The quantum task result to visualize
            
        Returns:
            ASCII string representation of the results
        """
        result_data = self.results_to_ascii(result)
        return result_data["ascii_histogram"]
    
    def results_to_ascii(self, result: TaskResult) -> Dict[str, Any]:
        """Convert quantum task results to ASCII representation.
        
        Args:
            result: The quantum task result
            
        Returns:
            Dictionary containing ASCII representation and analysis
        """
        if not result.counts:
            return {
                "ascii_histogram": "No measurement data available",
                "analysis": {"error": "No counts data"}
            }
        
        # Sort counts by binary value
        sorted_counts = dict(sorted(result.counts.items()))
        total_shots = sum(sorted_counts.values())
        
        # Create ASCII histogram
        max_count = max(sorted_counts.values())
        max_bar_length = 40  # Maximum bar length in characters
        
        histogram_lines = []
        histogram_lines.append("Measurement Results Histogram:")
        histogram_lines.append("=" * 50)
        
        for state, count in sorted_counts.items():
            # Calculate bar length
            bar_length = int((count / max_count) * max_bar_length)
            bar = "█" * bar_length
            percentage = (count / total_shots) * 100
            
            # Format line
            line = f"|{state}⟩: {bar:<{max_bar_length}} {count:>4} ({percentage:5.1f}%)"
            histogram_lines.append(line)
        
        histogram_lines.append("=" * 50)
        histogram_lines.append(f"Total shots: {total_shots}")
        
        ascii_histogram = "\n".join(histogram_lines)
        
        # Generate analysis
        analysis = self._analyze_results(result)
        
        return {
            "ascii_histogram": ascii_histogram,
            "analysis": analysis,
            "summary": self._generate_summary(result, analysis)
        }
    
    def _analyze_results(self, result: TaskResult) -> Dict[str, Any]:
        """Analyze quantum measurement results.
        
        Args:
            result: The quantum task result
            
        Returns:
            Dictionary containing analysis results
        """
        if not result.counts:
            return {"error": "No measurement data"}
        
        sorted_counts = dict(sorted(result.counts.items()))
        total_shots = sum(sorted_counts.values())
        
        # Basic statistics
        num_unique_states = len(sorted_counts)
        most_probable_state = max(sorted_counts.items(), key=lambda x: x[1])
        least_probable_state = min(sorted_counts.items(), key=lambda x: x[1])
        
        # Calculate probabilities
        probabilities = {state: count/total_shots for state, count in sorted_counts.items()}
        
        # Detect quantum phenomena
        analysis = {
            "total_shots": total_shots,
            "unique_states_measured": num_unique_states,
            "most_probable_state": most_probable_state[0],
            "most_probable_count": most_probable_state[1],
            "most_probable_probability": most_probable_state[1] / total_shots,
            "probability_distribution": probabilities,
        }
        
        # Detect entanglement patterns
        if self._detect_bell_pair_pattern(sorted_counts):
            analysis["quantum_phenomenon"] = "Bell pair entanglement"
            analysis["entanglement_detected"] = True
            analysis["classical_correlation"] = self._calculate_correlation(sorted_counts)
        elif self._detect_ghz_pattern(sorted_counts):
            analysis["quantum_phenomenon"] = "GHZ state entanglement"
            analysis["entanglement_detected"] = True
        elif self._detect_superposition_pattern(sorted_counts):
            analysis["quantum_phenomenon"] = "Quantum superposition"
            analysis["superposition_detected"] = True
        else:
            analysis["quantum_phenomenon"] = "Classical-like distribution"
            analysis["entanglement_detected"] = False
        
        return analysis
    
    def _detect_bell_pair_pattern(self, counts: Dict[str, int]) -> bool:
        """Detect if results show Bell pair entanglement pattern."""
        # Bell pairs should only show |00⟩ and |11⟩ states
        states = set(counts.keys())
        return states.issubset({'00', '11'}) and len(states) == 2
    
    def _detect_ghz_pattern(self, counts: Dict[str, int]) -> bool:
        """Detect if results show GHZ state pattern."""
        # GHZ states should show all-0s and all-1s states
        states = set(counts.keys())
        if len(states) != 2:
            return False
        
        # Check if we have complementary all-0s and all-1s states
        state_list = list(states)
        if len(state_list[0]) != len(state_list[1]):
            return False
        
        return (set(state_list[0]) == {'0'} and set(state_list[1]) == {'1'}) or \
               (set(state_list[0]) == {'1'} and set(state_list[1]) == {'0'})
    
    def _detect_superposition_pattern(self, counts: Dict[str, int]) -> bool:
        """Detect if results show superposition pattern."""
        # Superposition typically shows relatively uniform distribution
        if len(counts) < 2:
            return False
        
        total = sum(counts.values())
        expected_prob = 1.0 / len(counts)
        
        # Check if probabilities are reasonably uniform (within 20% of expected)
        for count in counts.values():
            prob = count / total
            if abs(prob - expected_prob) > 0.2:
                return False
        
        return True
    
    def _calculate_correlation(self, counts: Dict[str, int]) -> float:
        """Calculate classical correlation for two-qubit states."""
        if len(counts) == 0:
            return 0.0
        
        total = sum(counts.values())
        correlated_count = counts.get('00', 0) + counts.get('11', 0)
        
        return correlated_count / total
    
    def _generate_summary(self, result: TaskResult, analysis: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the results.
        
        Args:
            result: The quantum task result
            analysis: The analysis results
            
        Returns:
            String summary of the results
        """
        if "error" in analysis:
            return "No measurement data available for analysis."
        
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"Executed {analysis['total_shots']} shots")
        summary_parts.append(f"Measured {analysis['unique_states_measured']} unique quantum states")
        
        # Most probable outcome
        most_prob = analysis['most_probable_state']
        most_prob_pct = analysis['most_probable_probability'] * 100
        summary_parts.append(f"Most probable outcome: |{most_prob}⟩ ({most_prob_pct:.1f}%)")
        
        # Quantum phenomena
        if analysis.get('entanglement_detected'):
            if 'classical_correlation' in analysis:
                corr_pct = analysis['classical_correlation'] * 100
                summary_parts.append(f"Quantum entanglement detected with {corr_pct:.1f}% correlation")
            else:
                summary_parts.append("Quantum entanglement detected")
        elif analysis.get('superposition_detected'):
            summary_parts.append("Quantum superposition observed")
        else:
            summary_parts.append("Classical-like measurement distribution")
        
        return ". ".join(summary_parts) + "."


# Combined visualizer class for convenience
class ASCIIVisualizer:
    """Combined ASCII visualizer for circuits and results."""
    
    def __init__(self):
        """Initialize the combined visualizer."""
        self.circuit_visualizer = ASCIICircuitVisualizer()
        self.results_visualizer = ASCIIResultsVisualizer()
    
    def visualize_circuit(self, circuit: QuantumCircuit) -> str:
        """Visualize a quantum circuit as ASCII.
        
        Args:
            circuit: The quantum circuit to visualize
            
        Returns:
            ASCII string representation of the circuit
        """
        return self.circuit_visualizer.visualize_circuit(circuit)
    
    def visualize_results(self, result: TaskResult) -> str:
        """Visualize quantum results as ASCII.
        
        Args:
            result: The quantum task result to visualize
            
        Returns:
            ASCII string representation of the results
        """
        return self.results_visualizer.visualize_results(result)
