# 🤖 ChatBot RAG com Microsoft Foundry & Streamlit

Este repositório contém uma aplicação completa de ChatBot com arquitetura **RAG (Retrieval-Augmented Generation)** desenvolvida em **Python** e **Streamlit**, integrada à plataforma **Microsoft Foundry (Azure AI Services)**.

O aplicativo permite o envio de documentos (`.pdf` e `.txt`), extrai seu conteúdo em tempo real e utiliza o modelo `gpt-4.1-mini` da Microsoft/Azure para responder a dúvidas com base no contexto fornecido.

---

## 🚀 Funcionalidades

- **💬 Chat Interativo:** Interface conversacional construída com `st.chat_message` e `st.chat_input`, com histórico salvo no `st.session_state`.
- **📄 Suporte a Documentos (RAG Básico):** Leitura e extração de texto de arquivos **PDF** e **TXT** via barra lateral.
- **🎨 Interface Customizada:** Estilização profissional com CSS embutido (`st.markdown`), adicionando bordas, sombras e layout em formato de cartão na área principal.
- **☁️ Integração Azure AI / Microsoft Foundry:** Conexão direta utilizando o SDK oficial da OpenAI para Azure.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Interface Web:** [Streamlit](https://streamlit.io/)
- **Processamento de PDFs:** `pypdf`
- **Integração com LLM:** `openai` (AzureOpenAI client)

---

## ⚙️ Como Executar o Projeto Localmente

### 1. Pré-requisitos
Certifique-se de ter o **Python** instalado em sua máquina.

### 2. Clonar o Repositório
```bash
git clone [https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git](https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git)
cd NOME-DO-REPOSITORIO
