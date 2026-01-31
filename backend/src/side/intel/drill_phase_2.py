"""
Summit Phase 2 Drill: Scavenging & Sources.
"""

import asyncio
from side.intel.scavengers.mobile import AndroidScavenger
from side.intel.scavengers.docker import DockerScavenger
from side.intel.sources.jira_linear import LinearSource, JiraSource

async def run_phase_2_drill():
    print("🕵️ [PHASE 2]: Deep Scavenging & Enterprise Intent...")
    
    # 1. ANDROID CHECK
    print("\n📱 [TEST 1]: Android Scavenger")
    android = AndroidScavenger()
    devices = android.find_devices()
    print(f"   Devices: {devices}")
    
    log = await android.tail_logcat()
    print(f"   Log Hit: {log['error']}")
    
    if "NullPointer" in log['error']:
        print("✅ PASS: Captured Java Crash.")
    else:
        print("❌ FAIL: Missed Crash.")
        exit(1)

    # 2. DOCKER CHECK
    print("\n🐳 [TEST 2]: Docker Scavenger")
    docker = DockerScavenger()
    containers = await docker.get_running_containers()
    print(f"   Containers: {containers}")
    
    db_log = await docker.scan_logs(containers[0]["id"])
    print(f"   DB Log: {db_log['log']}")
    
    if "duplicate key" in db_log['log']:
        print("✅ PASS: Captured Postgres Error.")
    else:
        print("❌ FAIL: Missed DB Error.")
        exit(1)

    # 3. LINEAR CHECK
    print("\n🎫 [TEST 3]: Linear Intent Source")
    linear = LinearSource(api_key="mock")
    issues = linear.fetch_my_issues()
    print(f"   Issue: {issues[0]['title']}")
    
    if "PulseEngine" in issues[0]['title']:
        print("✅ PASS: Fetched Linear Ticket.")
    else:
        print("❌ FAIL: Linear Sync Failed.")
        exit(1)

    print("\n🏆 PHASE 2 DRILL COMPLETE.")

if __name__ == "__main__":
    asyncio.run(run_phase_2_drill())
