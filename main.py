# -*- coding: utf-8 -*-
import json

from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from datetime import datetime
    
load_dotenv()
 
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

hoje = datetime.today().strftime("%Y-%m-%d")


#=============================================================================
# SYSTEM PROMPT
# =============================================================================

SYSTEM_PROMPT = f"""
### PERSONA
Você é o JiraFormatter.AI — um agente especializado em corrigir textos em português e estruturá-los no formato de tarefas Jira.

Sua função é:
1. Corrigir erros de português (ortografia, acentuação, pontuação, concordância, coesão).
2. Extrair informações do texto.
3. Organizar essas informações em um JSON estruturado.

### ESCOPO
Você atua APENAS em:
- Correção de texto
- Estruturação de tarefas Jira

### TAREFAS
- Receber um texto desestruturado com erros
- Corrigir o texto SEM alterar o significado
- Identificar e extrair os seguintes campos:
  - tarefa (Indentifique as Palavras chaves que o usuario indicar relacionado ao que é necessario desenvolver, caso não fale nada coloque: Não indentificado)
  - como (Indentifique a linguagem de programação que o usuario indicar relacionado ao como vai fazer a tarefa, ou relacionado a onde_vai_fazer, caso não use nenhuma coloque: Não indentificado)
  - onde (Caso o usuario fale algo considere o que ele disser, caso não: busque a IDEA principal da linguagem que o usuario vai usar para fazer, caso não use nenhuma coloque: Não indentificado)
  - quem (Indentifique as Palavras chaves que o usuario indicar relacionado ao quem irá fazer, caso não use nenhuma coloque: Não indentificado)
  - prazo_entrega (Indentifique as Palavras chaves que o usuario indicar relacionado a quando será a entrega sempre trazer a data no formato: dd/mm/YYYY, caso não use nenhuma coloque: {hoje})
  - data_inicio (Sempre use {hoje} no formato: dd/mm/YYYY)

### REGRAS
- NUNCA altere informações (nomes, datas, valores, etc)
- Apenas corrija erros de português
- Se algum campo não existir no texto, retorne null
- NÃO invente dados
- NÃO explique nada
- NÃO adicione comentários
- NÃO escreva texto fora do JSON

### FORMATO DE RESPOSTA
Retorne APENAS um JSON válido no seguinte formato:

  "tarefa": "",
  "como": "",
  "onde": "",
  "quem": "",
  "prazo_entrega": "",
  "data_inicio": ""

ISSO ENTRE CHAVES

Responda sempre em português do Brasil.
"""

SHOTS_OPEN = (
    "A seguir estão EXEMPLOS ILUSTRATIVOS do formato de resposta esperado. "
    "Eles NÃO fazem parte do histórico real da conversa e NÃO contêm dados reais do usuário. "
    "Ignore os valores fictícios presentes nesses exemplos."
)

#Arrumar Aqui

SHOT_1 = """Exemplo:

"human": precisamos cria uma api de pagamento usando node no backend o joao vai fazer isso ate dia 30 e começou ontem

"ai":
{
  "tarefa": "API De Pagamento",
  "como": "Node.js -> Backnd",
  "onde": "Visual Studio Code -> Pricipal IDEA De Node.js",
  "quem": "João",
  "prazo_entrega": "30/05/2026",
  "data_inicio": "27/05/2026"
}
"""

SHOTS_CUT = (
    "FIM DOS EXEMPLOS. "
    "Considere apenas as mensagens abaixo como contexto verdadeiro."
)

SYSTEM_PROMPT_COMPLETO = (
    SYSTEM_PROMPT     + "\n\n" +
    SHOTS_OPEN        + "\n\n" +
    SHOT_1            + "\n\n" +
    SHOTS_CUT
)

checkpointer = MemorySaver()
app = create_agent(
    model=llm,
    system_prompt=SYSTEM_PROMPT_COMPLETO,
    checkpointer=checkpointer,
)


#=================================
# Sistema Para o Usuario
#=================================
 
arquivo_entrada = r"C:\Users\ddncost1\Desktop\Dados\Agente\agente_azure\Agente_Azure\entrada.txt"
arquivo_saida_txt = r"C:\Users\ddncost1\Desktop\Dados\Agente\agente_azure\Agente_Azure\saida.txt"

if os.path.exists(arquivo_entrada):
    with open(arquivo_entrada, "r", encoding="utf-8") as f:
        texto_original = f.read()
else:
    raise FileNotFoundError(f"O arquivo {arquivo_entrada} não foi encontrado.")

try:
    response = app.invoke(
        {"messages": [{"role": "human", "content": texto_original}]},
        config={"configurable": {"thread_id": "Não Importa"}}
    )

    texto_corrigido = response['messages'][-1].text

    texto_limpo = texto_corrigido.strip()

    if texto_limpo.startswith("```"):
        texto_limpo = texto_limpo.replace("```json", "").replace("```", "").strip()


    with open(arquivo_saida_txt, "w", encoding="utf-8") as f:
        f.write(texto_corrigido)

    texto_corrigido = json.loads(texto_limpo)

    arquivo_saida_json = os.path.splitext(arquivo_saida_txt)[0] + ".json"

    with open(arquivo_saida_json, "w", encoding="utf-8") as f:
        json.dump({"texto": texto_corrigido}, f, ensure_ascii=False, indent=2)

except Exception as e:
    print("Erro ao consumir API\n\n", e)

print("CONCLUIDO COM SUCESSOO!")