
import hmac
import streamlit as st
from openai import AzureOpenAI
from patient import Patients
from prompts import get_prompt, EXAMPLES



def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.


# Main Streamlit app starts here
st.title('👩‍⚕️ Welcome to Doctor Ring Chat')


#Prettify the values in drop down list for patients
def names_format(option):
    if option == "not_selected":
        return "-"
    return option.replace('_', ' ').title()

#Reset the session and initialize chat for selected patient
def reset_chat():
    st.session_state.messages = []

patient_names = Patients()

st.sidebar.success("Choose a patient for discussion.")

person_name = st.sidebar.selectbox("Choose a patient", patient_names.patients.keys(), format_func=names_format, 
                                 label_visibility = "collapsed", on_change=reset_chat)

initial_prompt = "Please select a patient to chat about"
st.session_state.patient = person_name
if person_name == "not_selected":
    person_full_name = ""
else:
    person_full_name = person_name.replace('_', ' ').title()
    initial_prompt = f"What questions can I answer for {person_full_name}?"

st.session_state.patient_full_name = person_full_name
st.session_state.patient_history = patient_names.patients[person_name]


def is_patient_selected():
    if st.session_state.patient_full_name == "":
        return False
    else:
        return True
    

if not is_patient_selected():
    with st.chat_message("assistant"):
        st.markdown("Please select a patient to proceed")
    st.stop()  # Do not continue if patient is not picked


def get_messages():
    messages = [{"role":"system","content":get_prompt(st.session_state.patient_history)}]
    for example in EXAMPLES:
        messages.append(example)

    for m in st.session_state.messages:
        chat_message = {"role": m["role"], "content": m["content"]}
        messages.append(chat_message)
    
    return messages


#Initialize chat with Azure Open AI
client = AzureOpenAI(
  azure_endpoint = st.secrets["AZURE_OPENAI_ENDPOINT"], 
  api_key=st.secrets["AZURE_OPENAI_KEY"],  
  api_version="2023-07-01-preview"
)


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    
    if message["role"] == "assistant":
        avatar = "https://cdn-icons-png.flaticon.com/512/3209/3209028.png"
    else:
        avatar = "https://cdn4.iconfinder.com/data/icons/small-n-flat/24/user-1024.png"
    
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input(initial_prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="https://cdn4.iconfinder.com/data/icons/small-n-flat/24/user-1024.png"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar = "https://cdn-icons-png.flaticon.com/512/3209/3209028.png"):
        message_placeholder = st.empty()
        full_response = ""
        completion = client.chat.completions.create(
                    messages=get_messages(),
                    max_tokens=1500,
                    model="gpt-35-turbo"
                    )
        full_response += completion.choices[0].message.content
        
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})