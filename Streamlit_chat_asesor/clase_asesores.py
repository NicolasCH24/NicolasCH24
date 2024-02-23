import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.tools.tavily_search import TavilySearchResults

class CrearAsesores:
#Quizas se pueda en un futuro dar al cliente la posibilidad de elegir la especialidad de su asesor, ya que algunos son mas fuertes en diferentes areas.
#POR AHORA SOLO EL CONVERSACIONAL
    def __init__(self, _retriever):
        self._retriever = _retriever
        self.tools = None
        self.prompt = None

    @st.cache_resource()
    def CrearAsesor(_self,_retriever):
        template = """Sos un asesor util para responder y ayudar a los usuarios de la mejor manera en base tus conocimientos.
            Debes responder de una manera rapida y sencilla, que sea facil de comprender.
            Debes ser amable en todo momento y responder siempre en relacion al lenguaje en el cual se comunican con vos.
            Usa solo tus herramientas en el caso que sea necesario. 
            Por sobre todas las cosas si no sabes la respuesta no inventes una, es decir, comenta que no tenes informacion sobre la pregunta solicitada.
        
        Chat_history : {chat_history}

        Mensaje de usuario : {input}
        Agent_scrachpad : {agent_scratchpad}
        """
        prompt = PromptTemplate(template= template, input_variables=["input","chat_history"])

        search = TavilySearchResults()
        
        tool = create_retriever_tool(
            _retriever,
            "doc_search_tool",
            "Util para buscar informacion sobre tus documentos.",
            )
        tools = [tool, search]
        memory = ConversationBufferMemory(memory_key="chat_history", input_key='input', return_messages=True, output_key='output')
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo-0125",
            temperature=0.3, streaming=True, verbose = True)
        
        agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
        asesor_personal = AgentExecutor(agent=agent,
                                name="Asesor legal",
                                tools=tools,
                                memory=memory,
                                handle_parsing_errors= True,
                                max_iterations=10, 
                                max_execution_time=60.0,
                                )
        return asesor_personal
    
    