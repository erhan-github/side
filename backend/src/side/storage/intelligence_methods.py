
    # ═══════════════════════════════════════════════════════════════════
    # INTELLIGENCE SIGNALS (Strategic Curation)
    # ═══════════════════════════════════════════════════════════════════
    
    def save_intelligence_signal(
        self,
        signal_id: str,
        title: str,
        url: str,
        source: str,
        domain: str,
        score: int,
        keywords: list[str],
        summary: str = None,
        published_at: str = None,
        retention_days: int = 30
    ) -> None:
        """
        Save a high-quality intelligence signal (Top 10 only).
        
        Args:
            signal_id: Unique identifier
            title: Article/paper title
            url: Source URL
            source: 'arxiv', 'hn', 'github', etc.
            domain: 'ai', 'devtool', 'saas', etc.
            score: LLM relevance score (0-100)
            keywords: Extracted keywords
            summary: Optional summary
            published_at: Publication timestamp
            retention_days: Days to keep (default 30)
        """
        import json
        from datetime import timedelta
        
        expires_at = (datetime.now(timezone.utc) + timedelta(days=retention_days)).isoformat()
        
        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO intelligence_signals 
                (id, title, url, source, domain, score, keywords, summary, published_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (signal_id, title, url, source, domain, score, json.dumps(keywords), 
                 summary, published_at, expires_at)
            )
    
    def get_top_signals(
        self,
        domain: str = None,
        keywords: list[str] = None,
        min_score: int = 70,
        limit: int = 10,
        days: int = 7
    ) -> list[dict[str, Any]]:
        """
        Retrieve top intelligence signals for RAG context.
        
        Args:
            domain: Filter by domain ('ai', 'devtool', etc.)
            keywords: Filter by keywords
            min_score: Minimum relevance score
            limit: Max results
            days: Only signals from last N days
        
        Returns:
            List of signal dicts
        """
        import json
        from datetime import timedelta
        
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        query = """
            SELECT id, title, url, source, domain, score, keywords, summary, published_at
            FROM intelligence_signals
            WHERE fetched_at >= ? AND score >= ?
        """
        params = [cutoff, min_score]
        
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        
        query += " ORDER BY score DESC, published_at DESC LIMIT ?"
        params.append(limit)
        
        with self._connection() as conn:
            rows = conn.execute(query, params).fetchall()
            
            signals = []
            for row in rows:
                signal = {
                    "id": row[0],
                    "title": row[1],
                    "url": row[2],
                    "source": row[3],
                    "domain": row[4],
                    "score": row[5],
                    "keywords": json.loads(row[6]) if row[6] else [],
                    "summary": row[7],
                    "published_at": row[8],
                }
                
                # Filter by keywords if provided
                if keywords:
                    if any(kw.lower() in ' '.join(signal['keywords']).lower() for kw in keywords):
                        signals.append(signal)
                else:
                    signals.append(signal)
            
            return signals[:limit]
    
    def get_signal_stats(self) -> dict[str, Any]:
        """Get intelligence signal statistics."""
        with self._connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM intelligence_signals").fetchone()[0]
            
            by_source = {}
            rows = conn.execute(
                "SELECT source, COUNT(*) FROM intelligence_signals GROUP BY source"
            ).fetchall()
            for source, count in rows:
                by_source[source] = count
            
            by_domain = {}
            rows = conn.execute(
                "SELECT domain, COUNT(*) FROM intelligence_signals GROUP BY domain"
            ).fetchall()
            for domain, count in rows:
                by_domain[domain] = count
            
            avg_score = conn.execute(
                "SELECT AVG(score) FROM intelligence_signals"
            ).fetchone()[0] or 0
            
            return {
                "total_signals": total,
                "by_source": by_source,
                "by_domain": by_domain,
                "avg_score": round(avg_score, 1)
            }
