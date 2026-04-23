import ollama
from core.db import get_recent_insights, get_sources

def generate_daily_summary():
    """Fetches recent insights and generates a structured daily summary."""
    
    # 1. Get recent insights (last 24h)
    insights = get_recent_insights(hours=24)
    if not insights:
        return {
            "global": "Nenhuma novidade relevante nas últimas 24 horas.",
            "categories": {}
        }

    # 2. Map insights to categories
    db_sources = get_sources()
    official_map = {s.url: s.category for s in db_sources}
    
    categorized_data = {}
    for item in insights:
        row = dict(item._mapping)
        category = "General"
        
        # Match category by URL
        for url, cat in official_map.items():
            if url in row['url']:
                category = cat
                break
        
        if category not in categorized_data:
            categorized_data[category] = []
        
        categorized_data[category].append(f"- {row['title']}: {row['summary']}")

    # 3. Generate summaries per category
    category_summaries = {}
    all_summaries_text = ""
    
    for category, items in categorized_data.items():
        items_text = "\n".join(items[:20]) # Increased limit
        prompt = f"""
        Você é um Analista de Inteligência Sênior especializado na categoria '{category}'. 
        Abaixo estão os eventos e notícias mais relevantes das últimas 24 horas.
        
        Sua tarefa é criar um RELATÓRIO ANALÍTICO em português que:
        1. Identifique os TEMAS CENTRAIS e tendências do dia.
        2. Explique as IMPLICAÇÕES dessas notícias (por que isso importa?).
        3. Use bullet points ricos em informações, não apenas frases curtas.
        4. Se houver conexões entre notícias diferentes, destaque-as.

        DADOS BRUTOS:
        {items_text}

        RELATÓRIO ANALÍTICO (EM PORTUGUÊS):
        """
        
        try:
            response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
            summary = response['message']['content'].strip()
            category_summaries[category] = summary
            all_summaries_text += f"\n--- CATEGORIA: {category} ---\n{summary}\n"
        except Exception as e:
            category_summaries[category] = f"Erro ao gerar resumo: {str(e)}"

    # 4. Generate Global Summary
    global_prompt = f"""
    Você é um Estrategista-Chefe. Com base nos relatórios categoriais abaixo, crie uma SÍNTESE EXECUTIVA GLOBAL do dia.
    
    ESTRUTURA DO SEU RELATÓRIO:
    - PANORAMA GERAL: Um parágrafo analítico sobre o "clima" das notícias hoje.
    - TOP 3 INSIGHTS CRÍTICOS: Identifique os 3 pontos mais cruciais que exigem atenção imediata ou que definem o dia.
    - CONEXÃO ENTRE SETORES: Existe algo que une as diferentes categorias hoje?

    RELATÓRIOS POR CATEGORIA:
    {all_summaries_text}
    
    SÍNTESE EXECUTIVA GLOBAL (EM PORTUGUÊS):
    """
    
    try:
        response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': global_prompt}])
        global_summary = response['message']['content'].strip()
    except Exception as e:
        global_summary = f"Erro ao gerar destaque global: {str(e)}"

    return {
        "global": global_summary,
        "categories": category_summaries
    }

if __name__ == "__main__":
    print(generate_daily_summary())
