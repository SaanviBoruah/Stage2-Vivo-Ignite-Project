import os
import sqlite3
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

# Set page config FIRST
st.set_page_config(page_title="Character Chatbot", layout="wide")

with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# Initialize environment and LLM
load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0.7)

# Initialize session state
if "characters" not in st.session_state:
    st.session_state.characters = {}
if "current_character" not in st.session_state:
    st.session_state.current_character = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

# Database setup
DATABASE_FILE = "prebuilt_characters.db"

@st.cache_resource
def load_prebuilt_characters():
    """Load prebuilt characters from SQLite database"""
    characters = {}
    if os.path.exists(DATABASE_FILE):
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT name, personality, backstory, examples, category FROM prebuilt_characters')
        for name, personality, backstory, examples, category in cursor.fetchall():
            characters[name] = {
                "name": name,
                "personality": personality,
                "backstory": backstory,
                "examples": examples,
                "category": category
            }
        conn.close()
    return characters

# Load prebuilt characters once
prebuilt_chars = load_prebuilt_characters()
st.session_state.characters.update(prebuilt_chars)


def character_selection_ui():
    """Sidebar UI for support type selection"""
    st.sidebar.header("Mental Support Chatbot")
    
    # Group characters by category
    categories = {
        "Assistants": [],
        "Anime": [],
        "Entertainment & Gaming": [],
        "Custom": [],
        "Mental Wellness": []
    }
    
    for name, data in st.session_state.characters.items():
        category = data.get("category", "Custom")
        if category in categories:
            categories[category].append((name, data))
        else:
            categories["Custom"].append((name, data))
    
    # Category selection
    selected_category = "Mental Wellness"
    
    # Character selection
    if selected_category:

        selected_char = st.sidebar.radio(
            "Select Support Type",
            [name for name, _ in categories[selected_category]]
        )
        
        if st.sidebar.button("Select Character"):
            st.session_state.current_character = st.session_state.characters[selected_char]
            st.session_state.chat_history[selected_char] = st.session_state.chat_history.get(selected_char, [])
            st.rerun()

def chat_interface():
    """Main chat interface"""
    st.title("Emotional Support Chatbot 💬")

    st.sidebar.markdown("""
        <div style="background:#EAEAED; padding:10px; text-align: center; border-radius:10px; border:2px solid #55E4C4; margin-bottom:20px">
        Built by <strong style="color:#ff4c4b">Saanvi Boruah</strong>. Project submission: <strong style="color:#ff4c4b">Multi-modal emotional wellbeing analysis suite</strong> for Vivo Ignite.
        </div>
        """, unsafe_allow_html=True)
    
    if not st.session_state.current_character:
        st.info("Please select a character from the sidebar")
        return
    
    char = st.session_state.current_character
    history = st.session_state.chat_history[char["name"]]
    
    # Character info
    with st.expander("Character Details"):
        st.subheader(char["name"])
        st.caption(f"{char.get('category', 'Custom')} Chatbot")
        st.write(f"**Personality**: {char['personality']}")
        st.write(f"**Backstory**: {char['backstory']}")
    
    # Chat history
    for msg in history:
        with st.chat_message("user"):
            st.write(msg["user"])
        with st.chat_message("assistant"):
            st.write(f"{char['name']}: {msg['bot']}")
    
    # User input
    if prompt := st.chat_input("Type your message..."):
        # Generate response
        history_context = "\n".join(
            [f"User: {msg['user']}\n{char['name']}: {msg['bot']}" 
             for msg in history]
        ) if history else "No previous conversation"
        
        prompt_template = PromptTemplate.from_template(
            """You are {name}, a character with these personality traits: {personality}.
    Backstory: {backstory}
    Example dialogues: {examples}

    Previous conversation:
    {history}

    Stay in character and respond to this message:
    User: {input}
    {name}:"""
        )

        try:
            response = prompt_template | llm
            result = response.invoke({
                "name": char["name"],
                "personality": char["personality"],
                "backstory": char["backstory"],
                "examples": char["examples"],
                "history": history_context,
                "input": prompt
            })
            bot_response = result.content.strip()
            
            # Update history
            history.append({"user": prompt, "bot": bot_response})
            
            # Rerun to show new messages
            st.rerun()
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")

def main():
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("Please set your GOOGLE_API_KEY in .env file!")
        return
    
    # Sidebar components
    character_selection_ui()
    
    # Main chat interface
    chat_interface()

if __name__ == "__main__":
    main()
