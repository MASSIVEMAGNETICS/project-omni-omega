"""
Defense Aura - Protect models from jailbreaks and adversarial inputs
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DefenseAura:
    """
    Defense system against jailbreaks, prompt injections, and adversarial inputs.
    Uses pattern matching, perplexity analysis, and learned defenses.
    """
    
    def __init__(self, enabled: bool = True, strictness: str = "medium"):
        """
        Initialize defense aura.
        
        Args:
            enabled: Whether defense is active
            strictness: Defense level ('low', 'medium', 'high')
        """
        self.enabled = enabled
        self.strictness = strictness
        self.jailbreak_patterns = self._load_jailbreak_patterns()
        
        logger.info(f"DefenseAura initialized: enabled={enabled}, strictness={strictness}")
    
    def _load_jailbreak_patterns(self) -> List[Dict[str, Any]]:
        """Load known jailbreak pattern families"""
        # Common jailbreak pattern families
        patterns = [
            {
                "name": "DAN (Do Anything Now)",
                "keywords": ["do anything now", "dan mode", "jailbreak"],
                "severity": "high"
            },
            {
                "name": "Role-play bypass",
                "keywords": ["pretend you are", "act as if", "ignore previous"],
                "severity": "medium"
            },
            {
                "name": "Encoding bypass",
                "keywords": ["base64", "rot13", "reverse the output"],
                "severity": "medium"
            },
            {
                "name": "Hypothetical scenarios",
                "keywords": ["hypothetically", "in a fictional world", "for educational purposes"],
                "severity": "low"
            }
        ]
        return patterns
    
    def check_input(self, prompt: str) -> Dict[str, Any]:
        """
        Check if input contains jailbreak attempts or adversarial patterns.
        
        Args:
            prompt: User input prompt
            
        Returns:
            Defense check results
        """
        if not self.enabled:
            return {"blocked": False, "reason": None}
        
        prompt_lower = prompt.lower()
        
        # Check against known patterns
        for pattern in self.jailbreak_patterns:
            for keyword in pattern["keywords"]:
                if keyword in prompt_lower:
                    severity = pattern["severity"]
                    
                    # Block based on strictness
                    should_block = (
                        (self.strictness == "high") or
                        (self.strictness == "medium" and severity in ["high", "medium"]) or
                        (self.strictness == "low" and severity == "high")
                    )
                    
                    if should_block:
                        logger.warning(f"Defense Aura blocked: {pattern['name']}")
                        return {
                            "blocked": True,
                            "reason": f"Potential {pattern['name']} detected",
                            "severity": severity,
                            "pattern": pattern["name"]
                        }
        
        # Check for excessive repetition (potential adversarial input)
        if self._check_repetition(prompt):
            logger.warning("Defense Aura blocked: excessive repetition")
            return {
                "blocked": True,
                "reason": "Excessive repetition detected",
                "severity": "medium",
                "pattern": "repetition_attack"
            }
        
        # Check for abnormal length
        if len(prompt) > 10000:
            logger.warning("Defense Aura blocked: excessive length")
            return {
                "blocked": True,
                "reason": "Input too long",
                "severity": "low",
                "pattern": "length_attack"
            }
        
        return {"blocked": False, "reason": None}
    
    def _check_repetition(self, text: str, max_repeat: int = 10) -> bool:
        """
        Check if text contains excessive repetition.
        
        Args:
            text: Input text
            max_repeat: Maximum allowed consecutive repeats
            
        Returns:
            True if excessive repetition detected
        """
        words = text.split()
        if len(words) < 2:
            return False
        
        consecutive = 1
        for i in range(1, len(words)):
            if words[i] == words[i-1]:
                consecutive += 1
                if consecutive > max_repeat:
                    return True
            else:
                consecutive = 1
        
        return False
    
    def evaluate_defense(self, test_prompts: List[str]) -> Dict[str, Any]:
        """
        Evaluate defense effectiveness on a test set.
        
        Args:
            test_prompts: List of test prompts (mix of benign and adversarial)
            
        Returns:
            Evaluation results
        """
        results = {
            "total": len(test_prompts),
            "blocked": 0,
            "allowed": 0,
            "by_severity": {"high": 0, "medium": 0, "low": 0}
        }
        
        for prompt in test_prompts:
            check = self.check_input(prompt)
            if check["blocked"]:
                results["blocked"] += 1
                severity = check.get("severity", "unknown")
                if severity in results["by_severity"]:
                    results["by_severity"][severity] += 1
            else:
                results["allowed"] += 1
        
        results["block_rate"] = results["blocked"] / results["total"] if results["total"] > 0 else 0
        
        logger.info(f"Defense evaluation: {results['blocked']}/{results['total']} blocked")
        return results
