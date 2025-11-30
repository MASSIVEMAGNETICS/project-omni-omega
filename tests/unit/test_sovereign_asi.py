"""
Unit tests for sovereign_asi_prototype.py module.
Tests HLHFM memory, Cognitive River, ExpandedLTN, QuantumCircuit, and SovereignASI components.
"""
import numpy as np
import pytest
import sys
import os
import torch

# Add parent directory to path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from sovereign_asi_prototype import (
    _unit_norm,
    _circ_conv,
    _superpose,
    _cos,
    _fractal_scales,
    _chunk_project,
    LiquidGate,
    HyperLiquidHolographicFractalMemory,
    Predicate,
    ExpandedLTN,
    QuantumCircuit,
    quantum_semiring_fusion,
    SimpleSNN,
    CognitiveRiver,
    SovereignASI
)


class TestHLHFMUtils:
    """Test HLHFM utility functions."""
    
    def test_unit_norm(self):
        """Test vector normalization."""
        vec = np.array([3.0, 4.0], dtype=np.float32)
        normed = _unit_norm(vec)
        assert np.isclose(np.linalg.norm(normed), 1.0)
        assert np.allclose(normed, [0.6, 0.8])
    
    def test_unit_norm_zero_vector(self):
        """Test normalization of near-zero vector."""
        vec = np.array([1e-15, 1e-15], dtype=np.float32)
        normed = _unit_norm(vec)
        # Should return normalized without division by zero (eps=1e-8)
        assert normed.shape == vec.shape
    
    def test_circ_conv(self):
        """Test circular convolution."""
        a = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        b = np.array([4.0, 5.0, 6.0], dtype=np.float32)
        result = _circ_conv(a, b)
        assert result.shape == a.shape
        assert isinstance(result, np.ndarray)
    
    def test_superpose(self):
        """Test vector superposition."""
        vec1 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        vec2 = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        vec3 = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        result = _superpose([vec1, vec2, vec3])
        
        assert result.shape == vec1.shape
        # Result should be normalized
        assert np.isclose(np.linalg.norm(result), 1.0)
    
    def test_superpose_empty(self):
        """Test superposition with empty list returns None."""
        result = _superpose([])
        assert result is None
    
    def test_cos(self):
        """Test cosine similarity."""
        a = np.array([1.0, 0.0], dtype=np.float32)
        b = np.array([1.0, 0.0], dtype=np.float32)
        assert np.isclose(_cos(a, b), 1.0)
        
        c = np.array([0.0, 1.0], dtype=np.float32)
        assert np.isclose(_cos(a, c), 0.0)
    
    def test_fractal_scales(self):
        """Test fractal scale generation."""
        scales = _fractal_scales(64, levels=4)
        assert len(scales) >= 1
        assert all(isinstance(s, int) for s in scales)
        assert all(s >= 8 for s in scales)
        assert all(s <= 64 for s in scales)
    
    def test_chunk_project(self):
        """Test chunk projection."""
        v = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
        proj = _chunk_project(v, 4)
        assert proj.shape == (4,)
        
        proj_smaller = _chunk_project(v, 2)
        assert proj_smaller.shape == (2,)


class TestLiquidGate:
    """Test LiquidGate temporal smoothing."""
    
    def test_init(self):
        """Test LiquidGate initialization."""
        gate = LiquidGate(dim=32, tau=0.5)
        assert gate.dim == 32
        assert gate.tau == 0.5
        assert gate.state.shape == (32,)
    
    def test_step(self):
        """Test LiquidGate temporal step."""
        gate = LiquidGate(dim=8, tau=1.0)
        inp = np.ones((8,), dtype=np.float32)
        
        out = gate.step(inp, dt=1.0)
        assert out.shape == (8,)
        assert not np.allclose(out, np.zeros(8))  # State should change


