#!/usr/bin/env python
import sys
import traceback

print("Starting app...", file=sys.stderr, flush=True)

try:
    print("Importing modules...", file=sys.stderr, flush=True)
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    print("Loading app module...", file=sys.stderr, flush=True)
    from app import app
    
    print("Launching Gradio app...", file=sys.stderr, flush=True)
    sys.stderr.flush()
    sys.stdout.flush()
    
    app.launch(
        server_name="127.0.0.1",
        server_port=7862,
        show_error=True,
        quiet=False
    )
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
