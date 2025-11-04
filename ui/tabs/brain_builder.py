"""
Brain Builder UI Tab - Design and deploy custom AI brains
"""
import streamlit as st
import requests
import json
import yaml
from typing import Dict, Any

API_BASE = "http://localhost:8000/api"


def render_brain_builder():
    """Render the Brain Builder tab"""
    st.header("🧠 Brain Builder")
    st.markdown("Design and deploy custom AI brains with AAI/PSM, InductionVM, and EPA.")
    
    # Two columns: Blueprint editor on left, preview/results on right
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Brain Blueprint")
        
        # Format selector
        format_type = st.radio("Format", ["YAML", "JSON"], horizontal=True)
        
        # Default brain template
        default_yaml = """id: my-brain
name: My Custom Brain
description: A custom AI brain
adapter: aai_psm
format: composite

aai:
  inner_manifest:
    id: llama-7b
    adapter: llama_cpp
    format: gguf
    files:
      weights: ./models/llama-7b/weights.gguf
  tools:
    - filesystem
    - memory
  reflection:
    enabled: true
    budget_tokens: 128
  memory:
    vector_dim: 384
    k: 6

defense:
  enabled: true
  strictness: medium

epa_seeds:
  - reasoning
  - helpfulness

defaults:
  temperature: 0.3
  top_p: 0.9
  max_tokens: 256
  threads: 2
"""
        
        default_json = json.dumps({
            "id": "my-brain",
            "name": "My Custom Brain",
            "adapter": "aai_psm",
            "format": "composite",
            "defaults": {"temperature": 0.3, "top_p": 0.9}
        }, indent=2)
        
        # Blueprint editor
        if format_type == "YAML":
            blueprint_text = st.text_area(
                "Brain Specification (YAML)",
                value=default_yaml,
                height=400,
                key="brain_yaml"
            )
        else:
            blueprint_text = st.text_area(
                "Brain Specification (JSON)",
                value=default_json,
                height=400,
                key="brain_json"
            )
        
        # Action buttons
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            validate_btn = st.button("✓ Validate", use_container_width=True)
        
        with col_b:
            simulate_btn = st.button("▶ Simulate", use_container_width=True)
        
        with col_c:
            compile_btn = st.button("⚙ Compile", use_container_width=True)
    
    with col2:
        st.subheader("Preview & Results")
        
        # Parse blueprint
        try:
            if format_type == "YAML":
                spec = yaml.safe_load(blueprint_text)
            else:
                spec = json.loads(blueprint_text)
            
            # Show parsed spec
            with st.expander("Parsed Specification", expanded=False):
                st.json(spec)
            
            # Validation
            if validate_btn:
                with st.spinner("Validating..."):
                    try:
                        response = requests.post(
                            f"{API_BASE}/lab/brain/validate",
                            json={"spec": spec},
                            timeout=10
                        )
                        if response.status_code == 200:
                            result = response.json()
                            if result.get("valid"):
                                st.success("✓ Brain specification is valid!")
                                st.info(f"**Brain ID:** {result.get('brain_id')}")
                                st.info(f"**Adapter:** {result.get('adapter')}")
                            else:
                                st.error("❌ Invalid specification")
                                for issue in result.get("issues", []):
                                    st.warning(issue)
                        else:
                            st.error(f"Validation failed: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            # Simulation
            if simulate_btn:
                with st.spinner("Simulating with synthetic prompts..."):
                    try:
                        response = requests.post(
                            f"{API_BASE}/lab/brain/simulate",
                            json={"spec": spec, "num_prompts": 10},
                            timeout=30
                        )
                        if response.status_code == 200:
                            result = response.json()
                            st.success("✓ Simulation complete!")
                            
                            # Show analysis
                            analysis = result.get("analysis", {})
                            metrics_col1, metrics_col2 = st.columns(2)
                            with metrics_col1:
                                st.metric("Avg Tokens/Prompt", 
                                         f"{analysis.get('avg_tokens_per_prompt', 0):.1f}")
                                st.metric("Avg Latency (ms)", 
                                         f"{analysis.get('avg_latency_ms', 0):.0f}")
                            with metrics_col2:
                                st.metric("Success Rate", 
                                         f"{analysis.get('success_rate', 0)*100:.0f}%")
                                st.metric("Throughput", 
                                         f"{analysis.get('estimated_throughput', 0):.1f} req/s")
                            
                            # Show sample results
                            with st.expander("Sample Results"):
                                for i, res in enumerate(result.get("results", [])[:3]):
                                    st.write(f"**Prompt {i+1}:** {res['prompt']}")
                                    st.write(f"Response: {res['response']}")
                                    st.divider()
                        else:
                            st.error(f"Simulation failed: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            # Compilation
            if compile_btn:
                with st.spinner("Compiling brain artifacts..."):
                    try:
                        response = requests.post(
                            f"{API_BASE}/lab/brain/compile",
                            json={"spec": spec},
                            timeout=30
                        )
                        if response.status_code == 200:
                            result = response.json()
                            st.success("✓ Compilation complete!")
                            
                            st.write(f"**Brain ID:** {result.get('brain_id')}")
                            st.write(f"**Artifacts Generated:** {len(result.get('artifacts', []))}")
                            
                            # Show artifacts
                            for artifact in result.get("artifacts", []):
                                st.info(f"📦 {artifact['type'].upper()}: `{artifact['path']}`")
                            
                            # Mount button
                            if st.button("🚀 Mount Brain", key="mount_brain"):
                                try:
                                    mount_response = requests.post(
                                        f"{API_BASE}/lab/brain/mount",
                                        json={"brain_id": result.get('brain_id')},
                                        timeout=10
                                    )
                                    if mount_response.status_code == 200:
                                        st.success("Brain mounted successfully!")
                                    else:
                                        st.error(f"Mount failed: {mount_response.text}")
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        else:
                            st.error(f"Compilation failed: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        except yaml.YAMLError as e:
            st.error(f"YAML parsing error: {e}")
        except json.JSONDecodeError as e:
            st.error(f"JSON parsing error: {e}")
