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


class HealthTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 8011), MealMindHandler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_health(self):
        with request.urlopen("http://127.0.0.1:8011/api/v1/health") as resp:  # nosec B310
            self.assertEqual(resp.status, 200)
            payload = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(payload, {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
