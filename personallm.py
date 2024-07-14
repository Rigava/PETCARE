import streamlit as st
import pandas as pd
import google.generativeai as palm


@st.cache_data
def load_data_a():
    df = pd.read_csv('https://raw.githubusercontent.com/Rigava/DataRepo/main/prompts.csv')
    return df 

#For Amazing prompts
st.title('Amazing Prompts')
st.header('This app generates ChatGPT prompts, it is based on a Google Palm model')
df = load_data_a()
st.sidebar.write("Filters")
fil = st.sidebar.multiselect("Select the chatgpt prompts for your character/act",df.act)
filered_df = df[df.act.isin(fil)]
st.write(filered_df)

key =st.secrets.API_KEY
#For Prompting
palm.configure(api_key = key)
model_bison ='models/text-bison-001'
from google.api_core import retry
@retry.Retry()
def generate_text(prompt,
                  model=model_bison,
                  temperature=0.0):
    return palm.generate_text(prompt=prompt,
                              model=model,
                              temperature=temperature)

task_list = ["Generate","Chat"]
task = st.selectbox("What is your task",task_list)
input = st.text_area("ask your question")
priming_input = st.text_area("prompt the persona")
if st.button("Submit"):
        with st.spinner("processing"):
            
            if task == "Generate":
                st.subheader("The most easy way to do it is shown below")
                prompt_template = """
                {priming}

                {question}

                Your solution:
                """
                decorator = "Keep the tone friendly and compelling"
                completion = generate_text(prompt = prompt_template.format(priming=priming_input,question=input))
                output = completion.result
                st.markdown(output)
