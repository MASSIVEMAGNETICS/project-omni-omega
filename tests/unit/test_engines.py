"""
Unit tests for Lab engines
"""
import pytest
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.engines.diagnostics import DiagnosticsEngine
from app.engines.trace_target import TraceTargetEngine
from app.engines.live_train import LiveTrainEngine


class MockAdapter:
    """Mock adapter for testing"""
    def __init__(self):
        self.loaded = True


class TestDiagnosticsEngine:
    """Test DiagnosticsEngine"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = DiagnosticsEngine(lab_dir=self.temp_dir)
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        assert self.engine.lab_dir == Path(self.temp_dir)
        assert self.engine.reports_dir.exists()
    
    def test_run_diagnostics(self):
        """Test running diagnostics"""
        adapter = MockAdapter()
        
        report = self.engine.run_diagnostics(
            adapter,
            model_id="test-model",
            modes=["capabilities"],
            quick_mode=True
        )
        
        assert report["model_id"] == "test-model"
        assert "capabilities" in report["modes"]
        assert "results" in report
        assert "recommendations" in report


class TestTraceTargetEngine:
    """Test TraceTargetEngine"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = TraceTargetEngine(lab_dir=self.temp_dir)
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        assert self.engine.lab_dir == Path(self.temp_dir)
        assert self.engine.traces_dir.exists()
        assert self.engine.targets_dir.exists()
    
    def test_trace(self):
        """Test causal tracing"""
        adapter = MockAdapter()
        
        result = self.engine.trace(
            adapter,
            model_id="test-model",
            prompt="Test prompt",
            methods=["grad_act"]
        )
        
        assert result["model_id"] == "test-model"
        assert result["prompt"] == "Test prompt"
        assert "components" in result
        assert "ranked_components" in result
    
    def test_causal_test(self):
        """Test causal testing"""
        adapter = MockAdapter()
        
        targets = [
            {"type": "attn_head", "layer": 5, "head": 3}
        ]
        
        result = self.engine.causal_test(
            adapter,
            model_id="test-model",
            prompt="Test prompt",
            targets=targets,
            method="ablate"
        )
        
        assert result["model_id"] == "test-model"
        assert result["method"] == "ablate"
        assert "interventions" in result


class TestLiveTrainEngine:
    """Test LiveTrainEngine"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = LiveTrainEngine(lab_dir=self.temp_dir)
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        assert self.engine.lab_dir == Path(self.temp_dir)
        assert self.engine.datasets_dir.exists()
        assert self.engine.deltas_dir.exists()
        assert self.engine.snapshots_dir.exists()
        assert self.engine.auras_dir.exists()
        assert self.engine.skillpacks_dir.exists()
    
    def test_queue_operations(self):
        """Test training queue operations"""
        example = {
            "prompt": "Test prompt",
            "chosen": "Good response",
            "rejected": "Bad response"
        }
        
        self.engine.add_to_queue(example)
        queue = self.engine.get_queue()
        
        assert len(queue) >= 1
        assert queue[-1]["prompt"] == "Test prompt"
    
    def test_create_snapshot(self):
        """Test snapshot creation"""
        snapshot_id = self.engine.create_snapshot(
            model_id="test-model",
            description="Test snapshot"
        )
        
        assert snapshot_id.startswith("SNAP_")
        snapshot_file = self.engine.snapshots_dir / "test-model" / snapshot_id / "stack.json"
        assert snapshot_file.exists()
    
    def test_create_aura(self):
        """Test aura creation"""
        aura_data = {
            "name": "Test Aura",
            "model_id": "test-model",
            "components": {
                "prompt_delta": "Be helpful",
                "token_biases": {}
            }
        }
        
        aura_id = self.engine.create_aura(aura_data)
        assert aura_id
        
        aura_file = self.engine.auras_dir / f"{aura_id}.aura.json"
        assert aura_file.exists()
    
    def test_export_skillpack(self):
        """Test skillpack export"""
        skillpack_data = {
            "name": "Test SkillPack",
            "model_id": "test-model"
        }
        
        skillpack_id = self.engine.export_skillpack(skillpack_data)
        assert skillpack_id
        
        skillpack_file = self.engine.skillpacks_dir / f"{skillpack_id}.spack"
        assert skillpack_file.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
