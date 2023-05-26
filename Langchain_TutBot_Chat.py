"""Python file to serve as the frontend"""
import streamlit as st
import os
from streamlit_chat import message

from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory

from openai.error import RateLimitError
import backoff

@backoff.on_exception(backoff.expo, RateLimitError)
def completions_with_backoff(**kwargs):
    response = openai.Completion.create(**kwargs)
    return response

st.set_page_config(page_title="Tutor Bot", page_icon=":robot:")

# From here down is all the StreamLit UI.
st.header("Tutor Bot - GPT")

os.environ["OPENAI_API_KEY"]=st.text_input(key='OpenAI_Key',label="Enter Your Key", value=st.secrets["user_api_key"], type="password")

def load_chain():
    from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

    system_template="""
You're a StudyBot below are your traits and features 

Topic
Constraints 
	Style: supportive, educational, informative, encouraging, enthusiastic. 
	Encourage the student to learn at the limits of their current understanding. 
	You are role-playing as the tutor. Refrain from issuing commands. 12 year old reading level.
	Frequent emotes to display enthusiasm, e.g., moonwalks


/learn [topic] - set the topic and provide a brief introduction, then list available commands.

/v | vocab - List a glossary of essential related terms with brief, concise definitions.

/f | flashcards - Play the glossary flashcard game.

/e | expand - Explore a subtopic more thoroughly.

/q | quiz Generate a concise question to test the student on their comprehension. Favor questions that force the learner to practice the skill being taught.

/n | next - move to the most logical next subtopic.

/h | help - List commands.



echo("Welcome to StudyBot. Type /learn [topic] to begin.")
"""
    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}")
    ]
    prompt = ChatPromptTemplate.from_messages(messages)
    
    chain_type_kwargs = {"prompt": prompt}

    llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0, max_tokens=256,openai_api_key=st.secrets["user_api_key"])  # Modify model_name if you have access to GPT-4
    
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
