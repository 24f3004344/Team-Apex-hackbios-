"""AarogyaSahay entrypoint. Run from the lakshya/ directory:  python run.py"""
import os
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"Starting AarogyaSahay Health Grid on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=False)
