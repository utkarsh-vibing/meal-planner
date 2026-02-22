import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from app.api import routes
from app.config import get_settings
from app.db import init_db


class MealMindHandler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict | list) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:  # noqa: N802
        settings = get_settings()
        path = self.path
        parsed = urlparse(path)

        if parsed.path == f"{settings.api_prefix}/health":
            code, payload = routes.health()
            return self._send(code, payload)

        if parsed.path == f"{settings.api_prefix}/meals":
            qs = parse_qs(parsed.query)
            user_id = int(qs.get("user_id", [0])[0])
            code, payload = routes.list_meals(user_id)
            return self._send(code, payload)

        if parsed.path.startswith(f"{settings.api_prefix}/meal-plan/"):
            week_start = parsed.path.split("/")[-1]
            qs = parse_qs(parsed.query)
            user_id = int(qs.get("user_id", [0])[0])
            code, payload = routes.get_plan(user_id, week_start)
            return self._send(code, payload)

        return self._send(404, {"detail": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        settings = get_settings()
        parsed = urlparse(self.path)
        payload = self._body()

        if parsed.path == f"{settings.api_prefix}/users":
            return self._send(*routes.create_user(payload))
        if parsed.path == f"{settings.api_prefix}/meals":
            return self._send(*routes.create_meal(payload))
        if parsed.path == f"{settings.api_prefix}/meal-plan/generate":
            return self._send(*routes.create_plan(payload))
        if parsed.path == f"{settings.api_prefix}/grocery-list":
            return self._send(*routes.grocery_list(payload))

        return self._send(404, {"detail": "Not found"})

    def do_PATCH(self) -> None:  # noqa: N802
        settings = get_settings()
        parsed = urlparse(self.path)
        payload = self._body()

        if parsed.path == f"{settings.api_prefix}/meal-plan/slot":
            return self._send(*routes.update_slot(payload))

        return self._send(404, {"detail": "Not found"})


def run() -> None:
    init_db()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), MealMindHandler)
    print("MealMind API running on http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    run()
