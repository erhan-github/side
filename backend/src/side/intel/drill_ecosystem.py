"""
Ecosystem Drill: Simulating Third-Party Clients.
"""

import asyncio
from side.intel.ecosystem.jetbrains import jetbrains_bridge

async def run_ecosystem_drill():
    print("🔌 [ECO DRILL]: Connecting Mock JetBrains Plugin...")
    
    # 1. Handshake
    response = jetbrains_bridge.handshake(version="1.0.0-Beta")
    print(f"   Handshake: {response}")
    
    if response["status"] != "CONNECTED":
        print("❌ FAIL: Handshake rejected.")
        exit(1)
        
    # 2. Context Push
    print("\n📦 [ECO DRILL]: Pushing Context (Java/Kotlin Payload)...")
    payload = {
        "projectPath": "/Users/me/IdeaProjects/SidelithJava",
        "filePath": "/src/main/java/Main.java",
        "caretOffset": 120,
        "selectionStart": 100,
        "selectionEnd": 120,
        "contentSnippet": "public static void main(String[] args)",
        "pluginVersion": "1.0.0-Beta"
    }
    
    ack = jetbrains_bridge.receive_context_update(payload)
    print(f"   Server Response: {ack}")
    
    if ack != "ACK":
        print("❌ FAIL: Context rejected.")
        exit(1)
        
    # 3. Verify State
    status = jetbrains_bridge.get_status()
    print(f"   Bridge Status: {status}")
    
    if status["last_file"] == "/src/main/java/Main.java":
        print("✅ PASS: JetBrains Bridge is Operational.")
    else:
        print("❌ FAIL: State mismatch.")
        exit(1)

    print("\n🏆 ECOSYSTEM DRILL COMPLETE.")

if __name__ == "__main__":
    asyncio.run(run_ecosystem_drill())
