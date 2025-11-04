"""
InductionVM Scheduler - Executes IR operations
"""
import logging
from typing import Dict, Any
import numpy as np

from .ir import InductionIR, OpType
from .kernels_cpu import CPUKernels
from .kvcache import KVCache

logger = logging.getLogger(__name__)


class InductionScheduler:
    """
    Scheduler that executes InductionVM IR operations
    """
    
    def __init__(self, num_layers: int = 32, max_seq_len: int = 2048):
        """
        Initialize scheduler.
        
        Args:
            num_layers: Number of transformer layers
            max_seq_len: Maximum sequence length
        """
        self.kernels = CPUKernels()
        self.kvcache = KVCache(num_layers, max_seq_len)
        self.tensors: Dict[str, np.ndarray] = {}
    
    def execute(self, ir: InductionIR, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Execute an IR graph.
        
        Args:
            ir: InductionVM IR
            inputs: Input tensors
            
        Returns:
            Output tensors
        """
        # Load input tensors
        self.tensors.update(inputs)
        
        # Execute nodes in order
        for node in ir.nodes:
            self._execute_node(node)
        
        # Return all tensors (caller can extract what they need)
        return self.tensors
    
    def _execute_node(self, node):
        """Execute a single IR node"""
        try:
            if node.op == OpType.MATMUL:
                x = self.tensors[node.inputs[0]]
                w = self.tensors[node.inputs[1]]
                out = self.kernels.matmul(x, w)
                self.tensors[node.outputs[0]] = out
            
            elif node.op == OpType.ADD:
                a = self.tensors[node.inputs[0]]
                b = self.tensors[node.inputs[1]]
                out = self.kernels.add(a, b)
                self.tensors[node.outputs[0]] = out
            
            elif node.op == OpType.MUL:
                a = self.tensors[node.inputs[0]]
                b = self.tensors[node.inputs[1]]
                out = self.kernels.mul(a, b)
                self.tensors[node.outputs[0]] = out
            
            elif node.op == OpType.RMSNORM:
                x = self.tensors[node.inputs[0]]
                w = self.tensors[node.inputs[1]]
                eps = node.attrs.get("eps", 1e-6)
                out = self.kernels.rmsnorm(x, w, eps)
                self.tensors[node.outputs[0]] = out
            
            elif node.op == OpType.SOFTMAX:
                x = self.tensors[node.inputs[0]]
                dim = node.attrs.get("dim", -1)
                out = self.kernels.softmax(x, dim)
                self.tensors[node.outputs[0]] = out
            
            elif node.op == OpType.ROPE:
                q = self.tensors[node.inputs[0]]
                k = self.tensors[node.inputs[1]]
                pos = node.attrs["position"]
                q_out, k_out = self.kernels.rope_apply(q, k, pos)
                self.tensors[node.outputs[0]] = q_out
                self.tensors[node.outputs[1]] = k_out
            
            elif node.op == OpType.KV_WRITE:
                k = self.tensors[node.inputs[0]]
                v = self.tensors[node.inputs[1]]
                layer = node.attrs["layer"]
                self.kvcache.write(layer, k, v)
            
            elif node.op == OpType.KV_READ:
                layer = node.attrs["layer"]
                k, v = self.kvcache.read(layer)
                self.tensors[node.outputs[0]] = k
                self.tensors[node.outputs[1]] = v
            
            else:
                logger.warning(f"Unknown op type: {node.op}")
        
        except Exception as e:
            logger.error(f"Error executing node {node}: {e}")
            raise
