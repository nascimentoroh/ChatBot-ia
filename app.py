import io
import os
import pypdf
import streamlit as st
from openai import AzureOpenAI

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="ChatBot RAG - Microsoft Foundry", page_icon="🤖", layout="wide"
)

# -----------------------------------------------------------------------------
# 1. ESTILIZAÇÃO CSS (Borda estilizada e visual profissional)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Fundo geral suave */
    .stApp {
        background-color: #f4f6f9;
    }
    
    /* Borda estilizada ao redor da área principal do app */
    .main .block-container {
        border: 2px solid #d1d5db;
        border-radius: 16px;
        padding: 2.5rem;
        background-color: #ffffff;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }

    /* Estilização da barra lateral */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    
    /* Títulos e textos */
    h1, h2, h3 {
        color: #1f2937;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. CONFIGURAÇÃO DA API (Microsoft Foundry / Azure AI)
# -----------------------------------------------------------------------------
API_KEY = "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
MODEL_DEPLOYMENT = (  # NOME DO DEPLOYMENT no Azure AI Studio
    "gpt-4.1-mini"
)
ENDPOINT = "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"

# Inicialização do Cliente Azure OpenAI
try:
  client = AzureOpenAI(
      api_key=API_KEY,
      api_version="2024-08-01-preview",  # Versão recomendada para Azure AI
      azure_endpoint=ENDPOINT,
  )
except Exception as e:
  st.error(f"Erro ao inicializar o cliente da API: {e}")

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL: Upload de Arquivos e Sistema RAG
# -----------------------------------------------------------------------------
with st.sidebar:
  st.title("📁 Painel RAG")
  st.markdown("Carregue documentos para consulta inteligente.")
  st.markdown("---")

  # Componente para upload de arquivos PDF e TXT
  uploaded_file = st.file_uploader(
      "Envie um arquivo (PDF ou TXT)", type=["pdf", "txt"]
  )

  document_text = ""

  if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()

    if file_extension == "txt":
      # Leitura de arquivo TXT
      try:
        document_text = uploaded_file.read().decode("utf-8")
        st.success(f"TXT '{uploaded_file.name}' carregado!")
      except Exception as e:
        st.error(f"Erro ao ler TXT: {e}")

    elif file_extension == "pdf":
      # Leitura de arquivo PDF usando pypdf
      try:
        reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
        extracted_pages = []
        for page in reader.pages:
          text = page.extract_text()
          if text:
            extracted_pages.append(text)
        document_text = "\n".join(extracted_pages)
        st.success(f"PDF '{uploaded_file.name}' carregado!")
      except Exception as e:
        st.error(f"Erro ao ler PDF: {e}")

    # Salva o texto extraído no session_state para persistência
    st.session_state["document_text"] = document_text
  else:
    # Recupera do estado da sessão caso já tenha sido carregado anteriormente
    document_text = st.session_state.get("document_text", "")

  if document_text:
    st.info(
        f"**Status RAG:** Ativo ({len(document_text)} caracteres na"
        " base de conhecimento)."
    )
  else:
    st.warning(
        "**Status RAG:** Nenhum documento carregado. O bot responderá sem"
        " contexto adicional."
    )

  st.markdown("---")
  if st.button("🗑️ Limpar Histórico do Chat", use_container_width=True):
    st.session_state.messages = []
    st.session_state["document_text"] = ""
    st.rerun()

# -----------------------------------------------------------------------------
# 4. LÓGICA PRINCIPAL DE CHAT E INTERFACE
# -----------------------------------------------------------------------------
st.title("💬 Assistente Virtual com RAG")
st.markdown(
    "Faça perguntas sobre o documento enviado ou converse diretamente com o"
    " modelo **gpt-4.1-mini** da Microsoft Foundry."
)
st.markdown("---")

# Inicializa o histórico de mensagens no session_state
if "messages" not in st.session_state:
  st.session_state.messages = []

# Exibe o histórico de mensagens na tela
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# Captura a entrada do usuário via chat_input
if prompt := st.chat_input(
    "Digite sua pergunta sobre o documento ou um assunto geral..."
):
  # Adiciona a mensagem do usuário ao histórico
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # Montagem do Prompt do Sistema (RAG Básico)
  system_instruction = (
      "Você é um assistente virtual corporativo especialista. "
      "Responda à pergunta do usuário utilizando primariamente o CONTEXTO DO DOCUMENTO fornecido abaixo. "
      "Caso a resposta não esteja no documento, informe educadamente que o conteúdo não consta no arquivo enviado, "
      "mas ofereça auxílio geral caso seja apropriado."
  )

  current_context = st.session_state.get("document_text", "")
  if current_context:
    full_system_prompt = f"{system_instruction}\n\n--- CONTEXTO DO DOCUMENTO ---\n{current_context}\n-----------------------------"
  else:
    full_system_prompt = (
        f"{system_instruction}\n\nNenhum documento de contexto foi anexado."
    )

  # Prepara as mensagens para a API do Azure OpenAI
  api_messages = [{"role": "system", "content": full_system_prompt}]
  for msg in st.session_state.messages:
    api_messages.append({"role": msg["role"], "content": msg["content"]})

  # Chamada ao modelo no Microsoft Foundry
  with st.chat_message("assistant"):
    with st.spinner("Analisando e gerando resposta..."):
      try:
        response = client.chat.completions.create(
            model=MODEL_DEPLOYMENT,
            messages=api_messages,
            temperature=0.3,
            max_tokens=1200,
        )
        assistant_response = response.choices[0].message.content
        st.markdown(assistant_response)
      except Exception as e:
        assistant_response = (
            f"❌ Erro ao se comunicar com a API do Microsoft Foundry: {e}"
        )
        st.error(assistant_response)

  # Salva a resposta do assistente no histórico
  st.session_state.messages.append(
      {"role": "assistant", "content": assistant_response}
  )
