import json
import ollama
import re
from core.db import get_pending_raw_content, save_insight, get_sources

def extract_json(text):
    """Attempt to find and parse a JSON object within a string."""
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return None

# Specialized prompts for different categories
CATEGORY_PROMPTS = {
    "Technology": """
        Focus: New major library releases, technical breakthroughs, deep dives, and architectural insights.
        Penalty: Avoid generic "Top 10" lists or "Introduction to" content. 
        High Score (8-10): Something that changes how I code today.
    """,
    "News": """
        Focus: Brazilian national news and specifically news from SOUTH BRAZIL (Rio Grande do Sul, Santa Catarina, Paraná).
        Anti-Focus: ABSOLUTELY NO gossip, soap operas (novelas), celebrities, or clickbait.
        High Score (8-10): Critical infrastructure, political shifts, or major economic impact in Brazil/South.
    """,
    "Finance": """
        Focus: Market shifts, interest rates (SELIC), new investment instruments, and macroeconomic policy.
        Anti-Focus: Avoid "get rich quick" schemes.
    """,
    "General": """
        Focus: High quality information, verified facts, and educational value.
        Anti-Focus: Clickbait, fofoca, novelas, and low-effort content.
    """
}

def refine_content():
    """Process all pending raw content using Ollama Llama 3 with CATEGORY-SPECIFIC prompts."""
    pending = get_pending_raw_content()
    if not pending:
        return
        
    # Get source categories to match
    db_sources = get_sources()
    source_map = {s.url: s.category for s in db_sources}
    
    print(f"Refining {len(pending)} items with categorical intelligence...")

    for item in pending:
        raw_id = item.id
        title = item.title
        content = item.content or ""
        url = item.url
        category = source_map.get(url, "General")
        
        # Get specialized instructions
        specific_instructions = CATEGORY_PROMPTS.get(category, CATEGORY_PROMPTS["General"])

        prompt = f"""
        You are a Senior Advisor and Expert Researcher. Analyze this content for the '{category}' category.
        
        SPECIAL INSTRUCTIONS FOR THIS CATEGORY:
        {specific_instructions}
        
        TITLE: {title}
        CONTENT: {content[:1500]}

        RESPOND ONLY WITH THIS JSON FORMAT:
        {{
            "summary": "2 direct sentences in Portuguese",
            "score": <0-10 integer>
        }}
        """

        try:
            response = ollama.chat(model='llama3', messages=[
                {'role': 'user', 'content': prompt}
            ])
            
            raw_response = response['message']['content'].strip()
            data = extract_json(raw_response)
            
            if data:
                summary = data.get("summary", "Resumo não gerado.")
                score = data.get("score", 0)
                save_insight(raw_id, summary, score)
                print(f"✅ [{category}] [{score}/10] {title[:60]}...")
            else:
                print(f"⚠️ Fail parse: {title[:30]}")
                save_insight(raw_id, f"Falha no processamento. Resposta bruta: {raw_response[:50]}...", 1)
            
        except Exception as e:
            print(f"❌ Error: {title[:30]}: {e}")

if __name__ == "__main__":
    refine_content()
