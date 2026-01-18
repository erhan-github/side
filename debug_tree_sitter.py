
try:
    from tree_sitter_languages import get_language, get_parser
    print("Version check:")
    import tree_sitter
    print(f"tree_sitter version: {tree_sitter.__version__ if hasattr(tree_sitter, '__version__') else 'unknown'}")
    
    print("Testing get_language('python')...")
    lang = get_language('python')
    print(f"Got language: {lang}")
    
    print("Testing get_parser('python')...")
    parser = get_parser('python')
    print(f"Got parser: {parser}")
    
    print("Testing get_language('rust')...")
    lang_rs = get_language('rust')
    print(f"Got language: {lang_rs}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
