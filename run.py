import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # macOS reserves port 5000 for AirPlay Receiver, so we default to 5001.
    port = int(os.getenv("PORT", "5001"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    print(f"\n  Resume Parser running at  http://127.0.0.1:{port}\n")
    app.run(host="127.0.0.1", port=port, debug=debug, use_reloader=False)
