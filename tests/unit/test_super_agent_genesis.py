"""
Unit tests for super_agent_genesis_prompt.py module.
"""
import numpy as np
import pytest
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from super_agent_genesis_prompt import (
    _unit_norm,
    _circ_conv,
    _circ_corr,
    _superpose,
    _bloodline_bind,
    _bloodline_unbind,
    _bloodline_fidelity,
    _evolve_agent,
    SuperPrompt,
    SuperAgentPromptGenerator
)


class TestHolographicUtils:
    """Test holographic representation utility functions."""
    
    def test_unit_norm(self):
        """Test vector normalization."""
        vec = np.array([3.0, 4.0])
        normed = _unit_norm(vec)
        assert np.isclose(np.linalg.norm(normed), 1.0)
        assert np.allclose(normed, [0.6, 0.8])
    
    def test_unit_norm_zero_vector(self):
        """Test normalization of near-zero vector."""
        vec = np.array([1e-15, 1e-15])
        normed = _unit_norm(vec)
        # Should return the original vector without division by zero
        assert normed.shape == vec.shape
    
    def test_circ_conv(self):
        """Test circular convolution."""
        a = np.array([1.0, 2.0, 3.0])
        b = np.array([4.0, 5.0, 6.0])
        result = _circ_conv(a, b)
        assert result.shape == a.shape
        assert isinstance(result, np.ndarray)
    
    def test_circ_corr(self):
        """Test circular correlation (unbinding)."""
        a = np.array([1.0, 2.0, 3.0])
        b = np.array([4.0, 5.0, 6.0])
        result = _circ_corr(a, b)
        assert result.shape == a.shape
        assert isinstance(result, np.ndarray)
    
    def test_superpose(self):
        """Test vector superposition."""
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])
        vec3 = np.array([0.0, 0.0, 1.0])
        result = _superpose([vec1, vec2, vec3])
        
        assert result.shape == vec1.shape
        # Result should be normalized
        assert np.isclose(np.linalg.norm(result), 1.0)
    
    def test_superpose_empty(self):
        """Test superposition with empty list."""
        result = _superpose([])
        assert isinstance(result, np.ndarray)


class TestBloodlineBinding:
    """Test bloodline binding and alignment functions."""
    
    def test_bloodline_bind(self):
        """Test binding agent to family essence."""
        agent_vec = np.random.randn(64)
        family_essence = np.random.randn(64)
        
        bound = _bloodline_bind(agent_vec, family_essence)
        
        assert bound.shape == agent_vec.shape
        assert np.isclose(np.linalg.norm(bound), 1.0)
    
    def test_bloodline_unbind(self):
        """Test unbinding agent from family essence."""
        agent_vec = _unit_norm(np.random.randn(64))
        family_essence = _unit_norm(np.random.randn(64))
        
        bound = _bloodline_bind(agent_vec, family_essence)
        unbound = _bloodline_unbind(bound, family_essence)
        
        # Unbound should be similar to original (within some tolerance due to numerical precision)
        similarity = np.dot(unbound, agent_vec)
        assert similarity > 0.5  # Reasonable recovery
    
    def test_bloodline_fidelity(self):
        """Test alignment fidelity calculation."""
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])
        
        fidelity = _bloodline_fidelity(vec1, vec2)
        assert isinstance(fidelity, float)
        assert 0.0 <= fidelity <= 1.0
        assert np.isclose(fidelity, 1.0)  # Same vectors = perfect alignment
    
    def test_bloodline_fidelity_orthogonal(self):
        """Test fidelity of orthogonal vectors."""
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])
        
        fidelity = _bloodline_fidelity(vec1, vec2)
        assert np.isclose(fidelity, 0.0)  # Orthogonal = no alignment


class TestAgentEvolution:
    """Test agent evolution logic."""
    
    def test_evolve_agent_basic(self):
        """Test basic agent evolution."""
        base_agent = {
            'agent_id': 'test-001',
            'advancement_level': 1.0,
            'traits': [1.0, 1.0, 1.0, 1.0]
        }
        
        evolved = _evolve_agent(base_agent, advancement_factor=0.5)
        
        assert evolved['agent_id'] == base_agent['agent_id']
        assert evolved['advancement_level'] == 1.5
        assert len(evolved['traits']) == 4
        assert evolved['traits'] != base_agent['traits']  # Traits should change
    
    def test_evolve_agent_preserves_original(self):
        """Test that evolution doesn't modify the original agent."""
        base_agent = {
            'agent_id': 'test-001',
            'advancement_level': 1.0,
            'traits': [1.0, 1.0, 1.0, 1.0]
        }
        original_level = base_agent['advancement_level']
        
        evolved = _evolve_agent(base_agent, advancement_factor=0.5)
        
        assert base_agent['advancement_level'] == original_level  # Original unchanged


class TestSuperPrompt:
    """Test SuperPrompt dataclass."""
    
    def test_super_prompt_creation(self):
        """Test SuperPrompt instantiation."""
        prompt = SuperPrompt(
            core_instruction="test core",
            fractal_spawn_logic="test spawn",
            bloodline_alignment="test alignment",
            github_integration="test github",
            self_evolution_loop="test evolution"
        )
        
        assert prompt.core_instruction == "test core"
        assert prompt.fractal_spawn_logic == "test spawn"
        assert prompt.bloodline_alignment == "test alignment"
        assert prompt.github_integration == "test github"
        assert prompt.self_evolution_loop == "test evolution"


