"""
OmniLoader Streamlit UI - Dual-tab interface (Chat | Lab)
Neon/grid GUI theme applied. Footer credit added.
"""
import streamlit as st
import requests
import json
from typing import Dict, Any, List
import time

# API Configuration
API_BASE = "http://localhost:8000/api"

# Page config
st.set_page_config(
    page_title="OmniLoader",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Neon/Grid GUI Theme
st.markdown("""
<style>
    /* Main app background - pure black with neon grid */
    .stApp {
        max-width: 100%;
        background-color: #000000;
        color: #00ff41;
        background-image: 
            linear-gradient(rgba(157, 0, 255, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(157, 0, 255, 0.1) 1px, transparent 1px);
        background-size: 50px 50px;
        background-position: -1px -1px;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 2px solid #ff00ff;
    }
    
    [data-testid="stSidebar"] * {
        color: #00ff41 !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ff00ff !important;
        text-shadow: 0 0 10px #ff00ff, 0 0 20px #ff00ff;
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid;
    }
    .user-message {
        background-color: #0a0a14;
        border-color: #00ff41;
        color: #00ff41;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
    }
    .assistant-message {
        background-color: #140a14;
        border-color: #ff00ff;
        color: #ff00ff;
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.3);
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #1a001a;
        color: #ff00ff;
        border: 2px solid #ff00ff;
        border-radius: 5px;
        text-shadow: 0 0 5px #ff00ff;
        box-shadow: 0 0 10px rgba(255, 0, 255, 0.5);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #2a002a;
        box-shadow: 0 0 20px rgba(255, 0, 255, 0.8);
        transform: scale(1.02);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background-color: #0a0a0a;
        color: #00ff41;
        border: 2px solid #9d00ff;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(157, 0, 255, 0.3);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #ff00ff;
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.5);
    }
    
    /* Select boxes */
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div {
        background-color: #0a0a0a;
        color: #00ff41;
        border: 2px solid #9d00ff;
        box-shadow: 0 0 10px rgba(157, 0, 255, 0.3);
    }
    
    /* Sliders */
    .stSlider > div > div > div > div {
        background-color: #9d00ff;
    }
    
    .stSlider > div > div > div > div > div {
        background-color: #ff00ff;
        box-shadow: 0 0 10px rgba(255, 0, 255, 0.7);
    }
    
    /* Checkboxes and radio buttons */
    .stCheckbox > label > div,
    .stRadio > label > div {
        color: #00ff41 !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #ff00ff !important;
        text-shadow: 0 0 10px #ff00ff;
    }
    
    [data-testid="stMetricLabel"] {
        color: #00ff41 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #0a0a0a;
        border-bottom: 2px solid #9d00ff;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #00ff41;
        background-color: transparent;
        border: 1px solid #9d00ff;
        border-radius: 5px 5px 0 0;
        margin-right: 5px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #1a001a;
        box-shadow: 0 0 10px rgba(157, 0, 255, 0.5);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2a002a;
        color: #ff00ff !important;
        border-color: #ff00ff;
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.6);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #0a0a0a;
        color: #ff00ff !important;
        border: 1px solid #9d00ff;
        border-radius: 5px;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #1a001a;
        box-shadow: 0 0 10px rgba(157, 0, 255, 0.5);
    }
    
    /* Dividers */
    hr {
        border-color: #9d00ff;
        box-shadow: 0 0 5px rgba(157, 0, 255, 0.5);
    }
    
    /* Code blocks */
    code {
        background-color: #0a0a0a;
        color: #00ff41;
        border: 1px solid #9d00ff;
        padding: 2px 5px;
        border-radius: 3px;
    }
    
    pre {
        background-color: #0a0a0a;
        border: 2px solid #9d00ff;
        box-shadow: 0 0 10px rgba(157, 0, 255, 0.3);
    }
    
    /* Success, warning, error messages */
    .stSuccess {
        background-color: #001a0a;
        color: #00ff41;
        border-left: 5px solid #00ff41;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
    }
    
    .stWarning {
        background-color: #1a1a00;
        color: #ffff00;
        border-left: 5px solid #ffff00;
        box-shadow: 0 0 15px rgba(255, 255, 0, 0.3);
    }
    
    .stError {
        background-color: #1a0000;
        color: #ff0066;
        border-left: 5px solid #ff0066;
        box-shadow: 0 0 15px rgba(255, 0, 102, 0.3);
    }
    
    .stInfo {
        background-color: #00001a;
        color: #00ffff;
        border-left: 5px solid #00ffff;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #ff00ff !important;
        border-right-color: #9d00ff !important;
        border-bottom-color: #ff00ff !important;
        border-left-color: #9d00ff !important;
    }
    
    /* General text */
    p, span, div, label {
        color: #00ff41;
    }
    
    /* Links */
    a {
        color: #ff00ff;
        text-shadow: 0 0 5px #ff00ff;
    }
    
    a:hover {
        color: #00ffff;
        text-shadow: 0 0 10px #00ffff;
    }
    
    /* Dataframe/table styling */
    .dataframe {
        background-color: #0a0a0a;
        color: #00ff41;
        border: 2px solid #9d00ff;
    }
    
    .dataframe th {
        background-color: #1a001a;
        color: #ff00ff;
        border: 1px solid #9d00ff;
    }
    
    .dataframe td {
        border: 1px solid #9d00ff;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
        border: 1px solid #9d00ff;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #ff00ff, #9d00ff);
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(255, 0, 255, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #ff00ff, #ff00ff);
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.8);
    }
    
    /* Footer styling */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: rgba(10, 10, 10, 0.9);
        border-top: 1px solid #9d00ff;
        padding: 10px 20px;
        text-align: center;
        color: #00ff41;
        font-size: 12px;
        z-index: 999;
        box-shadow: 0 -2px 10px rgba(157, 0, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = None
if "models" not in st.session_state:
    st.session_state.models = []


def fetch_models() -> List[Dict[str, Any]]:
    """Fetch available models from API"""
    try:
        response = requests.get(f"{API_BASE}/models", timeout=5)
        if response.status_code == 200:
            return response.json().get("models", [])
    except Exception as e:
        st.error(f"Failed to fetch models: {e}")
    return []


def load_model(model_id: str) -> bool:
    """Load a model"""
    try:
        response = requests.post(f"{API_BASE}/models/{model_id}/load", timeout=30)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return False


def generate_stream(model_id: str, prompt: str, params: Dict[str, Any]):
    """Generate text with streaming"""
    try:
        payload = {
            "model_id": model_id,
            "prompt": prompt,
            "stream": True,
            **params
        }
        
        response = requests.post(
            f"{API_BASE}/generate",
            json=payload,
            stream=True,
            timeout=300
        )
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data: "):
                    data = line_str[6:]
                    if data == "[DONE]":
                        break
                    yield data
                    
    except Exception as e:
        yield f"\n[Error: {str(e)}]"


def render_chat_tab():
    """Render the Chat tab"""
    st.title("💬 Chat")
    
    # Sidebar for model selection and params
    with st.sidebar:
        st.header("Model Settings")
        
        # Refresh models
        if st.button("🔄 Refresh Models"):
            st.session_state.models = fetch_models()
        
        # Model selector
        if not st.session_state.models:
            st.session_state.models = fetch_models()
        
        if st.session_state.models:
            model_options = {m["name"]: m["id"] for m in st.session_state.models}
            selected_name = st.selectbox(
                "Select Model",
                options=list(model_options.keys())
            )
            selected_id = model_options.get(selected_name)
            
            if selected_id != st.session_state.selected_model:
                st.session_state.selected_model = selected_id
            
            # Check if loaded
            selected_model = next((m for m in st.session_state.models if m["id"] == selected_id), None)
            if selected_model:
                if selected_model.get("loaded"):
                    st.success("✓ Model loaded")
                else:
                    if st.button("Load Model"):
                        with st.spinner("Loading model..."):
                            if load_model(selected_id):
                                st.success("Model loaded!")
                                st.rerun()
                            else:
                                st.error("Failed to load model")
        else:
            st.warning("No models found. Add models to the ./models directory.")
        
        st.divider()
        
        # Generation parameters
        st.subheader("Generation Parameters")
        temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
        top_p = st.slider("Top P", 0.0, 1.0, 0.9, 0.05)
        max_tokens = st.number_input("Max Tokens", 1, 2048, 256, 1)
        
        st.divider()
        
        # System prompt
        st.subheader("System Prompt")
        system_prompt = st.text_area(
            "System Prompt",
            value="You are a helpful AI assistant.",
            height=100
        )
        
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Display chat messages
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                st.markdown(f'<div class="chat-message user-message"><b>You:</b> {content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message"><b>Assistant:</b> {content}</div>', unsafe_allow_html=True)
        
        # Chat input
        if prompt := st.chat_input("Type your message..."):
            if not st.session_state.selected_model:
                st.error("Please select and load a model first")
            else:
                # Add user message
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Generate response
                params = {
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens
                }
                
                # Display user message
                st.markdown(f'<div class="chat-message user-message"><b>You:</b> {prompt}</div>', unsafe_allow_html=True)
                
                # Stream assistant response
                response_placeholder = st.empty()
                full_response = ""
                
                for token in generate_stream(st.session_state.selected_model, prompt, params):
                    full_response += token
                    response_placeholder.markdown(f'<div class="chat-message assistant-message"><b>Assistant:</b> {full_response}</div>', unsafe_allow_html=True)
                
                # Add to history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    with col2:
        st.subheader("Stats & Tools")
        if st.session_state.selected_model:
            st.metric("Model", st.session_state.selected_model)
            st.metric("Messages", len(st.session_state.messages))
        
        st.divider()
        st.caption("Quick Actions")
        if st.button("📋 Copy Last Response"):
            if st.session_state.messages:
                last_msg = st.session_state.messages[-1]["content"]
                st.code(last_msg)


def render_lab_tab():
    """Render the Lab tab with subtabs"""
    st.title("🔬 Lab")
    
    # Setup import path for tabs once
    import sys
    import os
    ui_dir = os.path.dirname(__file__)
    if ui_dir not in sys.path:
        sys.path.insert(0, ui_dir)
    
    # Lab subtabs
    lab_tabs = st.tabs([
        "Model Manager",
        "Diagnostics",
        "Diagnostics Plus",
        "Brain Builder",
        "Induction Settings",
        "Trace & Target",
        "Live Train",
        "Tokenizer",
        "Artifacts"
    ])
    
    with lab_tabs[0]:
        render_model_manager()
    
    with lab_tabs[1]:
        render_diagnostics()
    
    with lab_tabs[2]:
        # Import and render Diagnostics Plus
        try:
            from tabs.diagnostics_plus import render_diagnostics_plus
            render_diagnostics_plus()
        except ImportError as e:
            st.error(f"Diagnostics Plus tab not available: {e}")
    
    with lab_tabs[3]:
        # Import and render Brain Builder
        try:
            from tabs.brain_builder import render_brain_builder
            render_brain_builder()
        except ImportError as e:
            st.error(f"Brain Builder tab not available: {e}")
    
    with lab_tabs[4]:
        # Import and render Induction Settings
        try:
            from tabs.settings_induction import render_induction_settings
            render_induction_settings()
        except ImportError as e:
            st.error(f"Induction Settings tab not available: {e}")
    
    with lab_tabs[5]:
        render_trace_target()
    
    with lab_tabs[6]:
        render_live_train()
    
    with lab_tabs[7]:
        render_tokenizer()
    
    with lab_tabs[8]:
        render_artifacts()


def render_model_manager():
    """Render Model Manager subtab"""
    st.subheader("📦 Model Manager")
    
    models = fetch_models()
    
    if models:
        for model in models:
            with st.expander(f"{model['name']} ({model['id']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Adapter:** {model['adapter']}")
                    st.write(f"**Context:** {model['context_length']}")
                
                with col2:
                    status = "✅ Loaded" if model['loaded'] else "⭕ Not Loaded"
                    st.write(f"**Status:** {status}")
                
                with col3:
                    if model['loaded']:
                        if st.button(f"Unload", key=f"unload_{model['id']}"):
                            try:
                                requests.post(f"{API_BASE}/models/{model['id']}/unload")
                                st.success("Model unloaded")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    else:
                        if st.button(f"Load", key=f"load_{model['id']}"):
                            with st.spinner("Loading..."):
                                if load_model(model['id']):
                                    st.success("Model loaded!")
                                    st.rerun()
    else:
        st.info("No models registered. Add model manifests to ./models directory and restart.")


def render_diagnostics():
    """Render Diagnostics subtab"""
    st.subheader("🔍 Diagnostics")
    
    models = fetch_models()
    if not models:
        st.warning("No models available")
        return
    
    model_options = {m["name"]: m["id"] for m in models if m.get("loaded")}
    
    if not model_options:
        st.warning("No loaded models. Please load a model first.")
        return
    
    model_name = st.selectbox("Select Model", list(model_options.keys()))
    model_id = model_options[model_name]
    
    st.write("Select diagnostic modes to run:")
    
    col1, col2 = st.columns(2)
    with col1:
        head_roles = st.checkbox("Head Roles", value=True)
        sae = st.checkbox("SAE Features")
        spectral = st.checkbox("Spectral Analysis")
    
    with col2:
        capabilities = st.checkbox("Capabilities", value=True)
        redteam = st.checkbox("Redteam/Jailbreak")
        leakage = st.checkbox("Memorization/Leakage")
    
    quick_mode = st.checkbox("Quick Mode (90-150s)", value=True)
    
    if st.button("🔍 Run Diagnostics"):
        modes = []
        if head_roles: modes.append("head_roles")
        if sae: modes.append("sae")
        if spectral: modes.append("spectral")
        if capabilities: modes.append("capabilities")
        if redteam: modes.append("redteam")
        if leakage: modes.append("leakage")
        
        if not modes:
            st.error("Please select at least one diagnostic mode")
            return
        
        with st.spinner("Running diagnostics..."):
            try:
                payload = {
                    "model_id": model_id,
                    "modes": modes,
                    "quick_mode": quick_mode
                }
                response = requests.post(f"{API_BASE}/lab/diagnostics/run", json=payload, timeout=300)
                
                if response.status_code == 200:
                    report = response.json()
                    st.success("✅ Diagnostics complete!")
                    
                    st.json(report)
                    
                    if "recommendations" in report:
                        st.subheader("Recommendations")
                        for rec in report["recommendations"]:
                            st.info(f"**{rec['area']}**: {rec['suggestion']} (Priority: {rec['priority']})")
                else:
                    st.error(f"Diagnostics failed: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")


def render_trace_target():
    """Render Trace & Target subtab"""
    st.subheader("🎯 Trace & Target")
    
    models = fetch_models()
    model_options = {m["name"]: m["id"] for m in models if m.get("loaded")}
    
    if not model_options:
        st.warning("No loaded models available")
        return
    
    tab1, tab2 = st.tabs(["Trace", "Causal Test"])
    
    with tab1:
        st.write("**Causal Tracing**")
        
        model_name = st.selectbox("Model", list(model_options.keys()), key="trace_model")
        model_id = model_options[model_name]
        
        prompt = st.text_area("Prompt", "The capital of France is")
        desired = st.text_input("Desired Output (optional)", "Paris")
        
        methods = st.multiselect("Methods", ["grad_act", "ig", "rollout"], default=["grad_act"])
        resolution = st.multiselect("Resolution", ["layers", "heads", "mlp"], default=["layers"])
        
        if st.button("🎯 Run Trace"):
            with st.spinner("Tracing..."):
                try:
                    payload = {
                        "model_id": model_id,
                        "prompt": prompt,
                        "desired": desired if desired else None,
                        "methods": methods,
                        "resolution": resolution
                    }
                    response = requests.post(f"{API_BASE}/lab/trace", json=payload, timeout=60)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Trace complete!")
                        st.json(result)
                    else:
                        st.error(f"Trace failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab2:
        st.write("**Causal Intervention Test**")
        st.info("Configure and test causal interventions on specific components")


def render_live_train():
    """Render Live Train subtab"""
    st.subheader("🎓 Live Train")
    
    tab1, tab2, tab3 = st.tabs(["Queue", "Train", "Snapshots"])
    
    with tab1:
        st.write("**Training Queue**")
        
        with st.form("add_example"):
            prompt = st.text_area("Prompt")
            chosen = st.text_area("Chosen Response")
            rejected = st.text_area("Rejected Response (optional)")
            
            if st.form_submit_button("Add to Queue"):
                try:
                    payload = {
                        "prompt": prompt,
                        "chosen": chosen,
                        "rejected": rejected if rejected else None
                    }
                    response = requests.post(f"{API_BASE}/lab/queue", json=payload)
                    if response.status_code == 200:
                        st.success("Added to queue!")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if st.button("View Queue"):
            try:
                response = requests.get(f"{API_BASE}/lab/queue")
                if response.status_code == 200:
                    data = response.json()
                    st.write(f"Queue size: {data['count']}")
                    st.json(data['examples'][:10])  # Show first 10
            except Exception as e:
                st.error(f"Error: {e}")
    
    with tab2:
        st.write("**Live Training**")
        
        models = fetch_models()
        model_options = {m["name"]: m["id"] for m in models if m.get("loaded")}
        
        if model_options:
            model_name = st.selectbox("Model", list(model_options.keys()), key="train_model")
            model_id = model_options[model_name]
            
            mode = st.selectbox("Training Mode", ["rule", "hot_lora", "dpo", "rome"])
            
            st.write("**Budget Parameters**")
            col1, col2 = st.columns(2)
            with col1:
                rank = st.number_input("LoRA Rank", 1, 8, 2)
                steps = st.number_input("Training Steps", 10, 100, 40)
            with col2:
                lr = st.number_input("Learning Rate", 0.0, 0.01, 0.0002, format="%.4f")
                max_examples = st.number_input("Max Examples", 1, 100, 20)
            
            if st.button("🎓 Start Training"):
                with st.spinner("Training..."):
                    try:
                        payload = {
                            "model_id": model_id,
                            "mode": mode,
                            "budget": {
                                "rank": rank,
                                "steps": steps,
                                "lr": lr,
                                "max_examples": max_examples
                            }
                        }
                        response = requests.post(f"{API_BASE}/lab/train/live", json=payload, timeout=300)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success("✅ Training complete!")
                            st.json(result)
                        else:
                            st.error(f"Training failed: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    with tab3:
        st.write("**Snapshots**")
        
        models = fetch_models()
        model_options = {m["name"]: m["id"] for m in models if m.get("loaded")}
        
        if model_options:
            model_name = st.selectbox("Model", list(model_options.keys()), key="snapshot_model")
            model_id = model_options[model_name]
            
            description = st.text_input("Description")
            
            if st.button("📸 Create Snapshot"):
                try:
                    payload = {
                        "model_id": model_id,
                        "description": description
                    }
                    response = requests.post(f"{API_BASE}/lab/snapshot", json=payload)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Snapshot created: {result['snapshot_id']}")
                except Exception as e:
                    st.error(f"Error: {e}")


def render_tokenizer():
    """Render Tokenizer subtab"""
    st.subheader("🔤 Tokenizer")
    
    models = fetch_models()
    model_options = {m["name"]: m["id"] for m in models if m.get("loaded")}
    
    if not model_options:
        st.warning("No loaded models available")
        return
    
    model_name = st.selectbox("Model", list(model_options.keys()), key="tokenizer_model")
    model_id = model_options[model_name]
    
    text = st.text_area("Text to tokenize", "Hello, world!")
    
    if st.button("Tokenize"):
        try:
            response = requests.post(
                f"{API_BASE}/models/{model_id}/tokenize",
                params={"text": text}
            )
            if response.status_code == 200:
                result = response.json()
                st.write(f"**Token count:** {result['count']}")
                if result.get('tokens'):
                    st.write("**Tokens:**")
                    st.json(result['tokens'])
        except Exception as e:
            st.error(f"Error: {e}")


def render_artifacts():
    """Render Artifacts subtab"""
    st.subheader("📦 Artifacts")
    
    tab1, tab2 = st.tabs(["Auras", "SkillPacks"])
    
    with tab1:
        st.write("**Auras - Modular Behavior Overlays**")
        
        with st.form("create_aura"):
            name = st.text_input("Aura Name")
            
            models = fetch_models()
            if models:
                model_options = {m["name"]: m["id"] for m in models}
                model_name = st.selectbox("Model", list(model_options.keys()))
                model_id = model_options[model_name]
                
                components_json = st.text_area("Components (JSON)", "{}")
                
                if st.form_submit_button("Create Aura"):
                    try:
                        components = json.loads(components_json)
                        payload = {
                            "name": name,
                            "model_id": model_id,
                            "components": components
                        }
                        response = requests.post(f"{API_BASE}/lab/auras/create", json=payload)
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"Aura created: {result['aura_id']}")
                    except json.JSONDecodeError:
                        st.error("Invalid JSON")
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    with tab2:
        st.write("**SkillPacks - Portable Training Bundles**")
        
        with st.form("export_skillpack"):
            name = st.text_input("SkillPack Name")
            
            models = fetch_models()
            if models:
                model_options = {m["name"]: m["id"] for m in models}
                model_name = st.selectbox("Model", list(model_options.keys()), key="skillpack_model")
                model_id = model_options[model_name]
                
                include_dataset = st.checkbox("Include Dataset", value=True)
                include_deltas = st.checkbox("Include Deltas", value=True)
                include_evals = st.checkbox("Include Evaluations", value=True)
                
                if st.form_submit_button("Export SkillPack"):
                    try:
                        payload = {
                            "name": name,
                            "model_id": model_id,
                            "include_dataset": include_dataset,
                            "include_deltas": include_deltas,
                            "include_evals": include_evals
                        }
                        response = requests.post(f"{API_BASE}/lab/skillpack/export", json=payload)
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"SkillPack exported: {result['skillpack_id']}")
                    except Exception as e:
                        st.error(f"Error: {e}")


# Check if this is the first run or no models are loaded
def check_onboarding_needed() -> bool:
    """Check if onboarding should be shown"""
    if "onboarding_complete" not in st.session_state:
        st.session_state.onboarding_complete = False
    
    # Check if there are any models
    try:
        response = requests.get(f"{API_BASE}/models", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            # If there are loaded models, skip onboarding
            if any(m.get("loaded") for m in models):
                return False
    except:
        pass
    
    return not st.session_state.onboarding_complete


def render_welcome_screen():
    """Render the welcome/onboarding screen"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #ff00ff; text-shadow: 0 0 20px #ff00ff, 0 0 40px #ff00ff; font-size: 3rem;">
            🤖 Welcome to OmniLoader Studio
        </h1>
        <p style="color: #00ff41; font-size: 1.2rem; margin-top: 1rem;">
            Production-grade local-first AI model manager
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; border: 1px solid #9d00ff; border-radius: 10px; background: rgba(157, 0, 255, 0.1);">
            <h3 style="color: #ff00ff;">💬 Chat</h3>
            <p style="color: #00ff41; font-size: 0.9rem;">
                Interactive chat with any loaded AI model. 
                Stream responses in real-time.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; border: 1px solid #9d00ff; border-radius: 10px; background: rgba(157, 0, 255, 0.1);">
            <h3 style="color: #ff00ff;">🔬 Lab</h3>
            <p style="color: #00ff41; font-size: 0.9rem;">
                Advanced tools: diagnostics, tracing, 
                live training, and brain building.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; border: 1px solid #9d00ff; border-radius: 10px; background: rgba(157, 0, 255, 0.1);">
            <h3 style="color: #ff00ff;">⚡ Local-First</h3>
            <p style="color: #00ff41; font-size: 0.9rem;">
                Run entirely on your machine.
                Your data stays private.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Quick start guide
    st.subheader("🚀 Quick Start Guide")
    
    with st.expander("Step 1: Check Backend Status", expanded=True):
        try:
            response = requests.get(f"{API_BASE.replace('/api', '')}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ Backend is running and healthy!")
            else:
                st.error("❌ Backend responded with an error")
        except requests.exceptions.ConnectionError:
            st.error("❌ Backend is not running. Please start it with `run_backend.bat` or `./run_omni.sh`")
        except Exception as e:
            st.warning(f"⚠️ Could not check backend status: {e}")
    
    with st.expander("Step 2: Available Models", expanded=True):
        try:
            response = requests.get(f"{API_BASE}/models", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if models:
                    st.success(f"✅ Found {len(models)} model(s)")
                    for m in models:
                        status = "✅ Loaded" if m.get("loaded") else "⭕ Not Loaded"
                        st.write(f"  - **{m['name']}** ({m['adapter']}) - {status}")
                else:
                    st.warning("⚠️ No models found. Add model manifests to the `./models` directory.")
        except Exception as e:
            st.error(f"Could not fetch models: {e}")
    
    with st.expander("Step 3: Load Your First Model"):
        st.markdown("""
        1. **Add a model manifest** to `./models/your-model/manifest.json`
        2. **Restart the backend** to discover the model
        3. **Go to Lab > Model Manager** to load it
        4. **Start chatting** in the Chat tab!
        
        **Supported Adapters:**
        - `llama_cpp` - GGUF models (recommended for CPU)
        - `hf_transformers` - HuggingFace models
        - `vllm_remote` - Remote vLLM endpoints
        - `onnx_runtime` - ONNX models
        - `victor_custom` - Custom backends
        - `aai_psm` - Augmented AI with memory
        - `induction` - Optimized inference
        """)
    
    with st.expander("Step 4: Explore Lab Features"):
        st.markdown("""
        The Lab tab contains powerful tools:
        
        - **Model Manager** - Load/unload models
        - **Diagnostics** - Analyze model capabilities
        - **Diagnostics Plus** - EPA amplification & Defense Aura
        - **Brain Builder** - Design custom AI brains
        - **Induction Settings** - Optimize inference
        - **Trace & Target** - Causal localization
        - **Live Train** - Online learning
        - **Tokenizer** - Explore tokenization
        - **Artifacts** - Manage Auras & SkillPacks
        """)
    
    st.divider()
    
    # Continue button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Enter OmniLoader Studio", type="primary", use_container_width=True):
            st.session_state.onboarding_complete = True
            st.rerun()


def render_status_bar():
    """Render a status bar showing system status"""
    # Check backend and models
    backend_ok = False
    model_count = 0
    loaded_count = 0
    
    try:
        response = requests.get(f"{API_BASE.replace('/api', '')}/health", timeout=2)
        backend_ok = response.status_code == 200
        
        response = requests.get(f"{API_BASE}/models", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_count = len(models)
            loaded_count = sum(1 for m in models if m.get("loaded"))
    except:
        pass
    
    # Status bar HTML
    backend_status = "🟢 Online" if backend_ok else "🔴 Offline"
    backend_color = "#00ff41" if backend_ok else "#ff0066"
    
    st.markdown(f"""
    <div style="
        display: flex; 
        justify-content: space-between; 
        align-items: center;
        padding: 0.5rem 1rem;
        background: rgba(10, 10, 10, 0.8);
        border: 1px solid #9d00ff;
        border-radius: 5px;
        margin-bottom: 1rem;
        font-size: 0.85rem;
    ">
        <span style="color: {backend_color};">Backend: {backend_status}</span>
        <span style="color: #00ff41;">Models: {model_count} total, {loaded_count} loaded</span>
        <span style="color: #9d00ff;">v1.0.0</span>
    </div>
    """, unsafe_allow_html=True)


# Main app
def main():
    # Check if onboarding is needed
    if check_onboarding_needed():
        render_welcome_screen()
        return
    
    # Header with branding
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
        <span style="font-size: 2.5rem;">🤖</span>
        <div>
            <h1 style="margin: 0; padding: 0; color: #ff00ff; text-shadow: 0 0 10px #ff00ff;">OmniLoader</h1>
            <p style="margin: 0; padding: 0; color: #00ff41; font-size: 0.9rem;">Studio</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Status bar
    render_status_bar()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "🔬 Lab", "ℹ️ About"])
    
    with tab1:
        render_chat_tab()
    
    with tab2:
        render_lab_tab()
    
    with tab3:
        render_about_tab()
    
    # Footer credit
    st.markdown("""
    <div class="footer">
        dev by iambandobandz under massive magnetics | OmniLoader Studio v1.0.0
    </div>
    """, unsafe_allow_html=True)


def render_about_tab():
    """Render the About tab with documentation and links"""
    st.header("ℹ️ About OmniLoader Studio")
    
    st.markdown("""
    **OmniLoader** is a production-grade, local-first AI model manager with a dual-tab interface 
    (Chat | Lab) for running ANY text-generation model locally.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Features")
        st.markdown("""
        **Core:**
        - Universal model support (7 adapters)
        - Streaming token generation
        - CPU-optimized defaults
        
        **Lab:**
        - Comprehensive diagnostics
        - Causal tracing & interventions
        - Live training (Hot-LoRA, DPO, ROME)
        - Brain Builder for custom AI systems
        
        **GODCORE:**
        - AAI+PSM (Augmented AI + Memory)
        - InductionVM (optimized inference)
        - Defense Aura (jailbreak protection)
        - EPA 2.0 (behavior amplification)
        """)
    
    with col2:
        st.subheader("🔗 Links")
        st.markdown("""
        - [📖 Documentation](http://localhost:8000/docs)
        - [🐙 GitHub Repository](https://github.com/MASSIVEMAGNETICS/project-omni-omega)
        - [🐛 Report Issues](https://github.com/MASSIVEMAGNETICS/project-omni-omega/issues)
        """)
        
        st.subheader("⚙️ System Info")
        try:
            response = requests.get(f"{API_BASE.replace('/api', '')}", timeout=5)
            if response.status_code == 200:
                info = response.json()
                st.write(f"**API Version:** {info.get('version', 'Unknown')}")
                st.write(f"**Status:** {info.get('status', 'Unknown')}")
        except:
            st.write("Could not fetch system info")
        
        st.write(f"**API URL:** `{API_BASE}`")
    
    st.divider()
    
    st.subheader("📋 Keyboard Shortcuts")
    st.markdown("""
    | Action | Shortcut |
    |--------|----------|
    | Send message | `Enter` |
    | New line in input | `Shift+Enter` |
    | Refresh page | `F5` |
    """)
    
    st.divider()
    
    # Show welcome button
    if st.button("🏠 Show Welcome Screen"):
        st.session_state.onboarding_complete = False
        st.rerun()


if __name__ == "__main__":
    main()
