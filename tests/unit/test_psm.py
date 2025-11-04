"""
Tests for PSM (Persistent State Memory) components
"""
import pytest
import tempfile
import time
import numpy as np
from pathlib import Path

from app.engines.psm import PSMStore


class TestPSMStore:
    """Test PSM Store"""
    
    def test_init(self):
        """Test PSM store initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = PSMStore(store_dir=tmpdir, vector_dim=384)
            
            assert store.vector_dim == 384
            assert store.db_path.exists()
    
    def test_append_event(self):
        """Test appending events"""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = PSMStore(store_dir=tmpdir)
            
            event = {
                "type": "test_event",
                "data": {"key": "value"}
            }
            
            event_id = store.append_event(event)
            
            assert event_id.startswith("evt_")
            
            # Check that event file was created
            event_files = list(store.events_path.glob("*.json"))
            assert len(event_files) == 1
    
    def test_upsert_entity(self):
        """Test upserting entities"""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = PSMStore(store_dir=tmpdir)
            
            # Insert entity
            store.upsert_entity(
                entity_id="entity_1",
                entity_type="user",
                attributes={"name": "Alice", "age": 30}
            )
            
            # Update entity
            store.upsert_entity(
                entity_id="entity_1",
                entity_type="user",
                attributes={"name": "Alice", "age": 31}
            )
            
            # In production, would check entity was updated
    
    def test_add_relation(self):
        """Test adding relations"""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = PSMStore(store_dir=tmpdir)
            
            # Create entities
            store.upsert_entity("entity_1", "user", {"name": "Alice"})
            store.upsert_entity("entity_2", "user", {"name": "Bob"})
            
            # Add relation
            store.add_relation("entity_1", "knows", "entity_2", weight=0.8)
            
            # In production, would verify relation was added
    
    def test_get_context_pack(self):
        """Test retrieving context pack"""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = PSMStore(store_dir=tmpdir)
            
            # Add some entities
            for i in range(5):
                store.upsert_entity(
                    entity_id=f"entity_{i}",
                    entity_type="concept",
                    attributes={"value": i}
                )
            
            # Get context pack
            context = store.get_context_pack("test query", k=3)
            
            assert "query" in context
            assert "entities" in context
            assert len(context["entities"]) <= 3
    
    def test_create_snapshot(self):
        """Test creating snapshots"""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = PSMStore(store_dir=tmpdir)
            
            # Add some data
            store.append_event({"type": "test"})
            store.upsert_entity("e1", "test", {"data": "value"})
            
            # Create snapshot
            snapshot = store.create_snapshot(
                snapshot_id="snap_1",
                description="Test snapshot"
            )
            
            assert snapshot["snapshot_id"] == "snap_1"
            assert "path" in snapshot


class TestPSMIntegration:
    """Integration tests for PSM"""
    
    def test_event_entity_workflow(self):
        """Test typical workflow: events + entities"""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = PSMStore(store_dir=tmpdir)
            
            # Log an inference event
            event = {
                "type": "inference",
                "data": {
                    "prompt": "What is AI?",
                    "model": "test-model"
                },
                "entities": ["concept_ai"]
            }
            event_id = store.append_event(event)
            
            # Create entity for the concept
            store.upsert_entity(
                entity_id="concept_ai",
                entity_type="concept",
                attributes={
                    "name": "Artificial Intelligence",
                    "description": "Machine intelligence"
                }
            )
            
            # Retrieve context for related query
            context = store.get_context_pack("AI", k=5)
            
            assert len(context["entities"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
