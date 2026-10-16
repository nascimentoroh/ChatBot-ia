import io
import os
import pypdf
import streamlit as st
from openai import AzureOpenAI

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="Assistente Contábil | IA", page_icon="💼", layout="wide"
)

# -----------------------------------------------------------------------------
# 1. ESTILIZAÇÃO CSS (Design Elegante, Feminino e Profissional)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Fundo geral suave e sofisticado (Tom Linha/Off-White) */
    .stApp {
        background-color: #fbf9f7;
        color: #2c2c2c;
        font-family: 'Inter', sans-serif;
    }
    
    /* Borda estilizada ao redor da área principal do app (Efeito Cartão Clean) */
    .main .block-container {
        border: 1.5px solid #e8dcdf;
        border-radius: 20px;
        padding: 2.5rem;
        background-color: #ffffff;
        box-shadow: 0 8px 24px rgba(183, 110, 121, 0.06);
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }

    /* Estilização da barra lateral (Tom Rosa Quartzo Suave) */
    [data-testid="stSidebar"] {
        background-color: #f6f1f2;
        border-right: 1px solid #eadbde;
    }
    
    /* Títulos e cabeçalhos com tom corporativo elegante */
    h1, h2, h3 {
        color: #3b3032;
        font-weight: 600;
    }

    /* Botões personalizados */
    .stButton > button {
        background-color: #9f5c6b;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #834956;
        color: white;
        border: none;
    }

    /* Campo de upload de arquivos refinado */
    [data-testid="stFileUploader"] {
        border: 1px dashed #d4b5bc;
        border-radius: 12px;
        padding: 1rem;
        background-color: #ffffff;
    }

    /* Mensagens do chat com visual refinado */
    [data-testid="stChatMessage"] {
        border-radius: 14px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        margin-bottom: 0.8rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. CONFIGURAÇÃO DA API (Microsoft Foundry / Azure AI)
# -----------------------------------------------------------------------------
API_KEY = "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
MODEL_DEPLOYMENT = "gpt-4.1-mini"
ENDPOINT = "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"

# Inicialização do Cliente Azure OpenAI
try:
  client = AzureOpenAI(
      api_key=API_KEY,
      api_version="2024-08-01-preview",
      azure_endpoint=ENDPOINT,
  )
except Exception as e:
  st.error(f"Erro ao inicializar o cliente da API: {e}")

# -----------------------------------------------------------------------------
# 3. BARRA LATERAL: Upload de Documentos e Gestão RAG
# -----------------------------------------------------------------------------
with st.sidebar:
  st.markdown("### 💼 Painel Contábil RAG")
  st.markdown(
      "Carregue balanços, balancetes, extratos ou leis para consulta."
  )
  st.markdown("---")

  # Componente para upload de arquivos PDF e TXT
  uploaded_file = st.file_uploader(
      "Selecione um arquivo (PDF ou TXT)", type=["pdf", "txt"]
  )

  document_text = ""

  if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()

    if file_extension == "txt":
      try:
        document_text = uploaded_file.read().decode("utf-8")
        st.success(f"Arquivo TXT '{uploaded_file.name}' carregado com sucesso!")
      except Exception as e:
        st.error(f"Erro ao ler TXT: {e}")

    elif file_extension == "pdf":
      try:
        reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
        extracted_pages = []
        for page in reader.pages:
          text = page.extract_text()
          if text:
            extracted_pages.append(text)
        document_text = "\n".join(extracted_pages)
        st.success(f"Arquivo PDF '{uploaded_file.name}' carregado com sucesso!")
      except Exception as e:
        st.error(f"Erro ao ler PDF: {e}")

    st.session_state["document_text"] = document_text
  else:
    document_text = st.session_state.get("document_text", "")

  if document_text:
    st.info(
        f"**Base Conectada:** {len(document_text):,} caracteres prontos para"
        " análise."
    )
  else:
    st.warning("⚠️ Nenhum documento carregado no momento.")

  st.markdown("---")
  if st.button("🗑️ Limpar Conversa e Base", use_container_width=True):
    st.session_state.messages = []
    st.session_state["document_text"] = ""
    st.rerun()

# -----------------------------------------------------------------------------
# 4. LÓGICA PRINCIPAL DE CHAT E INTERFACE
# -----------------------------------------------------------------------------
st.title("✨ Assistente Contábil Inteligente")
st.markdown(
    "Gerencie suas dúvidas fiscais, financeiras e análise de documentos com o"
    " auxílio do modelo **gpt-4.1-mini**."
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
    "Digite sua dúvida contábil ou faça uma pergunta sobre o documento..."
):
  # Adiciona a mensagem do usuário ao histórico
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # Montagem do Prompt do Sistema (RAG Especializado para Contabilidade)
  system_instruction = (
      "Você é uma inteligência artificial assistente sênior especializada em"
      " contabilidade, finanças e legislação fiscal. Responda às perguntas"
      " utilizando com prioridade o CONTEXTO DO DOCUMENTO fornecido abaixo. Se"
      " a resposta não estiver no documento, utilize seus conhecimentos"
      " contábeis gerais, mas alerte claramente o usuário sobre isso. Mantenha"
      " um tom profissional, analítico, claro e objetivo."
  )

  current_context = st.session_state.get("document_text", "")
  if current_context:
    full_system_prompt = (
        f"{system_instruction}\n\n--- CONTEXTO DO DOCUMENTO CONTÁBIL"
        f" ---\n{current_context}\n---------------------------------------"
    )
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
    with st.spinner("Analisando dados contábeis..."):
      try:
        response = client.chat.completions.create(
            model=MODEL_DEPLOYMENT,
            messages=api_messages,
            temperature=0.2,
            max_tokens=1500,
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