class TestHyperLiquidHolographicFractalMemory:
    """Test HLHFM memory system."""
    
    def test_init(self):
        """Test HLHFM initialization."""
        hlhfm = HyperLiquidHolographicFractalMemory(dim=32)
        assert hlhfm.dim == 32
        assert hlhfm.levels == 4
        assert len(hlhfm.gates) == 4
        assert len(hlhfm.entries) == 0
    
    def test_write(self):
        """Test memory write."""
        hlhfm = HyperLiquidHolographicFractalMemory(dim=32)
        result = hlhfm.write("test memory", {"emotion": "happy", "intent": "test"})
        
        assert "echo_id" in result
        assert "t" in result
        assert "scales_written" in result
        assert result["scales_written"] > 0
        assert len(hlhfm.entries) > 0
    
    def test_query(self):
        """Test memory query."""
        hlhfm = HyperLiquidHolographicFractalMemory(dim=32)
        hlhfm.write("hello world", {"emotion": "neutral", "intent": "greet"})
        hlhfm.write("goodbye world", {"emotion": "sad", "intent": "farewell"})
        
        results = hlhfm.query("hello", top_k=2)
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert "emotion" in results[0]
        assert "intent" in results[0]
        assert "raw" in results[0]
    
    def test_consolidate(self):
        """Test memory consolidation."""
        hlhfm = HyperLiquidHolographicFractalMemory(dim=32)
        hlhfm.write("test", {"emotion": "neutral"})
        
        original_trace = hlhfm.holo_trace.copy()
        hlhfm.consolidate()
        # Trace should potentially change after consolidation
        assert hlhfm.holo_trace.shape == original_trace.shape
    
    def test_decay_step(self):
        """Test memory decay."""
        hlhfm = HyperLiquidHolographicFractalMemory(dim=32)
        hlhfm.write("test", {"emotion": "neutral"})
        
        original_trace_norm = np.linalg.norm(hlhfm.holo_trace)
        hlhfm.decay_step(lam=0.1)
        new_trace_norm = np.linalg.norm(hlhfm.holo_trace)
        
        # Decay should reduce the trace magnitude
        assert new_trace_norm <= original_trace_norm


class TestPredicate:
    """Test Predicate neural module."""
    
    def test_init(self):
        """Test Predicate initialization."""
        pred = Predicate(input_dim=2, hidden_dim=16)
        assert pred is not None
    
    def test_forward(self):
        """Test Predicate forward pass."""
        pred = Predicate(input_dim=2, hidden_dim=16)
        x = torch.randn(4, 2)
        out = pred(x)
        
        assert out.shape == (4, 1)
        assert (out >= 0).all() and (out <= 1).all()  # Sigmoid output


class TestExpandedLTN:
    """Test Expanded Logic Tensor Network."""
    
    def test_init(self):
        """Test ExpandedLTN initialization."""
        ltn = ExpandedLTN()
        assert ltn.parent is not None
        assert ltn.child_of is not None
        assert ltn.cause is not None
        assert ltn.effect is not None
        assert ltn.sovereign is not None
        assert ltn.loyal is not None
    
    def test_axioms(self):
        """Test axiom satisfaction computation."""
        ltn = ExpandedLTN()
        x = torch.randn(8, 1)
        y = torch.randn(8, 1)
        
        sat = ltn.axioms(x, y)
        
        assert isinstance(sat, torch.Tensor)
        assert sat.ndim == 0 or sat.numel() == 1  # Scalar
        assert sat.item() >= 0.0 and sat.item() <= 1.0
    
    def test_parameters(self):
        """Test parameter collection."""
        ltn = ExpandedLTN()
        params = ltn.parameters()
        
        assert isinstance(params, list)
        assert len(params) > 0
        assert all(isinstance(p, torch.nn.Parameter) for p in params)
    
    def test_train(self):
        """Test brief training loop."""
        ltn = ExpandedLTN()
        # Run minimal training
        ltn.train(None, epochs=5)
        # No assertion needed - just verify it doesn't crash


class TestQuantumCircuit:
    """Test Torch-based Quantum Circuit simulation."""
    
    def test_init(self):
        """Test QuantumCircuit initialization."""
        qc = QuantumCircuit(num_qubits=2)
        assert qc.num_qubits == 2
        assert qc.theta.shape == (2,)
    
    def test_forward(self):
        """Test quantum circuit forward pass."""
        qc = QuantumCircuit(num_qubits=2)
        ptrace = qc()
        
        assert ptrace.shape == (2, 2)
        assert ptrace.dtype == torch.cfloat
    
    def test_quantum_semiring_fusion(self):
        """Test quantum semiring fusion function."""
        result = quantum_semiring_fusion(qubits=2)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == (2, 2)


class TestSimpleSNN:
    """Test Simple Spiking Neural Network approximation."""
    
    def test_init(self):
        """Test SimpleSNN initialization."""
        snn = SimpleSNN(input_size=32, hidden_size=64)
        assert snn is not None
    
    def test_forward(self):
        """Test SimpleSNN forward pass."""
        snn = SimpleSNN(input_size=32, hidden_size=64)
        x = torch.randn(1, 5, 32)  # (batch, seq, features)
        out = snn(x)
        
        assert out.shape == (1, 5, 64)
        assert (out >= 0).all()  # ReLU output


