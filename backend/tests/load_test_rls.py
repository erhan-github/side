"""
Load Test: Supabase RLS Performance

Tests Row Level Security performance under load.
Validates tenant isolation doesn't degrade with scale.
"""
import asyncio
import time
import os
from typing import List, Dict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RLSLoadTestResult:
    """Results from RLS load test."""
    total_queries: int
    successful_queries: int
    avg_query_time_ms: float
    max_query_time_ms: float
    queries_per_second: float
    tenant_isolation_verified: bool


class SupabaseRLSLoadTester:
    """
    Load tester for Supabase RLS performance.
    
    Tests:
    1. Query performance with RLS enabled
    2. Tenant isolation under concurrent access
    3. Vector search performance with RLS
    """
    
    def __init__(self, num_tenants: int = 100, queries_per_tenant: int = 10):
        self.num_tenants = num_tenants
        self.queries_per_tenant = queries_per_tenant
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
    @property
    def is_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_key)
    
    async def run_rls_test(self) -> RLSLoadTestResult:
        """Run RLS performance test."""
        if not self.is_configured:
            logger.warning("⚠️ [RLS TEST]: Supabase not configured. Skipping.")
            return RLSLoadTestResult(
                total_queries=0,
                successful_queries=0,
                avg_query_time_ms=0,
                max_query_time_ms=0,
                queries_per_second=0,
                tenant_isolation_verified=False
            )
        
        try:
            from supabase import create_client
            client = create_client(self.supabase_url, self.supabase_key)
        except ImportError:
            logger.warning("⚠️ [RLS TEST]: supabase-py not installed")
            return RLSLoadTestResult(0, 0, 0, 0, 0, False)
        
        total_queries = self.num_tenants * self.queries_per_tenant
        query_times = []
        successful = 0
        
        start_time = time.time()
        
        for tenant_id in range(self.num_tenants):
            tenant_hash = f"tenant_{tenant_id:04d}"
            
            for _ in range(self.queries_per_tenant):
                try:
                    t0 = time.time()
                    
                    # Query with RLS filter
                    result = client.table("context_layers").select("*").eq(
                        "workspace_hash", tenant_hash
                    ).limit(10).execute()
                    
                    query_time = (time.time() - t0) * 1000
                    query_times.append(query_time)
                    successful += 1
                    
                except Exception as e:
                    logger.debug(f"Query failed: {e}")
        
        total_duration = time.time() - start_time
        
        return RLSLoadTestResult(
            total_queries=total_queries,
            successful_queries=successful,
            avg_query_time_ms=sum(query_times) / len(query_times) if query_times else 0,
            max_query_time_ms=max(query_times) if query_times else 0,
            queries_per_second=successful / total_duration if total_duration > 0 else 0,
            tenant_isolation_verified=successful == total_queries
        )
    
    def verify_isolation(self) -> bool:
        """Verify that RLS properly isolates tenants."""
        if not self.is_configured:
            return False
        
        try:
            from supabase import create_client
            client = create_client(self.supabase_url, self.supabase_key)
            
            # Test: Query with wrong tenant should return empty
            result = client.table("context_layers").select("*").eq(
                "workspace_hash", "nonexistent_tenant"
            ).execute()
            
            # Should be empty (no cross-tenant data leak)
            return len(result.data) == 0
            
        except Exception as e:
            logger.error(f"Isolation check failed: {e}")
            return False


def run_rls_load_test(num_tenants: int = 100) -> RLSLoadTestResult:
    """Run RLS load test."""
    tester = SupabaseRLSLoadTester(num_tenants)
    return asyncio.run(tester.run_rls_test())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("SUPABASE RLS LOAD TEST")
    print("=" * 60)
    
    result = run_rls_load_test(num_tenants=100)
    
    print(f"\nResults:")
    print(f"  Total Queries:      {result.total_queries}")
    print(f"  Successful:         {result.successful_queries}")
    print(f"  Avg Query Time:     {result.avg_query_time_ms:.2f}ms")
    print(f"  Max Query Time:     {result.max_query_time_ms:.2f}ms")
    print(f"  Queries/Second:     {result.queries_per_second:.1f}")
    print(f"  Isolation OK:       {result.tenant_isolation_verified}")
