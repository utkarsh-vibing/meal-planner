import json
import os
import tempfile
import unittest
from urllib import request

os.environ["MEALMIND_DATABASE_PATH"] = tempfile.NamedTemporaryFile(delete=False).name

from app.db import init_db  # noqa: E402
from app.main import MealMindHandler  # noqa: E402
from http.server import ThreadingHTTPServer  # noqa: E402
from threading import Thread  # noqa: E402


class ApiFlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 8010), MealMindHandler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def _post(self, path: str, payload: dict, method: str = "POST"):
        req = request.Request(
            f"http://127.0.0.1:8010{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method=method,
        )
        with request.urlopen(req) as resp:  # nosec B310
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def test_flow(self):
        status, user = self._post("/api/v1/users", {"name": "Asha"})
        self.assertEqual(status, 200)

        status, _meal = self._post(
            "/api/v1/meals",
            {
                "user_id": user["id"],
                "name": "Paneer Bowl",
                "ingredients": [
                    {"ingredient_name": "paneer", "quantity": 2, "unit": "cup", "category": "proteins"},
                    {"ingredient_name": "onion", "quantity": 1, "unit": "unit", "category": "produce"},
                ],
            },
        )
        self.assertEqual(status, 200)

        status, plan = self._post(
            "/api/v1/meal-plan/generate", {"user_id": user["id"], "week_start_date": "2026-02-16"}
        )
        self.assertEqual(status, 200)
        self.assertEqual(plan["week_start_date"], "2026-02-16")

        status, grocery = self._post("/api/v1/grocery-list", {"user_id": user["id"], "scope": "this_week"})
        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(grocery["items"]), 2)


if __name__ == "__main__":
    unittest.main()
