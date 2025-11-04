"""
Tests for Brain Builder components
"""
import pytest
import tempfile
import json
from pathlib import Path

from app.engines.brainbuilder import BrainLoader, BrainCompiler, BrainSimulator
from app.engines.brainbuilder.schemas import BrainSpec


class TestBrainLoader:
    """Test Brain Loader"""
    
    def test_load_from_dict(self):
        """Test loading brain spec from dictionary"""
        loader = BrainLoader()
        
        spec_dict = {
            "id": "test-brain",
            "name": "Test Brain",
            "adapter": "aai_psm",
            "format": "composite",
            "defaults": {
                "temperature": 0.7,
                "max_tokens": 256
            }
        }
        
        brain_spec = loader.load_from_dict(spec_dict)
        
        assert brain_spec.id == "test-brain"
        assert brain_spec.name == "Test Brain"
        assert brain_spec.adapter == "aai_psm"
    
    def test_validate_valid_spec(self):
        """Test validation of valid spec"""
        loader = BrainLoader()
        
        spec_dict = {
            "id": "valid-brain",
            "name": "Valid Brain",
            "adapter": "aai_psm",
            "format": "composite"
        }
        
        result = loader.validate(spec_dict)
        
        assert result["valid"] is True
        assert result["brain_id"] == "valid-brain"
    
    def test_validate_invalid_spec(self):
        """Test validation of invalid spec"""
        loader = BrainLoader()
        
        spec_dict = {
            # Missing required 'id' field
            "name": "Invalid Brain",
            "adapter": "aai_psm"
        }
        
        result = loader.validate(spec_dict)
        
        assert result["valid"] is False
        assert "error" in result


class TestBrainCompiler:
    """Test Brain Compiler"""
    
    def test_compile_basic(self):
        """Test compiling a basic brain spec"""
        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = BrainCompiler(output_dir=tmpdir)
            
            spec = BrainSpec(
                id="test-brain",
                name="Test Brain",
                adapter="aai_psm",
                format="composite",
                defaults={"temperature": 0.7}
            )
            
            result = compiler.compile(spec)
            
            assert result["status"] == "success"
            assert result["brain_id"] == "test-brain"
            assert len(result["artifacts"]) > 0
    
    def test_compile_with_defense(self):
        """Test compiling brain with defense aura"""
        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = BrainCompiler(output_dir=tmpdir)
            
            spec = BrainSpec(
                id="defended-brain",
                name="Defended Brain",
                adapter="aai_psm",
                format="composite",
                defense={"enabled": True, "strictness": "medium"}
            )
            
            result = compiler.compile(spec)
            
            # Check that aura artifact was generated
            aura_artifacts = [a for a in result["artifacts"] if a["type"] == "aura"]
            assert len(aura_artifacts) > 0
    
    def test_compile_with_epa(self):
        """Test compiling brain with EPA seeds"""
        with tempfile.TemporaryDirectory() as tmpdir:
            compiler = BrainCompiler(output_dir=tmpdir)
            
            spec = BrainSpec(
                id="epa-brain",
                name="EPA Brain",
                adapter="aai_psm",
                format="composite",
                epa_seeds=["reasoning", "helpfulness"]
            )
            
            result = compiler.compile(spec)
            
            # Check that skillpack artifact was generated
            skillpack_artifacts = [a for a in result["artifacts"] 
                                  if a["type"] == "skillpack"]
            assert len(skillpack_artifacts) > 0


class TestBrainSimulator:
    """Test Brain Simulator"""
    
    def test_simulate(self):
        """Test simulating brain behavior"""
        simulator = BrainSimulator()
        
        spec = BrainSpec(
            id="sim-brain",
            name="Simulation Brain",
            adapter="aai_psm",
            format="composite"
        )
        
        result = simulator.simulate(spec, num_prompts=5)
        
        assert result["status"] == "success"
        assert result["num_prompts"] == 5
        assert len(result["results"]) == 5
        assert "analysis" in result
    
    def test_simulate_with_tools(self):
        """Test simulation with AAI tools"""
        simulator = BrainSimulator()
        
        from app.engines.brainbuilder.schemas import AAIConfig, MemoryConfig, ReflectionConfig
        
        spec = BrainSpec(
            id="tool-brain",
            name="Tool Brain",
            adapter="aai_psm",
            format="composite",
            aai=AAIConfig(
                inner_manifest={"id": "base-model"},
                tools=["filesystem", "memory"],
                reflection=ReflectionConfig(enabled=True),
                memory=MemoryConfig()
            )
        )
        
        result = simulator.simulate(spec, num_prompts=3)
        
        assert result["status"] == "success"
        # Check that some results used tools
        # (in a real implementation)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