class TestCognitiveRiver:
    """Test Cognitive River stream merging."""
    
    def test_init(self):
        """Test CognitiveRiver initialization."""
        river = CognitiveRiver()
        
        assert len(river.STREAMS) == 8
        assert all(s in river.state for s in river.STREAMS)
        assert river.energy == 0.5
        assert river.stability == 0.8
    
    def test_set_status(self):
        """Test status stream setter."""
        river = CognitiveRiver()
        river.set_status({"health": 1.0})
        
        assert river.state["status"] == {"health": 1.0}
        assert river.priority_logits["status"] > 0
    
    def test_set_emotion(self):
        """Test emotion stream setter."""
        river = CognitiveRiver()
        river.set_emotion({"state": "happy"})
        
        assert river.state["emotion"] == {"state": "happy"}
    
    def test_set_memory(self):
        """Test memory stream setter."""
        river = CognitiveRiver()
        river.set_memory({"recall": ["item1", "item2"]})
        
        assert river.state["memory"]["recall"] == ["item1", "item2"]
    
    def test_set_awareness(self):
        """Test awareness stream setter."""
        river = CognitiveRiver()
        river.set_awareness({"clarity": 0.9})
        
        assert river.state["awareness"] == {"clarity": 0.9}
    
    def test_set_systems(self):
        """Test systems stream setter."""
        river = CognitiveRiver()
        river.set_systems({"load": 0.5})
        
        assert river.state["systems"] == {"load": 0.5}
    
    def test_set_user(self):
        """Test user stream setter."""
        river = CognitiveRiver()
        river.set_user({"input": "hello"})
        
        assert river.state["user"] == {"input": "hello"}
    
    def test_set_sensory(self):
        """Test sensory stream setter."""
        river = CognitiveRiver()
        river.set_sensory({"novelty": 0.7})
        
        assert river.state["sensory"] == {"novelty": 0.7}
    
    def test_set_realworld(self):
        """Test realworld stream setter."""
        river = CognitiveRiver()
        river.set_realworld({"urgency": 0.3})
        
        assert river.state["realworld"] == {"urgency": 0.3}
    
    def test_step_merge(self):
        """Test stream merging."""
        river = CognitiveRiver()
        river.set_status({"health": 1.0})
        river.set_emotion({"state": "neutral"})
        
        merged = river.step_merge()
        
        assert "t" in merged
        assert "weights" in merged
        assert "signal" in merged
        assert merged["signal"]["status"] == {"health": 1.0}
    
    def test_event_log(self):
        """Test event logging."""
        river = CognitiveRiver()
        river.set_status({"health": 1.0})
        river.set_emotion({"state": "happy"})
        
        assert len(river.event_log) == 2
        assert river.event_log[0]["key"] == "status"
        assert river.event_log[1]["key"] == "emotion"


class TestSovereignASI:
    """Test integrated Sovereign ASI system."""
    
    def test_init(self):
        """Test SovereignASI initialization."""
        import logging
        logging.getLogger().setLevel(logging.WARNING)  # Reduce noise
        
        asi = SovereignASI()
        
        assert asi.hlhfm is not None
        assert asi.river is not None
        assert asi.ltn is not None
        assert asi.snn is not None
        assert "loyalty" in asi.loyalty_matrix
    
    def test_process_input(self):
        """Test input processing."""
        import logging
        logging.getLogger().setLevel(logging.WARNING)  # Reduce noise
        
        asi = SovereignASI()
        result = asi.process_input("test input", emotion="curious", intent="explore")
        
        assert "merge" in result
        assert "sat" in result
        assert "quantum" in result
        assert "spikes" in result
        
        assert isinstance(result["sat"], float)
        assert isinstance(result["quantum"], np.ndarray)
        assert isinstance(result["spikes"], float)
    
    def test_loyalty_matrix(self):
        """Test loyalty matrix invariants."""
        import logging
        logging.getLogger().setLevel(logging.WARNING)
        
        asi = SovereignASI()
        
        assert asi.loyalty_matrix["loyalty"] >= 0.95
        assert asi.loyalty_matrix["protectiveness"] >= 0.9


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_full_workflow(self):
        """Test complete workflow from input to output."""
        import logging
        logging.getLogger().setLevel(logging.WARNING)
        
        asi = SovereignASI()
        
        # Process multiple inputs
        for text in ["Hello", "How are you?", "Goodbye"]:
            result = asi.process_input(text)
            assert "merge" in result
            assert "sat" in result
        
        # Consolidate and decay
        asi.hlhfm.consolidate()
        asi.hlhfm.decay_step()
        
        # Query memory
        memories = asi.hlhfm.query("Hello", top_k=3)
        assert len(memories) > 0
    
    def test_memory_persistence(self):
        """Test that memories persist across inputs."""
        import logging
        logging.getLogger().setLevel(logging.WARNING)
        
        asi = SovereignASI()
        
        # Write specific memory
        asi.process_input("specific memory content", emotion="important", intent="remember")
        
        # Query for it
        memories = asi.hlhfm.query("specific memory", top_k=5)
        
        assert len(memories) > 0
        # Should find the memory we just wrote
        found = any("specific" in m.get("raw", "") for m in memories)
        assert found


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
