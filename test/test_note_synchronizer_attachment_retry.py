import unittest
from unittest.mock import MagicMock, patch

from requests.exceptions import ReadTimeout


class TestNoteSynchronizerAttachmentRetry(unittest.TestCase):
    def _make_synchronizer(self):
        from sync.note_synchronizer import NoteSynchronizer

        api_client = MagicMock()
        db = MagicMock()
        return NoteSynchronizer(api_client=api_client, db=db)

    @patch("sync.note_synchronizer.FileManager.download_attachment_from_byte")
    def test_normal_attachment_retries_then_succeeds(self, mock_save):
        syncer = self._make_synchronizer()

        syncer.api_client.get_note_attachments.return_value = [
            {"attGuid": "att1", "name": "a.bin"}
        ]
        syncer.api_client.download_attachment.side_effect = [
            Exception("net1"),
            Exception("net2"),
            b"data",
        ]

        from sync.parsed_note import ParsedNote

        record = {"doc_guid": "doc1", "category": "/cat/"}
        parsed_note = ParsedNote("hello", [])

        fail_reason = syncer._process_normal_note_attachments(record, parsed_note)

        self.assertIsNone(fail_reason)
        self.assertEqual(syncer.api_client.download_attachment.call_count, 3)
        mock_save.assert_called_once()
        self.assertIn("## 附件", parsed_note.content)

    @patch("sync.note_synchronizer.FileManager.download_attachment_from_byte")
    def test_normal_attachment_fails_after_retries(self, mock_save):
        syncer = self._make_synchronizer()

        syncer.api_client.get_note_attachments.return_value = [
            {"attGuid": "att1", "name": "a.bin"}
        ]
        syncer.api_client.download_attachment.side_effect = ReadTimeout("read timed out")

        from sync.parsed_note import ParsedNote

        record = {"doc_guid": "doc1", "category": "/cat/"}
        parsed_note = ParsedNote("hello", [])

        fail_reason = syncer._process_normal_note_attachments(record, parsed_note)

        self.assertIsNotNone(fail_reason)
        self.assertIn("普通笔记附件下载失败", fail_reason)
        self.assertEqual(syncer.api_client.download_attachment.call_count, 3)
        mock_save.assert_not_called()

    @patch("sync.note_synchronizer.FileManager.download_attachment_from_byte")
    def test_collaboration_attachment_fails_after_retries(self, mock_save):
        syncer = self._make_synchronizer()

        syncer.api_client.get_collaboration_token.return_value = "token"
        syncer.api_client.get_collaboration_image_byte.side_effect = ReadTimeout("read timed out")

        from sync.parsed_note import ParsedNote

        record = {"doc_guid": "doc1", "category": "/cat/"}
        parsed_note = ParsedNote("[x](wiz-collab-attachment://a.bin)", [])

        fail_reason = syncer._process_collaboration_note_attachments(record, parsed_note)

        self.assertIsNotNone(fail_reason)
        self.assertIn("协作笔记附件下载失败", fail_reason)
        self.assertEqual(syncer.api_client.get_collaboration_image_byte.call_count, 3)
        mock_save.assert_not_called()

    @patch("sync.note_synchronizer.FileManager.save_md_to_file")
    @patch("sync.note_synchronizer.NoteProperty.from_sync_record")
    @patch("sync.note_synchronizer.NoteParserFactory.create_parser")
    def test_sync_single_note_marks_failed_when_attachments_failed(
        self,
        mock_create_parser,
        mock_note_prop,
        mock_save_md,
    ):
        syncer = self._make_synchronizer()

        class _FakeParsed:
            def __init__(self):
                self.content = "body"
                self.need_upload_images = []

            def replace_image_url(self, _):
                return

        fake_parser = MagicMock()
        fake_parser.process_content.return_value = _FakeParsed()
        mock_create_parser.return_value = fake_parser

        mock_note_prop.return_value.to_string.return_value = ""

        syncer._get_note_origin_content = MagicMock(return_value="origin")
        syncer._save_img_and_get_url = MagicMock(return_value={})
        syncer._process_note_attachment = MagicMock(return_value="附件下载失败: a.bin")

        record = {
            "doc_guid": "doc1",
            "title": "t",
            "type": "lite/markdown",
            "category": "/cat/",
        }

        syncer._sync_single_note_to_local(record)

        syncer.db.update_note_sync_status.assert_called_with(
            "doc1",
            sync_status=False,
            fail_reason="附件下载失败: a.bin",
        )
        mock_save_md.assert_called_once()

    @patch("sync.note_synchronizer.FileManager.save_md_to_file")
    @patch("sync.note_synchronizer.NoteProperty.from_sync_record")
    @patch("sync.note_synchronizer.NoteParserFactory.create_parser")
    def test_sync_single_note_marks_success_when_no_attachment_failures(
        self,
        mock_create_parser,
        mock_note_prop,
        mock_save_md,
    ):
        syncer = self._make_synchronizer()

        class _FakeParsed:
            def __init__(self):
                self.content = "body"
                self.need_upload_images = []

            def replace_image_url(self, _):
                return

        fake_parser = MagicMock()
        fake_parser.process_content.return_value = _FakeParsed()
        mock_create_parser.return_value = fake_parser

        mock_note_prop.return_value.to_string.return_value = ""

        syncer._get_note_origin_content = MagicMock(return_value="origin")
        syncer._save_img_and_get_url = MagicMock(return_value={})
        syncer._process_note_attachment = MagicMock(return_value=None)

        record = {
            "doc_guid": "doc1",
            "title": "t",
            "type": "lite/markdown",
            "category": "/cat/",
        }

        syncer._sync_single_note_to_local(record)

        syncer.db.update_note_sync_status.assert_called_with(
            "doc1",
            sync_status=True,
            fail_reason="",
        )
        mock_save_md.assert_called_once()


if __name__ == "__main__":
    unittest.main()
