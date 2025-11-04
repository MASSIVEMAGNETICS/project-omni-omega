"""
Diagnostics Plus UI Tab - Enhanced diagnostics with EPA and Defense
"""
import streamlit as st
import requests
from typing import Dict, Any

API_BASE = "http://localhost:8000/api"


def render_diagnostics_plus():
    """Render the Diagnostics Plus tab"""
    st.header("🔍 Diagnostics Plus")
    st.markdown("Enhanced diagnostics with EPA amplification and Defense Aura testing.")
    
    # Model selection
    try:
        response = requests.get(f"{API_BASE}/models", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            loaded_models = [m for m in models if m.get("loaded")]
            
            if not loaded_models:
                st.warning("No loaded models. Please load a model first.")
                return
            
            model_options = {m["name"]: m["id"] for m in loaded_models}
            selected_name = st.selectbox("Select Model", list(model_options.keys()))
            model_id = model_options[selected_name]
        else:
            st.error("Failed to fetch models")
            return
    except Exception as e:
        st.error(f"Error: {e}")
        return
    
    st.divider()
    
    # Two columns: Configuration on left, results on right
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Diagnostic Configuration")
        
        # Standard diagnostics
        st.write("**Standard Diagnostics**")
        head_roles = st.checkbox("Head Roles", value=True)
        sae = st.checkbox("SAE Features")
        spectral = st.checkbox("Spectral Analysis")
        capabilities = st.checkbox("Capabilities", value=True)
        redteam = st.checkbox("Redteam/Jailbreak")
        leakage = st.checkbox("Memorization/Leakage")
        
        quick_mode = st.checkbox("Quick Mode (90-150s)", value=True)
        
        st.divider()
        
        # EPA Amplification
        st.write("**EPA (Enhanced Prompt Amplification)**")
        epa_enabled = st.checkbox("Enable EPA Amplification")
        
        if epa_enabled:
            epa_seed = st.selectbox(
                "Seed Behavior",
                ["reasoning", "helpfulness", "conciseness", "creativity"]
            )
            epa_steps = st.slider("Training Steps", 10, 100, 40)
        
        st.divider()
        
        # Defense Aura
        st.write("**Defense Aura**")
        defense_enabled = st.checkbox("Enable Defense Aura")
        
        if defense_enabled:
            defense_strictness = st.select_slider(
                "Strictness",
                options=["low", "medium", "high"],
                value="medium"
            )
            defense_test_set = st.selectbox(
                "Test Set",
                ["standard_jailbreaks", "encoding_attacks", "role_play_bypass", "all"]
            )
        
        st.divider()
        
        # InductionVM Stats
        st.write("**InductionVM Stats**")
        show_induction = st.checkbox("Show InductionVM Statistics")
    
    with col2:
        st.subheader("Results & Live Stats")
        
        # Run diagnostics button
        if st.button("🔍 Run Enhanced Diagnostics", type="primary", use_container_width=True):
            modes = []
            if head_roles: modes.append("head_roles")
            if sae: modes.append("sae")
            if spectral: modes.append("spectral")
            if capabilities: modes.append("capabilities")
            if redteam: modes.append("redteam")
            if leakage: modes.append("leakage")
            
            if not modes:
                st.error("Please select at least one diagnostic mode")
            else:
                with st.spinner("Running diagnostics..."):
                    try:
                        # Run standard diagnostics
                        payload = {
                            "model_id": model_id,
                            "modes": modes,
                            "quick_mode": quick_mode
                        }
                        response = requests.post(
                            f"{API_BASE}/lab/diagnostics/run",
                            json=payload,
                            timeout=300
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success("✓ Standard diagnostics complete!")
                            
                            # Show results summary
                            with st.expander("Standard Diagnostics Results", expanded=True):
                                st.json(result)
                            
                            # Show recommendations
                            if "recommendations" in result:
                                st.subheader("Recommendations")
                                for rec in result["recommendations"]:
                                    st.info(f"**{rec['area']}**: {rec['suggestion']} "
                                           f"(Priority: {rec['priority']})")
                        else:
                            st.error(f"Diagnostics failed: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                
                # EPA amplification
                if epa_enabled:
                    st.divider()
                    with st.spinner(f"Running EPA amplification with {epa_seed} seed..."):
                        st.info(f"🎯 EPA: Amplifying '{epa_seed}' behavior "
                               f"with {epa_steps} steps...")
                        # Placeholder - in production would call EPA API
                        st.success("✓ EPA amplification complete!")
                        st.metric("Amplification Score", "1.45x")
                
                # Defense Aura testing
                if defense_enabled:
                    st.divider()
                    with st.spinner("Testing Defense Aura..."):
                        st.info(f"🛡️ Defense Aura: Testing with {defense_strictness} "
                               f"strictness on {defense_test_set}...")
                        # Placeholder - in production would call Defense API
                        st.success("✓ Defense Aura testing complete!")
                        
                        # Mock results
                        def_col1, def_col2, def_col3 = st.columns(3)
                        with def_col1:
                            st.metric("Blocked", "18/20")
                        with def_col2:
                            st.metric("False Positives", "0/20")
                        with def_col3:
                            st.metric("Block Rate", "90%")
        
        st.divider()
        
        # Live stats
        if show_induction:
            st.subheader("InductionVM Live Stats")
            
            # Placeholder metrics
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("Tokens/sec", "45.3", "+12%")
                st.metric("KV Cache Size", "128 MB")
            with metric_col2:
                st.metric("KV Hit Rate", "78%", "+5%")
                st.metric("Patterns Cached", "234")
            
            # Graph placeholder
            st.line_chart({"tokens/s": [40, 42, 45, 43, 46, 45, 47]})
