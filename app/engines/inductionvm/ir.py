"""
InductionVM Intermediate Representation
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class OpType(Enum):
    """Operation types in InductionVM IR"""
    MATMUL = "matmul"
    ADD = "add"
    MUL = "mul"
    RMSNORM = "rmsnorm"
    SOFTMAX = "softmax"
    ROPE = "rope"
    KV_READ = "kv_read"
    KV_WRITE = "kv_write"
    KV_COMPRESS = "kv_compress"


@dataclass
class IRNode:
    """IR node representing an operation"""
    op: OpType
    inputs: List[str]
    outputs: List[str]
    attrs: Dict[str, Any]
    
    def __repr__(self):
        return f"IRNode({self.op.value}, in={self.inputs}, out={self.outputs})"


class InductionIR:
    """
    InductionVM IR builder and optimizer
    """
    
    def __init__(self):
        self.nodes: List[IRNode] = []
        self.tensors: Dict[str, Dict[str, Any]] = {}
    
    def add_tensor(self, name: str, shape: List[int], dtype: str = "float32"):
        """Register a tensor in the IR"""
        self.tensors[name] = {
            "shape": shape,
            "dtype": dtype
        }
    
    def add_op(self, op: OpType, inputs: List[str], outputs: List[str], 
               attrs: Optional[Dict[str, Any]] = None):
        """Add an operation to the IR"""
        node = IRNode(
            op=op,
            inputs=inputs,
            outputs=outputs,
            attrs=attrs or {}
        )
        self.nodes.append(node)
        return node
    
    def matmul(self, x: str, w: str, out: str):
        """Matrix multiplication"""
        return self.add_op(OpType.MATMUL, [x, w], [out])
    
    def add(self, a: str, b: str, out: str):
        """Element-wise addition"""
        return self.add_op(OpType.ADD, [a, b], [out])
    
    def rmsnorm(self, x: str, w: str, out: str, eps: float = 1e-6):
        """RMS normalization"""
        return self.add_op(OpType.RMSNORM, [x, w], [out], {"eps": eps})
    
    def softmax(self, x: str, out: str, dim: int = -1):
        """Softmax operation"""
        return self.add_op(OpType.SOFTMAX, [x], [out], {"dim": dim})
    
    def rope(self, q: str, k: str, q_out: str, k_out: str, pos: int):
        """Rotary position embedding"""
        return self.add_op(OpType.ROPE, [q, k], [q_out, k_out], {"position": pos})
    
    def kv_write(self, k: str, v: str, layer: int):
        """Write to KV cache"""
        return self.add_op(OpType.KV_WRITE, [k, v], [], {"layer": layer})
    
    def kv_read(self, k_out: str, v_out: str, layer: int):
        """Read from KV cache"""
        return self.add_op(OpType.KV_READ, [], [k_out, v_out], {"layer": layer})
    
    def optimize(self):
        """Apply IR-level optimizations"""
        # Placeholder for optimization passes
        # Future: operator fusion, constant folding, etc.
        pass
    
    def __repr__(self):
        return f"InductionIR({len(self.nodes)} nodes, {len(self.tensors)} tensors)"
