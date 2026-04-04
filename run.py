import os
from flask import Flask
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Default port to 5000, host on 0.0.0.0
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
