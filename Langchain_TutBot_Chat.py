"""Python file to serve as the frontend"""
import streamlit as st
import os
from streamlit_chat import message

from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory

from openai.error import RateLimitError
import backoff

file_path = "/app/tutorbot/LawyerBot.txt"
file_path1 = "/app/tutorbot/educator_bot.txt"

with open(file_path, "r") as file:
    # Read the contents of the file
    file_contents = file.read()
    
lawyerbot = print(file_contents) 

with open(file_path, "r") as file:
    # Read the contents of the file
    file_contents = file.read()

educatorbot = print(file_contents)

@backoff.on_exception(backoff.expo, RateLimitError)
def completions_with_backoff(**kwargs):
    response = openai.Completion.create(**kwargs)
    return response

st.set_page_config(page_title="Tutor Bot", page_icon=":robot:")

# From here down is all the StreamLit UI.
st.header("Bot - GPT")

# os.environ["OPENAI_API_KEY"]=st.text_input(key='OpenAI_Key',label="Enter Your Key", value="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", type="password")
os.environ["OPENAI_API_KEY"]=st.text_input(key='OpenAI_Key',label="Enter Your Key", value=st.secrets["api"], type="password")

def load_chain():
    from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

    system_template= [lawyerbot, educatorbot]

    selected_option = st.selectbox("Select an option", system_template)
    
    messages = [
        SystemMessagePromptTemplate.from_template(selected_option),
        HumanMessagePromptTemplate.from_template("{question}")
    ]
    prompt = ChatPromptTemplate.from_messages(messages)
    
    chain_type_kwargs = {"prompt": prompt}

    llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0, max_tokens=256,openai_api_key="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")  # Modify model_name if you have access to GPT-4
    
    chain = LLMChain(
    llm=llm,
    verbose=True,
    **chain_type_kwargs
    )
    
    return chain
    
@backoff.on_exception(backoff.expo, RateLimitError,max_time=60)
def execute_query(query):
    output = chain(query)
    return output


chain = load_chain()


if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []
    
placeholder = st.empty()

form = st.form("my_form")

user_input=form.text_input("You: ", "Hi, How can I Learn from you?", key="input")

submitted_flag=form.form_submit_button()

if submitted_flag:
    with placeholder.container():

        if user_input:

            output = execute_query(user_input)
            
            st.session_state.past.append(user_input)
            st.session_state.generated.append(output.get('text'))
            
            print('Check Point 2')

        if st.session_state["generated"]:

            for i in range(0, len(st.session_state["generated"]), 1):
                print('Check Point 3')
                message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")
                message(st.session_state["generated"][i], key=str(i))
