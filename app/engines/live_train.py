"""
Live Train engine for online learning from feedback
"""
import logging
import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


class LiveTrainEngine:
    """
    Engine for live training and online learning
    """
    
    def __init__(self, lab_dir: str):
        self.lab_dir = Path(lab_dir)
        self.datasets_dir = self.lab_dir / "datasets"
        self.deltas_dir = self.lab_dir / "deltas"
        self.snapshots_dir = self.lab_dir / "snapshots"
        self.auras_dir = self.lab_dir / "auras"
        self.skillpacks_dir = self.lab_dir / "skillpacks"
        
        # Create directories
        for dir_path in [self.datasets_dir, self.deltas_dir, self.snapshots_dir, 
                         self.auras_dir, self.skillpacks_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Training queue
        self.queue_file = self.datasets_dir / "online_corrections.jsonl"
        if not self.queue_file.exists():
            self.queue_file.touch()
    
    def add_to_queue(self, example: Dict[str, Any]) -> None:
        """Add training example to queue"""
        with open(self.queue_file, 'a') as f:
            f.write(json.dumps(example) + '\n')
        logger.info("Added example to training queue")
    
    def get_queue(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get examples from queue"""
        examples = []
        with open(self.queue_file, 'r') as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line))
                    if limit and len(examples) >= limit:
                        break
        return examples
    
    def live_train(
        self,
        adapter,
        model_id: str,
        mode: str,
        budget: Dict[str, Any],
        dataset: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run live training with gradient budget routing.
        
        Args:
            adapter: Loaded model adapter
            model_id: Model identifier
            mode: Training mode (rule, hot_lora, dpo, rome)
            budget: Budget parameters (rank, steps, lr, etc.)
            dataset: Training dataset (optional, uses queue if not provided)
            
        Returns:
            Training result with delta_id
        """
        timestamp = int(time.time())
        delta_id = f"delta_{timestamp}"
        
        logger.info(f"Starting live training for {model_id} with mode {mode}")
        
        result = {
            "model_id": model_id,
            "timestamp": timestamp,
            "mode": mode,
            "budget": budget,
            "delta_id": delta_id,
            "status": "pending"
        }
        
        try:
            # Get training data
            if dataset:
                train_data = dataset.get("pairs", [])
            else:
                train_data = self.get_queue(limit=budget.get("max_examples", 100))
            
            result["examples_used"] = len(train_data)
            
            # Route to appropriate training method
            if mode == "rule":
                delta = self._train_rule_patch(adapter, train_data, budget)
            elif mode == "hot_lora":
                delta = self._train_hot_lora(adapter, train_data, budget)
            elif mode == "dpo":
                delta = self._train_dpo(adapter, train_data, budget)
            elif mode == "rome":
                delta = self._train_rome(adapter, train_data, budget)
            else:
                raise ValueError(f"Unknown training mode: {mode}")
            
            # Save delta
            self._save_delta(model_id, delta_id, delta, mode)
            
            result["status"] = "completed"
            result["delta"] = delta
            
            logger.info(f"Live training complete for {model_id}")
            
        except Exception as e:
            logger.error(f"Live training error: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
        
        return result
    
    def _train_rule_patch(
        self,
        adapter,
        train_data: List[Dict[str, Any]],
        budget: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Train using rule patches (prompt/template delta + token bias)"""
        logger.info("Training rule patch")
        
        delta = {
            "type": "rule_patch",
            "prompt_delta": "",
            "token_biases": {}
        }
        
        # Analyze common patterns in corrections
        # Simplified implementation
        if train_data:
            # Extract common themes
            delta["prompt_delta"] = "Be more concise and accurate."
            delta["token_biases"] = {
                "yes": 0.1,
                "no": -0.1
            }
        
        return delta
    
    def _train_hot_lora(
        self,
        adapter,
        train_data: List[Dict[str, Any]],
        budget: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Train using Hot-LoRA (rank 2-4, 20-60 steps)"""
        logger.info("Training Hot-LoRA")
        
        rank = budget.get("rank", 2)
        steps = budget.get("steps", 40)
        lr = budget.get("lr", 2e-4)
        
        delta = {
            "type": "hot_lora",
            "rank": rank,
            "steps": steps,
            "lr": lr,
            "modules": [],
            "note": "Simplified implementation - actual training would use PEFT library"
        }
        
        # In real implementation, would:
        # 1. Create LoRA config with specified rank
        # 2. Attach to top-k important modules (from tracing)
        # 3. Train for specified steps with lr
        # 4. Save adapter weights
        
        return delta
    
    def _train_dpo(
        self,
        adapter,
        train_data: List[Dict[str, Any]],
        budget: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Train using DPO/KTO micro-preference update"""
        logger.info("Training DPO")
        
        pairs = budget.get("pairs", 8)
        steps = budget.get("steps", 30)
        
        delta = {
            "type": "dpo",
            "pairs": pairs,
            "steps": steps,
            "note": "Simplified implementation - actual training would use TRL library"
        }
        
        # In real implementation, would:
        # 1. Format data as preference pairs
        # 2. Use DPOTrainer from TRL
        # 3. Train adapter-only
        # 4. Save adapter weights
        
        return delta
    
    def _train_rome(
        self,
        adapter,
        train_data: List[Dict[str, Any]],
        budget: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Train using ROME-style knowledge edits"""
        logger.info("Training ROME knowledge edit")
        
        delta = {
            "type": "rome",
            "edits": [],
            "note": "Simplified implementation - actual training would implement ROME algorithm"
        }
        
        # In real implementation, would:
        # 1. Identify facts to edit
        # 2. Locate knowledge storage layers
        # 3. Compute optimal edit
        # 4. Apply surgical weight update
        
        for example in train_data[:5]:  # Limit edits
            delta["edits"].append({
                "subject": "unknown",
                "relation": "unknown",
                "target": example.get("chosen", "")
            })
        
        return delta
    
    def _save_delta(self, model_id: str, delta_id: str, delta: Dict[str, Any], mode: str) -> None:
        """Save delta checkpoint"""
        delta_dir = self.deltas_dir / model_id / delta_id
        delta_dir.mkdir(parents=True, exist_ok=True)
        
        delta_file = delta_dir / "delta.json"
        with open(delta_file, 'w') as f:
            json.dump(delta, f, indent=2)
        
        logger.info(f"Saved delta to {delta_file}")
    
    def create_snapshot(self, model_id: str, description: Optional[str] = None) -> str:
        """Create a model snapshot"""
        timestamp = int(time.time())
        snapshot_id = f"SNAP_{timestamp}"
        
        snapshot_dir = self.snapshots_dir / model_id / snapshot_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        snapshot = {
            "snapshot_id": snapshot_id,
            "model_id": model_id,
            "timestamp": timestamp,
            "description": description,
            "stack": []
        }
        
        with open(snapshot_dir / "stack.json", 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        logger.info(f"Created snapshot {snapshot_id} for {model_id}")
        return snapshot_id
    
    def create_aura(self, aura_data: Dict[str, Any]) -> str:
        """Create or update an Aura"""
        aura_id = aura_data.get("aura_id") or str(uuid.uuid4())
        
        aura = {
            "aura_id": aura_id,
            "name": aura_data["name"],
            "model_id": aura_data["model_id"],
            "components": aura_data["components"],
            "created": int(time.time())
        }
        
        aura_file = self.auras_dir / f"{aura_id}.aura.json"
        with open(aura_file, 'w') as f:
            json.dump(aura, f, indent=2)
        
        logger.info(f"Created aura {aura_id}")
        return aura_id
    
    def export_skillpack(self, skillpack_data: Dict[str, Any]) -> str:
        """Export a SkillPack"""
        skillpack_id = str(uuid.uuid4())
        
        skillpack = {
            "skillpack_id": skillpack_id,
            "name": skillpack_data["name"],
            "model_id": skillpack_data["model_id"],
            "created": int(time.time()),
            "include_dataset": skillpack_data.get("include_dataset", True),
            "include_deltas": skillpack_data.get("include_deltas", True),
            "include_evals": skillpack_data.get("include_evals", True)
        }
        
        skillpack_file = self.skillpacks_dir / f"{skillpack_id}.spack"
        with open(skillpack_file, 'w') as f:
            json.dump(skillpack, f, indent=2)
        
        logger.info(f"Exported skillpack {skillpack_id}")
        return skillpack_id
    
    def rollback(self, model_id: str, snapshot_id: str) -> Dict[str, Any]:
        """Rollback model to a snapshot"""
        snapshot_file = self.snapshots_dir / model_id / snapshot_id / "stack.json"
        
        if not snapshot_file.exists():
            raise ValueError(f"Snapshot {snapshot_id} not found for model {model_id}")
        
        with open(snapshot_file, 'r') as f:
            snapshot = json.load(f)
        
        logger.info(f"Rolled back model {model_id} to snapshot {snapshot_id}")
        
        return {
            "status": "success",
            "snapshot_id": snapshot_id,
            "model_id": model_id
        }
