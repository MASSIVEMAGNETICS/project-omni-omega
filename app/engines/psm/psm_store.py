"""
PSM Store - Persistent State Memory with event log and context packing
"""
import sqlite3
import json
import time
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class PSMStore:
    """
    Persistent State Memory store with:
    - Append-only event log
    - SQLite graph for entities and relations
    - Context packing with vector similarity
    """
    
    def __init__(self, store_dir: str, vector_dim: int = 384):
        """
        Initialize PSM store.
        
        Args:
            store_dir: Directory for PSM data
            vector_dim: Dimension for entity embeddings
        """
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        
        self.vector_dim = vector_dim
        self.db_path = self.store_dir / "psm.db"
        self.events_path = self.store_dir / "events"
        self.events_path.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                attributes TEXT,
                embedding BLOB,
                created_at REAL,
                updated_at REAL
            )
        """)
        
        # Relations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relations (
                source_id TEXT,
                relation_type TEXT,
                target_id TEXT,
                weight REAL DEFAULT 1.0,
                created_at REAL,
                PRIMARY KEY (source_id, relation_type, target_id)
            )
        """)
        
        # Events table (index for quick lookup)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT,
                timestamp REAL,
                file_path TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def append_event(self, event: Dict[str, Any]) -> str:
        """
        Append an event to the event log.
        
        Args:
            event: Event dictionary
            
        Returns:
            Event ID
        """
        event_id = f"evt_{int(time.time() * 1000000)}"
        event["event_id"] = event_id
        event["timestamp"] = time.time()
        
        # Write to append-only file
        event_file = self.events_path / f"{event_id}.json"
        with open(event_file, "w") as f:
            json.dump(event, f, indent=2)
        
        # Index in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (event_id, event_type, timestamp, file_path) VALUES (?, ?, ?, ?)",
            (event_id, event.get("type", "unknown"), event["timestamp"], str(event_file))
        )
        conn.commit()
        conn.close()
        
        logger.info(f"Appended event {event_id} of type {event.get('type')}")
        return event_id
    
    def upsert_entity(self, entity_id: str, entity_type: str, 
                      attributes: Dict[str, Any], embedding: Optional[np.ndarray] = None):
        """
        Insert or update an entity.
        
        Args:
            entity_id: Unique entity identifier
            entity_type: Type of entity
            attributes: Entity attributes
            embedding: Optional vector embedding
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = time.time()
        embedding_blob = embedding.tobytes() if embedding is not None else None
        
        cursor.execute("""
            INSERT INTO entities (id, type, attributes, embedding, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                type = excluded.type,
                attributes = excluded.attributes,
                embedding = excluded.embedding,
                updated_at = excluded.updated_at
        """, (entity_id, entity_type, json.dumps(attributes), embedding_blob, now, now))
        
        conn.commit()
        conn.close()
    
    def add_relation(self, source_id: str, relation_type: str, target_id: str, weight: float = 1.0):
        """
        Add a relation between entities.
        
        Args:
            source_id: Source entity ID
            relation_type: Type of relation
            target_id: Target entity ID
            weight: Relation weight
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO relations (source_id, relation_type, target_id, weight, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (source_id, relation_type, target_id, weight, time.time()))
        
        conn.commit()
        conn.close()
    
    def get_context_pack(self, query: str, k: int = 6) -> Dict[str, Any]:
        """
        Get a context pack for a query.
        
        Args:
            query: Query string
            k: Number of entities to retrieve
            
        Returns:
            Context pack dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # For now, simple retrieval without vector search
        # In production, this would use FAISS or similar
        cursor.execute("""
            SELECT id, type, attributes, updated_at
            FROM entities
            ORDER BY updated_at DESC
            LIMIT ?
        """, (k,))
        
        entities = []
        for row in cursor.fetchall():
            entities.append({
                "id": row[0],
                "type": row[1],
                "attributes": json.loads(row[2]) if row[2] else {},
                "updated_at": row[3]
            })
        
        conn.close()
        
        return {
            "query": query,
            "entities": entities,
            "timestamp": time.time()
        }
    
    def create_snapshot(self, snapshot_id: str, description: str = "") -> Dict[str, Any]:
        """
        Create a snapshot of the current PSM state.
        
        Args:
            snapshot_id: Unique snapshot identifier
            description: Snapshot description
            
        Returns:
            Snapshot metadata
        """
        snapshot_dir = self.store_dir.parent / "psm" / "snapshots" / snapshot_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy database
        import shutil
        shutil.copy2(self.db_path, snapshot_dir / "psm.db")
        
        # Create metadata
        metadata = {
            "snapshot_id": snapshot_id,
            "description": description,
            "timestamp": time.time(),
            "path": str(snapshot_dir)
        }
        
        with open(snapshot_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Created PSM snapshot {snapshot_id}")
        return metadata
