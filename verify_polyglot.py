
import asyncio
import logging
from pathlib import Path
from cso_ai.intel.technical import TechnicalAnalyzer

# Configure logging to see debug output
logging.basicConfig(level=logging.DEBUG)

async def verify():
    analyzer = TechnicalAnalyzer()
    root = Path("/Users/erhanerdogan/Desktop/CSO_ai/cso-ai/tests")
    
    print(f"Analyzing {root}...")
    intel = await analyzer.analyze(root)
    
    print(f"Languages detected: {intel.languages}")
    print(f"Code Graph Size: {len(intel.code_graph)}")
    
    found_ts_class = False
    found_rs_struct = False
    
    for key, node in intel.code_graph.items():
        print(f"Found Node: {node.name} ({node.type}) in {node.file_path}")
        if "UserManager" in node.name and "class" in node.type:
            found_ts_class = True
        if "Order" in node.name: # Structs might be mapped to 'class' or 'struct' depending on my mapping logic
             found_rs_struct = True

    if found_ts_class:
        print("✅ TypeScript AST Verified: Found 'UserManager'")
    else:
        print("❌ TypeScript AST Failed: 'UserManager' not found")

    if found_rs_struct:
         print("✅ Rust AST Verified: Found 'Order'")
    else:
         print("❌ Rust AST Failed: 'Order' not found")

if __name__ == "__main__":
    asyncio.run(verify())
