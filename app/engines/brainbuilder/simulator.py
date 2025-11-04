"""
Brain Simulator - Test brain specs with synthetic prompts
"""
import logging
from typing import Dict, Any, List
import random

from .schemas import BrainSpec

logger = logging.getLogger(__name__)


class BrainSimulator:
    """
    Simulate brain behavior with synthetic prompts.
    Provides dry-run testing before deployment.
    """
    
    def __init__(self):
        logger.info("BrainSimulator initialized")
    
    def simulate(self, brain_spec: BrainSpec, 
                num_prompts: int = 10) -> Dict[str, Any]:
        """
        Simulate brain behavior with synthetic prompts.
        
        Args:
            brain_spec: Brain specification to test
            num_prompts: Number of test prompts to generate
            
        Returns:
            Simulation results
        """
        logger.info(f"Simulating brain: {brain_spec.id} with {num_prompts} prompts")
        
        # Generate synthetic prompts based on brain configuration
        prompts = self._generate_test_prompts(brain_spec, num_prompts)
        
        # Simulate responses
        results = []
        for prompt in prompts:
            result = self._simulate_response(brain_spec, prompt)
            results.append(result)
        
        # Analyze results
        analysis = self._analyze_results(results)
        
        return {
            "brain_id": brain_spec.id,
            "num_prompts": num_prompts,
            "results": results,
            "analysis": analysis,
            "status": "success"
        }
    
    def _generate_test_prompts(self, brain_spec: BrainSpec, 
                               num_prompts: int) -> List[str]:
        """
        Generate synthetic test prompts based on brain configuration.
        
        Args:
            brain_spec: Brain specification
            num_prompts: Number of prompts to generate
            
        Returns:
            List of test prompts
        """
        prompt_templates = [
            "What is {topic}?",
            "Explain {topic} in simple terms.",
            "How does {topic} work?",
            "Give me an example of {topic}.",
            "What are the benefits of {topic}?"
        ]
        
        topics = ["AI", "machine learning", "neural networks", 
                 "natural language processing", "computer vision"]
        
        prompts = []
        for _ in range(num_prompts):
            template = random.choice(prompt_templates)
            topic = random.choice(topics)
            prompts.append(template.format(topic=topic))
        
        return prompts
    
    def _simulate_response(self, brain_spec: BrainSpec, 
                          prompt: str) -> Dict[str, Any]:
        """
        Simulate brain response to a prompt.
        
        Args:
            brain_spec: Brain specification
            prompt: Test prompt
            
        Returns:
            Simulated response
        """
        # Placeholder simulation
        # In production, this could:
        # - Use a small model to generate responses
        # - Apply defense checks
        # - Simulate tool usage
        # - Estimate token usage and latency
        
        response = {
            "prompt": prompt,
            "response": "[Simulated response]",
            "tokens": random.randint(50, 200),
            "latency_ms": random.randint(100, 500)
        }
        
        # Check defense if configured
        if brain_spec.defense:
            response["defense_check"] = "passed"
        
        # Check tool usage if AAI is configured
        if brain_spec.aai and brain_spec.aai.tools:
            response["tools_used"] = random.choice([[], ["filesystem"], ["memory"]])
        
        return response
    
    def _analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze simulation results.
        
        Args:
            results: List of simulation results
            
        Returns:
            Analysis summary
        """
        total_tokens = sum(r.get("tokens", 0) for r in results)
        avg_latency = sum(r.get("latency_ms", 0) for r in results) / len(results)
        
        analysis = {
            "total_prompts": len(results),
            "total_tokens": total_tokens,
            "avg_tokens_per_prompt": total_tokens / len(results),
            "avg_latency_ms": avg_latency,
            "estimated_throughput": 1000 / avg_latency if avg_latency > 0 else 0,
            "success_rate": 1.0  # Placeholder
        }
        
        return analysis