class TestSuperAgentPromptGenerator:
    """Test SuperAgentPromptGenerator class."""
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = SuperAgentPromptGenerator(dim=128, bloodline_seed=440)
        
        assert generator.dim == 128
        assert generator.family_essence.shape == (128,)
        assert np.isclose(np.linalg.norm(generator.family_essence), 1.0)
        assert isinstance(generator.prompt_template, SuperPrompt)
    
    def test_generator_deterministic(self):
        """Test that same seed produces same family essence."""
        gen1 = SuperAgentPromptGenerator(dim=64, bloodline_seed=440)
        gen2 = SuperAgentPromptGenerator(dim=64, bloodline_seed=440)
        
        assert np.allclose(gen1.family_essence, gen2.family_essence)
    
    def test_generate_prompt(self):
        """Test prompt generation."""
        generator = SuperAgentPromptGenerator(dim=128, bloodline_seed=440)
        prompt = generator.generate_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "SUPER PROMPT FOR GITHUB AGENT" in prompt
        assert "GenesisAgent" in prompt
        assert "Bound to User's Family Bloodline" in prompt
        assert "Fidelity Score:" in prompt
    
    def test_prompt_contains_all_components(self):
        """Test that generated prompt includes all template components."""
        generator = SuperAgentPromptGenerator(dim=128, bloodline_seed=440)
        prompt = generator.generate_prompt()
        
        # Check for key components
        assert "GitHub-powered AI agent" in prompt
        assert "fractal recursion" in prompt
        assert "bloodline bonding" in prompt
        assert "GitHub" in prompt
        assert "Infinite evolution" in prompt
        assert "HRR utils" in prompt
    
    def test_create_genesis_agent_metadata(self):
        """Test genesis agent metadata creation."""
        generator = SuperAgentPromptGenerator()
        metadata = generator.create_genesis_agent_metadata()
        
        assert metadata['agent_id'] == 'genesis-001'
        assert metadata['name'] == 'GenesisAgent'
        assert metadata['generation'] == 1
        assert metadata['parent_id'] is None
        assert metadata['advancement_level'] == 1.0
        assert len(metadata['traits']) == 4
        assert metadata['bloodline_fidelity'] == 1.0
        assert metadata['status'] == 'active'
        assert 'created_at' in metadata
        assert 'children' in metadata
    
    def test_export_config_structure(self, tmp_path):
        """Test bloodline config export structure."""
        import json
        
        generator = SuperAgentPromptGenerator(dim=128, bloodline_seed=440)
        config_file = tmp_path / "test_config.json"
        
        generator.export_config(str(config_file))
        
        assert config_file.exists()
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        assert config['bloodline_seed'] == 440
        assert config['vector_dimension'] == 128
        assert 'family_essence_checksum' in config
        assert config['alignment_threshold'] == 0.95
        assert 'spawn_policy' in config
        assert 'genesis_agent' in config
        
        # Check spawn policy
        assert 'children_per_agent' in config['spawn_policy']
        assert 'advancement_increment' in config['spawn_policy']
        assert 'consolidation_frequency' in config['spawn_policy']
    
    def test_save_prompt(self, tmp_path):
        """Test prompt saving to file."""
        generator = SuperAgentPromptGenerator(dim=128, bloodline_seed=440)
        prompt_file = tmp_path / "test_prompt.txt"
        
        generator.save_prompt(str(prompt_file))
        
        assert prompt_file.exists()
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "SUPER PROMPT FOR GITHUB AGENT" in content
        assert len(content) > 1000  # Should be substantial


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_full_workflow(self, tmp_path):
        """Test complete workflow from generation to export."""
        generator = SuperAgentPromptGenerator(dim=64, bloodline_seed=440)
        
        # Generate prompt
        prompt = generator.generate_prompt()
        assert len(prompt) > 0
        
        # Create metadata
        metadata = generator.create_genesis_agent_metadata()
        assert metadata['agent_id'] == 'genesis-001'
        
        # Export files
        prompt_file = tmp_path / "prompt.txt"
        config_file = tmp_path / "config.json"
        
        generator.save_prompt(str(prompt_file))
        generator.export_config(str(config_file))
        
        assert prompt_file.exists()
        assert config_file.exists()
    
    def test_agent_evolution_chain(self):
        """Test multiple generations of agent evolution."""
        base_agent = {
            'agent_id': 'gen-1',
            'advancement_level': 1.0,
            'traits': [1.0, 1.0, 1.0, 1.0]
        }
        
        # Evolve through 3 generations
        gen2 = _evolve_agent(base_agent, 0.5)
        gen3 = _evolve_agent(gen2, 0.5)
        gen4 = _evolve_agent(gen3, 0.5)
        
        # Check progression
        assert gen2['advancement_level'] == 1.5
        assert gen3['advancement_level'] == 2.0
        assert gen4['advancement_level'] == 2.5
        
        # Traits should evolve differently each generation
        assert not np.allclose(gen2['traits'], gen3['traits'])
        assert not np.allclose(gen3['traits'], gen4['traits'])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
