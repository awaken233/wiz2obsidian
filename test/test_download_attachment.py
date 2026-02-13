import unittest
from unittest.mock import patch

from requests.exceptions import ReadTimeout


class _FakeResponse:
    def __init__(self, *, status_code=200, headers=None, chunks=None, raise_on_iter=None):
        self.status_code = status_code
        self.headers = headers or {}
        self._chunks = list(chunks or [])
        self._raise_on_iter = raise_on_iter

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def iter_content(self, chunk_size=1):
        for chunk in self._chunks:
            yield chunk
        if self._raise_on_iter is not None:
            raise self._raise_on_iter


class TestDownloadAttachment(unittest.TestCase):
    def _make_api(self):
        from sync.wiz_open_api import WizOpenApi

        api = WizOpenApi.__new__(WizOpenApi)
        api.kb_server = "https://example.com"
        api.kb_guid = "kb_guid"
        api.token = "token"
        return api

    @patch("sync.wiz_open_api.requests.get")
    def test_download_attachment_streaming_success(self, mock_get):
        api = self._make_api()

        mock_get.return_value = _FakeResponse(
            status_code=200,
            headers={"Content-Length": "10"},
            chunks=[b"hello", b"world"],
        )

        content = api.download_attachment("doc_guid", "att_guid", att_name="file.bin")
        self.assertEqual(content, b"helloworld")

        self.assertEqual(mock_get.call_count, 1)
        called_url = mock_get.call_args[0][0]
        called_kwargs = mock_get.call_args.kwargs

        self.assertIn("/ks/attachment/download/kb_guid/doc_guid/att_guid", called_url)
        self.assertTrue(called_kwargs.get("stream"))
        self.assertEqual(called_kwargs.get("timeout"), (10, 60))

    @patch("sync.wiz_open_api.requests.get")
    def test_download_attachment_raises_on_http_error_status(self, mock_get):
        api = self._make_api()

        mock_get.return_value = _FakeResponse(status_code=500)

        with self.assertRaises(Exception) as ctx:
            api.download_attachment("doc_guid", "att_guid", att_name="file.bin")

        self.assertIn("下载附件失败", str(ctx.exception))

    @patch("sync.wiz_open_api.requests.get")
    def test_download_attachment_propagates_read_timeout(self, mock_get):
        api = self._make_api()

        mock_get.return_value = _FakeResponse(
            status_code=200,
            headers={"Content-Length": "999"},
            chunks=[b"partial"],
            raise_on_iter=ReadTimeout("read timed out"),
        )

        with self.assertRaises(ReadTimeout):
            api.download_attachment("doc_guid", "att_guid", att_name="file.bin")


if __name__ == "__main__":
    unittest.main()
