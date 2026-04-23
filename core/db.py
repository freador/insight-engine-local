import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Table, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, MetaData, select, update, insert, func
from sqlalchemy.exc import IntegrityError

# Configuration - Using SQLite for a lightweight local setup
DB_URL = "sqlite:///insight_engine.db"

metadata = MetaData()

# Tables
sources = Table(
    "sources",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("url", String(500), unique=True, nullable=False),
    Column("type", String(20), nullable=False), # 'RSS', 'YouTube', 'Scraper'
    Column("category", String(50), default="General"),
    Column("item_limit", Integer, default=10), # New limit field
    Column("name", String(100)),
    Column("created_at", DateTime, default=datetime.utcnow),
)

raw_content = Table(
    "raw_content",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("source", String(50), nullable=False),
    Column("title", String(255), nullable=False),
    Column("url", String(500), unique=True, nullable=False),
    Column("content", Text),
    Column("published_at", DateTime),
    Column("created_at", DateTime, default=datetime.utcnow),
)

processed_insights = Table(
    "processed_insights",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("raw_id", Integer, ForeignKey("raw_content.id"), unique=True),
    Column("summary", Text),
    Column("relevance_score", Integer),
    Column("is_read", Boolean, default=False),
    Column("created_at", DateTime, default=datetime.utcnow),
)

engine = create_engine(DB_URL)

def init_db():
    metadata.create_all(engine)
    # Basic migration check for SQLite
    with engine.connect() as conn:
        try:
            conn.execute(select(sources.c.category).limit(1))
        except:
            from sqlalchemy import text
            conn.execute(text("ALTER TABLE sources ADD COLUMN category VARCHAR(50) DEFAULT 'General'"))
            conn.commit()
        
        try:
            conn.execute(select(sources.c.item_limit).limit(1))
        except:
            print("🔧 Migrating database to add 'item_limit' column...")
            from sqlalchemy import text
            conn.execute(text("ALTER TABLE sources ADD COLUMN item_limit INTEGER DEFAULT 10"))
            conn.commit()

def get_sources():
    """Get all configured sources."""
    with engine.connect() as conn:
        query = select(sources)
        return conn.execute(query).fetchall()

def get_sources_with_counts():
    """Get all configured sources with their item counts from raw_content."""
    with engine.connect() as conn:
        all_sources = conn.execute(select(sources)).fetchall()
        results = []
        for s in all_sources:
            s_dict = dict(s._mapping)
            
            # Reconstruct display_name like pipeline.py does
            if s.name:
                display_name = s.name
            elif "@" in s.url: # Capture @Handle for YouTube
                display_name = s.url.split("@")[-1].split('/')[0]
                display_name = f"@{display_name}"
            else:
                display_name = s.url.split('//')[-1].split('/')[0].replace('www.', '')
            
            # Reconstruct source string like collectors do
            if s.type == 'RSS': source_str = display_name
            else: source_str = f"{s.type}: {display_name}"
            
            # Count items in raw_content where source matches exactly
            count_stmt = select(func.count(raw_content.c.id)).where(raw_content.c.source == source_str)
            count = conn.execute(count_stmt).scalar()
            
            # Fallback to URL matching if count is 0 (for old data or inconsistencies)
            if count == 0:
                clean_url = s.url.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
                count_stmt_fallback = select(func.count(raw_content.c.id)).where(raw_content.c.url.like(f"%{clean_url}%"))
                count = conn.execute(count_stmt_fallback).scalar()
            
            s_dict['article_count'] = count
            results.append(s_dict)
        return results

def add_source(url, source_type, category="General", limit=10, name=None):
    """Add a new source."""
    with engine.connect() as conn:
        stmt = insert(sources).values(url=url, type=source_type, category=category, item_limit=limit, name=name)
        try:
            conn.execute(stmt)
            conn.commit()
            return True
        except IntegrityError:
            return False

def update_source(source_id, **kwargs):
    """Update an existing source."""
    with engine.connect() as conn:
        stmt = update(sources).where(sources.c.id == source_id).values(**kwargs)
        conn.execute(stmt)
        conn.commit()

