import json
from pathlib import Path

from flask import url_for


class ViteAssets:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.static_url_path = app.static_url_path
        self.manifest_path = (
            Path(app.static_folder) / "dist" / ".vite" / "manifest.json"
        )
        self.dev_server_url = "http://localhost:5173"

        # 開発モードかどうかを判定
        self.dev_mode = app.config.get("FLASK_ENV") == "development"

        # マニフェストの読み込み
        self.manifest = {}
        if not self.dev_mode and self.manifest_path.exists():
            with open(self.manifest_path) as f:
                self.manifest = json.load(f)

    def get_script_tag(self):
        if self.dev_mode:
            return (
                f'<script type="module" src="{self.dev_server_url}/@vite/client"></script>'
                f'<script type="module" src="{self.dev_server_url}/src/main.jsx"></script>'
            )
        else:
            entry_file = self.manifest.get("src/main.jsx", {})
            return f'<script type="module" src="{url_for("static", filename=f"dist/{entry_file.get("file")}")}"></script>'
