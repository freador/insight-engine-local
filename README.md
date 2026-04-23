# 🚀 InsightEngine: O Seu Hub de Inteligência Pessoal

O **InsightEngine** é um rastreador de notícias e agregador de informações inteligente, projetado para transformar o caos da internet em conhecimento estruturado. Ele combina coleta multi-fonte (RSS, YouTube, GitHub, Web Scraping) com o poder do processamento de linguagem natural local via **Ollama**.

![Mockup do InsightEngine](https://img.shields.io/badge/Status-Ativo-brightgreen?style=for-the-badge)
![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Ollama Support](https://img.shields.io/badge/AI-Ollama%20(Llama3)-orange?style=for-the-badge)

---

## ✨ Funcionalidades Principais

*   **🔍 Coleta Multi-Fonte**: Rastreia automaticamente RSS Feeds, canais do YouTube, repositórios do GitHub e sites genéricos (via Web Scraping inteligente).
*   **🤖 Inteligência Artificial Local**: Utiliza modelos como `llama3` via Ollama para gerar resumos analíticos, identificar tendências e filtrar o que realmente importa.
*   **📊 Dashboard Premium**: Interface web moderna construída com Flask para visualizar seus insights, gerenciar fontes e ler relatórios diários.
*   **📅 Resumo Executivo Diário**: Gera automaticamente uma síntese global e relatórios por categoria para você começar o dia bem informado.
*   **⚙️ Gestão de Fontes**: Adicione, edite ou remova fontes diretamente pelo dashboard, definindo limites de itens e categorias personalizadas.

---

## 🛠️ Stack Tecnológica

- **Backend**: Python 3.10+, Flask
- **Banco de Dados**: SQLite (via SQLAlchemy)
- **Cérebro (IA)**: Ollama (`llama3`)
- **Coleta**: `yt-dlp` (YouTube), `feedparser` (RSS), `BeautifulSoup4` (Scraping)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

---

## 🚀 Como Começar

### Pré-requisitos

1.  **Python 3.10+** instalado.
2.  **Ollama** instalado e rodando em sua máquina.
    *   Baixe em: [ollama.com](https://ollama.com)
    *   Certifique-se de baixar o modelo padrão: `ollama pull llama3`

### Instalação

1.  **Clone o repositório**:
    ```bash
    git clone https://github.com/seu-usuario/biro-news-tracker.git
    cd biro-news-tracker
    ```

2.  **Crie e ative um ambiente virtual**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```

3.  **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Inicialize a aplicação** (Opcional - via script):
    ```bash
    bash init_app.sh
    ```

---

## 🖥️ Como Usar

### 1. Inicie o Pipeline de Coleta
Para buscar as notícias mais recentes e processá-las:
```bash
python pipeline.py
```

### 2. Inicie o Dashboard Web
Para visualizar seus insights e gerenciar a aplicação:
```bash
python app_web.py
```
Acesse: [http://127.0.0.1:5001](http://127.0.0.1:5001)

---

## 📂 Estrutura do Projeto

```text
.
├── app_web.py          # Servidor Flask e API
├── pipeline.py         # Motor de coleta e processamento
├── core/               # Lógica central (DB, Resumidor AI)
├── collectors/         # Módulos de coleta (YouTube, RSS, Scraper, GitHub)
├── templates/          # Interface Web (HTML)
└── insight_engine.db   # Banco de dados SQLite
```

---

## 🧩 Adicionando Novas Fontes

Você pode adicionar fontes diretamente pela interface web em **Configurações**:
- **RSS**: Insira a URL do feed XML.
- **YouTube**: Use a URL do canal ou página de vídeos.
- **GitHub**: Insira a URL do repositório.
- **Scraper**: Insira qualquer URL de blog ou site de notícias.

---

## 🤝 Contribuição

Sinta-se à vontade para abrir **Issues** ou enviar **Pull Requests**. Adoraríamos ver novos coletores ou melhorias na interface!

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

Desenvolvido com ❤️ para facilitar sua vida digital.
