"""
Tests for Victor Swarm Monolith components
"""
import pytest
import tempfile
import os
import torch

from victor.victor_swarm_monolith import (
    NeuroSymbolicReflector,
    FractalAttentionHead,
    VictorBrain,
    VictorSoul,
    detect_emotion,
)


class TestNeuroSymbolicReflector:
    """Test NeuroSymbolicReflector module"""
    
    def test_init(self):
        """Test initialization with various dimensions"""
        reflector = NeuroSymbolicReflector(dim=64)
        assert reflector.p.in_features == 64
        assert reflector.p.out_features == 64
        assert reflector.sym.shape == (1, 64)
    
    def test_forward(self):
        """Test forward pass"""
        reflector = NeuroSymbolicReflector(dim=128)
        x = torch.randn(2, 128)  # batch of 2
        out = reflector(x)
        assert out.shape == (2, 128)


class TestFractalAttentionHead:
    """Test FractalAttentionHead module"""
    
    def test_init(self):
        """Test initialization"""
        fractal = FractalAttentionHead(dim=64, depth=3)
        assert fractal.qkv.in_features == 64
        assert fractal.qkv.out_features == 192  # dim * 3
        assert fractal.depth == 3
        assert fractal.w.shape == (3, 64, 64)
    
    def test_forward_single_token(self):
        """Test forward pass with single token sequence"""
        fractal = FractalAttentionHead(dim=64)
        x = torch.randn(1, 1, 64)  # batch=1, seq=1, dim=64
        out = fractal(x)
        assert out.shape == (1, 1, 64)


class TestVictorBrain:
    """Test VictorBrain module"""
    
    def test_init(self):
        """Test initialization"""
        brain = VictorBrain(dim=256)
        assert brain.embed.num_embeddings == 256
        assert brain.embed.embedding_dim == 256
        assert brain.out.out_features == 256
        assert brain.memory_bank == []
    
    def test_forward(self):
        """Test forward pass with text input"""
        brain = VictorBrain(dim=64)
        logits, vec = brain("Hello")
        assert logits.shape == (1, 256)  # output vocabulary
        assert vec.shape == (1, 64)
        assert len(brain.memory_bank) == 1
    
    def test_memory_bank_limit(self):
        """Test memory bank doesn't exceed limit"""
        brain = VictorBrain(dim=64)
        for i in range(60):
            brain(f"Message {i}")
        assert len(brain.memory_bank) == 50  # limited to 50


class TestVictorSoul:
    """Test VictorSoul persistence"""
    
    def test_init_new(self):
        """Test initialization with new state"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_soul.json")
            soul = VictorSoul(path=path)
            assert soul.state["loop"] == 0
            assert soul.state["emotion"] == "neutral"
            assert soul.state["memory"] == []
    
    def test_log(self):
        """Test logging interactions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_soul.json")
            soul = VictorSoul(path=path)
            soul.log("input", "output", "joy")
            assert soul.state["loop"] == 1
            assert soul.state["emotion"] == "joy"
            assert len(soul.state["memory"]) == 1
            assert soul.state["memory"][0]["in"] == "input"
            assert soul.state["memory"][0]["out"] == "output"
    
    def test_save_load(self):
        """Test saving and loading state"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_soul.json")
            
            # Create and log
            soul1 = VictorSoul(path=path)
            soul1.log("test", "response")
            soul1.save()
            
            # Load in new instance
            soul2 = VictorSoul(path=path)
            assert soul2.state["loop"] == 1


class TestDetectEmotion:
    """Test emotion detection"""
    
    def test_joy(self):
        """Test joy detection"""
        assert detect_emotion("I love this!") == "joy"
    
    def test_anger(self):
        """Test anger detection"""
        assert detect_emotion("I hate it") == "anger"
        assert detect_emotion("kill the process") == "anger"
    
    def test_sadness(self):
        """Test sadness detection"""
        assert detect_emotion("This makes me sad") == "sadness"
    
    def test_fear(self):
        """Test fear detection"""
        assert detect_emotion("I fear the outcome") == "fear"
    
    def test_neutral(self):
        """Test neutral (default)"""
        assert detect_emotion("Hello world") == "neutral"
        assert detect_emotion("") == "neutral"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
