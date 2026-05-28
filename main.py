# -*- coding: utf-8 -*-

###============================================================================
### IMPORTS
###============================================================================

import json

from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from datetime import datetime
from system_prompt import SYSTEM_PROMPT_COMPLETO
load_dotenv()



###============================================================================
### CRIANDO AS DEF
###============================================================================

def agente_ortografia(input):
    try:
        response = app.invoke(
            {"messages": [{"role": "human", "content": input}]},
            config={"configurable": {"thread_id": "Não Importa"}}
        )

        return str(response['messages'][-1].text)

    except Exception as e:
        erro = str("Erro ao consumir API\n\n", e)
        return erro
    
def estruturar(txt, aqv_entrada, aqv_saida):
    if os.path.exists(entrada):
        with open(entrada, "r", encoding="utf-8") as f:
            texto_original = f.read()
    else:
        raise FileNotFoundError(f"O arquivo {entrada} não foi encontrado.")
    
    texto_corrigido = response['messages'][-1].text

    texto_limpo = texto_corrigido.strip()

    if texto_limpo.startswith("```"):
        texto_limpo = texto_limpo.replace("```json", "").replace("```", "").strip()


    with open(saida, "w", encoding="utf-8") as f:
        f.write(texto_corrigido)

    texto_corrigido = json.loads(texto_limpo)

    arquivo_saida_json = os.path.splitext(saida)[0] + ".json"

    with open(arquivo_saida_json, "w", encoding="utf-8") as f:
        json.dump({"texto": texto_corrigido}, f, ensure_ascii=False, indent=2)

###============================================================================
### Criando os agentes | Usando Falbacks
###============================================================================
 
llm_gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    top_p=0.95,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

llm_groq = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
    #top_p=0.95,
    api_key=os.getenv("GROQ_API_KEY")
)

llm = llm_gemini.with_fallbacks([llm_groq])

hoje = datetime.today().strftime("%d-%m-%Y")

###============================================================================
### Definindo Checkpointer
###============================================================================

checkpointer = MemorySaver()
app = create_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT_COMPLETO,
    checkpointer=checkpointer,
)


#=================================
# Sistema Para o Usuario
#=================================
 
entrada = r"C:\Users\ddncost1\Desktop\Dados\Agente\agente_azure\Agente_Azure\entrada.txt"
saida = r"C:\Users\ddncost1\Desktop\Dados\Agente\agente_azure\Agente_Azure\saida.txt"

print("CONCLUIDO COM SUCESSOO!")