def delete_source(source_id):
    """Remove a source and all its associated content/insights."""
    with engine.connect() as conn:
        # 1. Get the URL of the source to identify its content
        source_query = select(sources.c.url).where(sources.c.id == source_id)
        source_url = conn.execute(source_query).scalar()
        
        if source_url:
            # 2. Delete from processed_insights that link to this source's content
            # We use a subquery to find raw_ids associated with this source URL
            raw_ids_query = select(raw_content.c.id).where(raw_content.c.url.like(f"%{source_url}%"))
            del_insights = processed_insights.delete().where(processed_insights.c.raw_id.in_(raw_ids_query))
            conn.execute(del_insights)
            
            # 3. Delete from raw_content
            del_raw = raw_content.delete().where(raw_content.c.url.like(f"%{source_url}%"))
            conn.execute(del_raw)
            
            # 4. Finally, delete the source itself
            stmt = sources.delete().where(sources.c.id == source_id)
            conn.execute(stmt)
            conn.commit()

def save_raw_content(items):
    """Save raw content items. Skips duplicates based on URL."""
    with engine.connect() as conn:
        for item in items:
            try:
                stmt = raw_content.insert().values(**item)
                conn.execute(stmt)
            except IntegrityError:
                # URL already exists, skip
                continue
        conn.commit()

def get_pending_raw_content():
    """Get raw content that hasn't been processed yet."""
    with engine.connect() as conn:
        query = select(raw_content).where(
            ~select(processed_insights.c.raw_id).where(processed_insights.c.raw_id == raw_content.c.id).exists()
        )
        result = conn.execute(query)
        return result.fetchall()

def save_insight(raw_id, summary, score):
    """Save or update insight for a raw content item."""
    with engine.connect() as conn:
        # Check if insight exists
        check_query = select(processed_insights).where(processed_insights.c.raw_id == raw_id)
        existing = conn.execute(check_query).fetchone()
        
        if existing:
            stmt = update(processed_insights).where(processed_insights.c.raw_id == raw_id).values(
                summary=summary,
                relevance_score=score
            )
        else:
            stmt = processed_insights.insert().values(
                raw_id=raw_id,
                summary=summary,
                relevance_score=score,
                is_read=False
            )
        conn.execute(stmt)
        conn.commit()

def mark_as_read(insight_id):
    """Mark an insight as read."""
    with engine.connect() as conn:
        stmt = update(processed_insights).where(processed_insights.c.id == insight_id).values(is_read=True)
        conn.execute(stmt)
        conn.commit()

def get_dashboard_data():
    """Get processed insights joined with raw content, sorted by score. Limited to 5 days."""
    five_days_ago = datetime.utcnow() - timedelta(days=5)
    with engine.connect() as conn:
        query = select(
            processed_insights.c.id,
            processed_insights.c.summary,
            processed_insights.c.relevance_score,
            processed_insights.c.created_at,
            raw_content.c.title,
            raw_content.c.url,
            raw_content.c.source,
            func.coalesce(raw_content.c.published_at, raw_content.c.created_at).label('published_at')
        ).select_from(
            processed_insights.join(raw_content, processed_insights.c.raw_id == raw_content.c.id)
        ).where(
            processed_insights.c.is_read == False,
            func.coalesce(raw_content.c.published_at, raw_content.c.created_at) >= five_days_ago
        ).order_by(
            processed_insights.c.relevance_score.desc(),
            processed_insights.c.created_at.desc()
        )
        result = conn.execute(query)
        return result.fetchall()

def get_recent_insights(hours=24):
    """Get insights from the last N hours for summarization."""
    since = datetime.utcnow() - timedelta(hours=hours)
    with engine.connect() as conn:
        query = select(
            processed_insights.c.summary,
            raw_content.c.title,
            raw_content.c.url,
            raw_content.c.source,
            raw_content.c.created_at
        ).select_from(
            processed_insights.join(raw_content, processed_insights.c.raw_id == raw_content.c.id)
        ).where(
            processed_insights.c.created_at >= since
        )
        result = conn.execute(query)
        return result.fetchall()
