"""
Example Victor custom backend runner

Implement this interface for custom model backends:
- init(config: dict) -> None
- infer(messages|prompt, params: dict) -> dict
- trace(prompt, desired, methods) -> dict (optional)
- causal_test(targets, ...) -> dict (optional)
- train_target(strategy, targets, params, dataset) -> dict (optional)
- diagnostics(modes) -> dict (optional)
- tokenize(text) -> dict (optional)
- cleanup() -> None (optional)
"""


def init(config):
    """Initialize the Victor backend"""
    print("Victor backend initialized")


def infer(prompt=None, messages=None, params=None):
    """
    Run inference.
    
    Returns:
        dict with 'stream' (generator) or 'text' (string) or 'usage' (dict)
    """
    if messages:
        text = messages[-1].get("content", "")
    else:
        text = prompt or ""
    
    # Simple echo response for demonstration
    response = f"Victor echo: {text[:50]}..."
    
    # Return as generator for streaming
    def generator():
        for char in response:
            yield char
    
    return {
        "stream": generator(),
        "text": None,
        "usage": {"prompt_tokens": 10, "completion_tokens": 10}
    }


def tokenize(text):
    """Tokenize text"""
    tokens = text.split()
    return {
        "tokens": tokens,
        "ids": list(range(len(tokens))),
        "count": len(tokens)
    }


def trace(prompt, desired=None, methods=None):
    """Run causal tracing (optional)"""
    return {
        "status": "not_implemented",
        "message": "Victor backend does not implement tracing"
    }


def causal_test(targets, prompt, method, baseline_prompt=None):
    """Run causal testing (optional)"""
    return {
        "status": "not_implemented",
        "message": "Victor backend does not implement causal testing"
    }


def train_target(strategy, targets, params, dataset):
    """Run targeted training (optional)"""
    return {
        "status": "not_implemented",
        "message": "Victor backend does not implement targeted training"
    }


def diagnostics(modes):
    """Run diagnostics (optional)"""
    return {
        "status": "not_implemented",
        "message": "Victor backend does not implement diagnostics"
    }


def cleanup():
    """Cleanup resources (optional)"""
    print("Victor backend cleanup")
