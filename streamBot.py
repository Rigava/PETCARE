# https://www.youtube.com/watch?v=zKGeRWjJlTU
# https://alejandro-ao.com/how-to-use-streaming-in-langchain-and-streamlit/
# https://github.com/amjadraza/streamlit-agent/blob/main/streamlit_agent/basic_streaming.py
import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models.google_palm import ChatGooglePalm
from langchain_google_genai import ChatGoogleGenerativeAI 

key=  "AIzaSyAKEaaM7fWIErN3VbikjP_T5m0UfhBy5iE"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.set_page_config(page_title="streaming bot", page_icon =':bar_chart:')
st.title("Streaming Bot")
#Get response of ai
def get_response(user_query, chat_history):

    template = """
    You are a helpful assistant. Answer the following questions considering the history of the conversation:

    Chat history: {chat_history}

    User question: {user_question}
    """

    prompt = ChatPromptTemplate.from_template(template)
    # llm = ChatGooglePalm(model ='models/gemini-1.0-pro',google_api_key =key)
    llm = ChatGoogleGenerativeAI(
model="gemini-pro",
temperature=0.1,
google_api_key=key,
)

        
    chain = prompt | llm | StrOutputParser()
    
    return chain.stream({
        "chat_history": chat_history,
        "user_question": user_query,
    })

#Conversation
for message in st.session_state.chat_history:
    if isinstance(message,HumanMessage):
        with st.chat_message("human"):
            st.markdown(message.content)
    else:
        with st.chat_message("ai"):
            st.markdown(message.content)
#Chat with user input
user_query = st.chat_input("Your message")
if user_query is not None and user_query !="":
    st.session_state.chat_history.append(HumanMessage(user_query))

    with st.chat_message("human"):
        st.markdown(user_query)    
    with st.chat_message("ai"):
        # ai_response = get_response(user_query,st.session_state.chat_history)
        # st.markdown(ai_response)
        ai_response = st.write_stream(get_response(user_query,st.session_state.chat_history))
    st.session_state.chat_history.append(AIMessage(ai_response))

