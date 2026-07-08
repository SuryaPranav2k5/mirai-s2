import streamlit as st

# Configure the Streamlit page layout and title
st.set_page_config(
    page_title="The Void",
    page_icon="🌌",
    layout="centered"
)

# --- Task 1: The UI Shell ---
st.title("The Void")
st.write("Welcome to the Identity Echo Interface. Provide your credentials and a message below to transmit it to the void.")

# --- Task 2: Multi-Data Collection ---
user_name = st.text_input(
    label="Name",
    placeholder="Identify yourself..."
)

user_message = st.text_input(
    label="Message",
    placeholder="Enter the echo transmission payload..."
)

# --- Task 3: The Action Gate ---
transmit_button = st.button("Transmit")

# --- Task 4 & 5: Conditional Routing & Formatted Output ---
if transmit_button:
    if not user_name.strip():
        # Edge Case: Name field is empty
        st.error("Please provide your name.")
    elif not user_message.strip():
        # Edge Case: Message field is empty
        st.warning("Please type a message to transmit.")
    else:
        # Success Case: Both fields are populated
        st.success(f"Transmission successful! Greetings, {user_name}. We received your message: {user_message}")
        
        # --- Advanced Challenge: Token Cost Estimator ---
        char_length = len(user_message)
        token_count = char_length / 4
        
        # Format token_count as integer if it represents a whole number
        if token_count.is_integer():
            token_count = int(token_count)
            
        st.info(f"System Check: Your message will consume approximately {token_count} tokens from our context window.")
