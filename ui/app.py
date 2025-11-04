"""
OmniLoader Streamlit UI - Dual-tab interface (Chat | Lab)
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

# Custom CSS - Dark Neon Cyberpunk Theme
st.markdown("""
<style>
    /* Main app background - pure black */
    .stApp {
        max-width: 100%;
        background-color: #000000;
        color: #00ff41;
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


# Main app
def main():
    # Header
    st.markdown("# 🤖 OmniLoader")
    st.markdown("*Production-grade local-first AI model manager*")
    
    # Main tabs
    tab1, tab2 = st.tabs(["💬 Chat", "🔬 Lab"])
    
    with tab1:
        render_chat_tab()
    
    with tab2:
        render_lab_tab()


if __name__ == "__main__":
    main()
