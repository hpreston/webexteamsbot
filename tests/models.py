import unittest
from webexteamsbot.models import Response


class ModelTests(unittest.TestCase):
    def test_response_text(self):
        r = Response()
        r.text = "hello"
        self.assertEqual(r.text, "hello")

    def test_response_files(self):
        r = Response()
        r.files = "someurl"
        self.assertEqual(r.files[0], "someurl")

    def test_response_roomid(self):
        r = Response()
        r.roomId = "someid"
        self.assertEqual(r.roomId, "someid")

    def test_response_markdown(self):
        r = Response()
        r.markdown = "**some markdown**"
        self.assertEqual(r.markdown, "**some markdown**")

    def test_response_html(self):
        r = Response()
        r.html = "<h1>some html</h1>"
        self.assertEqual(r.html, "<h1>some html</h1>")

    def test_response_json(self):
        r = Response()
        r.text = "foo"
        self.assertIn("text", r.json())

    def test_response_as_dict(self):
        r = Response()
        r.text = "foo"
        self.assertIn("text", r.as_dict())
