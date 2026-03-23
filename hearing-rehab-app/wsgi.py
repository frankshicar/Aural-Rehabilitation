#!/usr/bin/env python3
"""
WSGI 入口點
用於生產環境部署 (Gunicorn, uWSGI 等)
"""

from app import app

if __name__ == "__main__":
    app.run()