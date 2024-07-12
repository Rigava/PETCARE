import streamlit as st
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# import chromadb
from crewai import Crew, Process, Agent, Task
from langchain_core.callbacks import BaseCallbackHandler
from typing import TYPE_CHECKING, Any, Dict, Optional

import google.generativeai as genai 
key =st.secrets.API_KEY
genai.configure(api_key=key)


# from langchain_google_genai import GoogleGenerativeAI
# llm = GoogleGenerativeAI(model='models/text-bison-001',google_api_key=key)
from langchain_community.llms import GooglePalm
llm = GooglePalm(model ='models/text-bison-001',google_api_key =key)



avators = {"Writer":"https://cdn-icons-png.flaticon.com/512/320/320336.png",
            "Reviewer":"https://cdn-icons-png.freepik.com/512/9408/9408201.png"}


class MyCustomHandler(BaseCallbackHandler):

    
    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Print out that we are entering a chain."""
        st.session_state.messages.append({"role": "assistant", "content": inputs['input']})
        st.chat_message("assistant").write(inputs['input'])
   
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""
        st.session_state.messages.append({"role": self.agent_name, "content": outputs['output']})
        st.chat_message(self.agent_name, avatar=avators[self.agent_name]).write(outputs['output'])


st.title("💬 Snoopy Care")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "What is the test report and the result?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    Writer = Agent(
        role='Veterinary doctor',
        backstory='''You have a knack for beagle breed.''',
        goal="Write the interpretation of dog test.",
        llm=llm,
        callbacks=[MyCustomHandler("Writer")],
    )
    Reviewer = Agent(
        role='Senior Veterinary doctor',
        backstory = '''You're a meticulous doctor with a keen eye for detail. You're known for
                    your ability to turn complex case into clear and concise reports, making
                    it easy for others to understand and act on the information you provide..''',
        goal="Write the clinical context,next step and conclusion of the dog test",
        llm=llm,
        callbacks=[MyCustomHandler("Reviewer")],
    )

    task1 = Task(
      description=f"""Write the refrence ranges to compare against the {prompt}. """,
      agent=Writer,
      expected_output="Prepare a interpretation of the dog test result."
    )

    task2 = Task(
      description="""Using the iterpreatation provided, provide a comprhensive diagnosis.""",
      agent=Reviewer,
      expected_output="Provide a diagnostic report including the clinical context , next steps and conclusion."
    )
    # Establishing the crew with a hierarchical process
    project_crew = Crew(
        tasks=[task1, task2],  # Tasks to be delegated and executed under the manager's supervision
        agents=[Writer, Reviewer],
        manager_llm=llm,
        process=Process.hierarchical  # Specifies the hierarchical management approach
    )
    final = project_crew.kickoff()

    result = f"## Here is the Final Result \n\n {final}"
    st.session_state.messages.append({"role": "assistant", "content": result})
    st.chat_message("assistant").write(result)