import streamlit as st
from streamlit.components.v1 import html
from datetime import datetime
from intent_detector import IntentDetector
from orchestrator import Orchestrator
from knowledge.store import KnowledgeStore
import base64
import os
# --- Set Streamlit page config ---
st.set_page_config(page_title="Ripple Copilot", layout="wide", initial_sidebar_state="expanded")



# Icons for user and assistant
ICON_SVG = {
    "user": "👤",
    "assistant": "🤖",
}


# Custom CSS for VSCode-like look
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: "Consolas", "Courier New", monospace;
        font-size: 12px;
        background-color: #1e1e1e;
        color: #d4d4d4;
    }

    /* Header styling */
    .header {
        background-color: #252526;
        padding: 1rem;
        border-bottom: 1px solid #3c3c3c;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-title {
        font-size: 18px;
        font-weight: bold;
        color: #4FC3F7;
    }
    .header-status {
        font-size: 12px;
        color: #888;
    }

    .logo {
        position: fixed;
        top: 15px;
        left: 15px;
        width: 80px;
        z-index: 100;
    }
    /* Chat container */

    .chat-container {
    max-height: 400px;
    overflow-y: auto;
    padding: 1rem;
    border-radius: 10px;
    background-color: #1e1e1e;
    border: 1px solid #444;
    }
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    .chat-container::-webkit-scrollbar-thumb {
        background: #444;
        border-radius: 10px;
    }
    /* Scroll to bottom */
    .chat-container::after {
        content: '';
        display: block;
        height: 1px;
        visibility: hidden;
    }

    /* Chat bubble container */
    .chat-row {
        display: flex;
        flex-wrap: wrap;
        margin-bottom: 0.5rem;
        width: 100%;
        box-sizing: border-box;
    }

    .chat-left {
        justify-content: flex-start;
    }

    .chat-right {
        justify-content: flex-end;
    }

    .chat-bubble {
        max-width: 70%;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        font-size: 12px;
        line-height: 1.5;
        box-sizing: border-box;
    }

    .chat-bubble.user {
        background-color: #2d2d2d;
        color: white;
        border-left: 4px solid #777;
    }

    .chat-bubble.assistant {
        background-color: #007acc;
        color: white;
        border-left: 4px solid #4FC3F7;
    }

    /* Timestamp */
    .chat-timestamp {
        font-size: 10px;
        color: #888;
        margin-top: 0.2rem;
        text-align: right;
    }

    /* Avatar icons */
    .avatar-icon {
        width: 28px;
        height: 28px;
        margin: 0 0.5rem;
        font-size: 20px;
        flex-shrink: 0;
    }

    .avatar-icon.user {
        color: #aaa;
    }

    .avatar-icon.assistant {
        color: #4FC3F7;
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #252526;
    }

    .sidebar-expander {
        background-color: #333;
        border: 1px solid #3c3c3c;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }

    .sidebar-button {
        background-color: #007acc;
        color: white;
        border: none;
        padding: 0.3rem 0.6rem;
        border-radius: 3px;
        font-size: 12px;
        cursor: pointer;
    }

    .sidebar-button:hover {
        background-color: #005f99;
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .chat-bubble {
            max-width: 85%;
        }
        .chat-container {
            height: 50vh;
        }
        .avatar-icon {
            width: 20px;
            height: 20px;
            font-size: 16px;
        }
    }
    </style>


    """,
    unsafe_allow_html=True
)



st.markdown("""
<style>
.chat-container {
    height: 500px;               /* Fixed size */
    overflow-y: auto;
    padding: 1rem;
    border-radius: 10px;
    background-color: #1e1e1e;
    border: 1px solid #444;
    margin-bottom: 1rem;
    scroll-behavior: smooth;
}

.chat-container::-webkit-scrollbar {
    width: 6px;
}
.chat-container::-webkit-scrollbar-thumb {
    background: #444;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)
# Init components
# This is where we initialize the intent detector, which will process user inputs and detect intents."""
intent_detector = IntentDetector()

# Initialize knowledge store 
#This is where we load the knowledge store, which contains projects and experiments."""
store = KnowledgeStore()

#This is where we initialize the orchestrator, which will handle the intent processing and interaction with the knowledge store."""
# Initialize orchestrator with the store
orchestrator = Orchestrator(store)



# Render message with timestamp and proper styling
def render_message(role, message, timestamp=None):
    alignment = "flex-start" if role == "assistant" else "flex-end"
    bg_color = "#007acc" if role == "assistant" else "#2d2d2d"
    text_color = "#ffffff"
    border_color = "#4FC3F7" if role == "assistant" else "#777"
    icon = "🤖" if role == "assistant" else "👤"
    if timestamp is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")


    return f"""
    <div style="display: flex; justify-content: {alignment}; margin-bottom: 0.5rem;">
        <div style="
            background-color: {bg_color};
            color: {text_color};
            padding: 0.5rem 0.75rem;
            max-width: 70%;
            border-radius: 10px;
            border-left: 4px solid {border_color};
            font-family: Consolas, monospace;
            font-size: 12px;
            line-height: 1.4;
        ">
            <span style="margin-right: 0.5rem;">{icon}</span>
            {message}
            <div style="font-size: 10px; color: #ccc; margin-top: 4px;">{timestamp}</div>
        </div>
    </div>
    """




# --- STATE INIT ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.last_prompt = ""
#--- HEADER ---

st.markdown(
    """
    <div class="header">
        <span class="header-title">Ripple Copilot</span>
        <span class="header-status">Online • 08:59 PM -04, May 23, 2025</span>
    </div>
    """,
    unsafe_allow_html=True,
)



# --- SIDEBAR: Projects and Experiments ---
with st.sidebar:
    st.image("https://rplmvpbucket.s3.us-east-2.amazonaws.com/logo2.png", width=100)
    st.title("📁 Projects")

    all_projects = store.data.get("projects", {})


    if not all_projects:
        st.markdown("Create one to get started!")
    else:

        for project, details in all_projects.items():

            with st.expander(f"{project}", expanded=False,icon=":material/arrow_right:"):
                
                st.markdown(f"**Description:** {details.get('description', 'No description')}")

                files = details.get("files", [])

                if not files:
                    st.markdown("No files attached.")
                else:
                    for file in files:
                        if st.button(file["file_name"], icon=":material/csv:", use_container_width=False):
                            st.markdown("You clicked the Material button.")
                        # if st.button(file["file_name"], type="tertiary"):
                        #     pass


                experiments = details.get("experiments", [])


                if not experiments:
                    st.markdown("No experiments logged.")
                else:

                    for exp in details.get("experiments", []):
                        col1, col2 = st.columns([2, 5])


                        with col1:
                            st.markdown(f" {exp.get('name', 'Unnamed')}")
                        with col2:
                            st.markdown(f"{exp.get('description', '')}\n")
                            
                            st.markdown(f"""<p><em>Results:<br />{exp.get('results', '')}</em></p>""",unsafe_allow_html=True)

                            st.markdown(f"""<p><em>Date<br />{exp.get('timestamp', '')}</em></p>""",unsafe_allow_html=True)


                if st.button("Delete Project", key=f"delete_{project}", help="Delete this project"):
                    del store.data["projects"][project]
                    store.save()
                    st.session_state.chat_history.append(
                        ("assistant", f"Project '{project}' deleted successfully.")
                    )
                    st.rerun()

# --- MAIN PANEL: Chat UI ---
# 1. Generate chat HTML
chat_html = "".join([
    render_message(role, msg if isinstance(msg, str) else msg.get("message", str(msg)))
    for role, msg in st.session_state.chat_history
])


st.markdown(
    f"""
    <div id="chatbox" class="chat-container">
    {chat_html}
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<script>
const chatContainer = window.parent.document.getElementById('chatbox');
if (chatContainer) {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
</script>
""", unsafe_allow_html=True)



# Chat input with loading state
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Describe your intent...", key="user_input")
    submit_button = st.form_submit_button("Send")

if submit_button and user_input:
    with st.spinner("Processing your request..."):
        try:
            result = intent_detector.detect(user_input)

            if result.get("intent") == "error":
                response = {"status": "error", "message": result["data"]["error"]}
            else:
                response = orchestrator.process_intent(result)
                
        except Exception as e:
            response = {"status": "error", "message": f"Failed to process intent: {str(e)}"}

    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("assistant", response))
    st.session_state.last_prompt = user_input  # Store last prompt for file upload context
    st.rerun()


st.markdown("#### 📤 Upload Experiment File")
os.makedirs("uploaded_files", exist_ok=True)

uploaded_file = st.file_uploader("Upload result file (e.g. .csv)", type=["csv", "txt", "png", "jpg"])

# After uploaded_file = st.file_uploader(...)
if uploaded_file is not None:
    file_name = uploaded_file.name

    # Save the file
    save_path = f"uploaded_files/{file_name}"
    os.makedirs("uploaded_files", exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Detect intent from user prompt
    user_input = st.session_state.last_prompt  # or however you're storing it
    result = intent_detector.detect(user_input)

    # ✅ Inject the uploaded filename into the intent
    if result["intent"] == "upload_file":
        result["data"]["file_name"] = file_name

    # ✅ Fallback to last active project if project is missing
    if "project" not in result["data"]:
        result["data"]["project"] = orchestrator.last_active_project

    # Run through orchestrator
    response = orchestrator.process_intent(result)
    st.session_state.chat_history.append(("assistant", response))




# Render chat history

for role, msg in st.session_state.chat_history:
    text = msg if isinstance(msg, str) else msg.get("message", str(msg))
    
