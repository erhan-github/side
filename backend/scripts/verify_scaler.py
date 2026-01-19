import os
import sys
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from side.audit.experts.performance import PerformanceLead
from side.audit.experts.base import ExpertContext
from side.audit.core import AuditStatus
from side.server import load_env_file

# Setup
logging.basicConfig(level=logging.ERROR)
load_env_file()

def verify_scaler():
    print("🚀 Initializing The Scaler (Performance Lead)...")
    expert = PerformanceLead()
    
    # 1. Test Case: N+1 Query (Django/ORM style)
    n_plus_1_code = """
def get_feed(user_id):
    users = User.objects.all() # Fetch all users
    feed = []
    
    for user in users:
        # N+1 Problem: Querying profile inside the loop
        profile = Profile.objects.get(user_id=user.id)
        posts = Post.objects.filter(author=profile) # Another query!
        feed.extend(posts)
        
    return feed
"""
    
    print("\n⚡ Analyzing 'N+1 Query' Snippet...")
    ctx_bad = ExpertContext(
        check_id="PERF-001",
        file_path="src/api/feed.py",
        content_snippet=n_plus_1_code,
        language="python"
    )
    
    result_bad = expert.review(ctx_bad)
    
    print(f"\n[RESULT] Status: {result_bad.status}")
    print(f"[RESULT] Notes: {result_bad.notes}")
    
    if result_bad.status == AuditStatus.FAIL:
        print("✅ SUCCESS: The Scaler caught the N+1 query.")
    else:
        print(f"❌ FAILURE: The Scaler missed it. Status: {result_bad.status}")

    # 2. Test Case: Efficient Bulk Fetch
    efficient_code = """
def get_feed_efficient(user_id):
    # Optimized: Fetch specific user with related data
    # Uses select_related to avoid N+1
    try:
        user = User.objects.select_related('profile').get(id=user_id)
    except User.DoesNotExist:
        return []
    
    # Efficiently fetch recent posts only (Pagination)
    posts = user.profile.posts.all().order_by('-created_at')[:20]
        
    return list(posts)
"""
    
    print("\n⚡ Analyzing 'Efficient Code' Snippet...")
    ctx_good = ExpertContext(
        check_id="PERF-002",
        file_path="src/api/feed.py",
        content_snippet=efficient_code,
        language="python"
    )
    
    result_good = expert.review(ctx_good)
    
    print(f"\n[RESULT] Status: {result_good.status}")
    print(f"[RESULT] Notes: {result_good.notes}")
    
    if result_good.status == AuditStatus.PASS:
        print("✅ SUCCESS: The Scaler liked the efficient code.")
    else:
        print(f"❌ FAILURE: The Scaler complained about efficient code: {result_good.status}")

if __name__ == "__main__":
    verify_scaler()
