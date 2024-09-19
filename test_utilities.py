import utilities
import unittest
import os
import tempfile



class TestUtilities(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        self.edl_file = os.path.join(self.test_dir.name, "test.edl")
        self.subtitle_file = os.path.join(self.test_dir.name, "test.srt")
        self.media_file = os.path.join(self.test_dir.name, "test.mp4")

        # Create a sample EDL file
        with open(self.edl_file, "w") as f:
            f.write("# mpv EDL v0\n")
            f.write(f"{self.media_file},0,10\n")

        # Create a sample subtitle file
        with open(self.subtitle_file, "w") as f:
            f.write("1\n00:00:00,000 --> 00:00:10,000\nHello World\n")

        # Create a sample media file
        with open(self.media_file, "w") as f:
            f.write("dummy content")

    def tearDown(self):
        # Cleanup the temporary directory
        self.test_dir.cleanup()

    def test_logmessage(self):
        utilities.logmessage("Test log message")
        with open(utilities.LOG_FILE, "r") as log_file:
            logs = log_file.read()
            self.assertIn("Test log message", logs)

    def test_message(self):
        with self.assertLogs(level='INFO') as log:
            utilities.message("Test message")
            self.assertIn("Test message", log.output[0])

    def test_shuffle_edl(self):
        result = utilities.shuffle_edl(self.edl_file, shuffle_num=1, shuffle_restore="N")
        self.assertIsNone(result)

    def test_get_subtitle_related_media(self):
        result = utilities.get_subtitle_related_media(self.subtitle_file)
        self.assertEqual(result, self.media_file)

    def test_get_random_subtitles(self):
        # This test is limited due to the dependency on external environment
        result = utilities.get_random_subtitles("Hello")
        self.assertIsInstance(result, str)

    def test_get_random_edl_content(self):
        # This test is limited due to the dependency on external environment
        result = utilities.get_random_edl_content("test")
        self.assertIsInstance(result, str)

    def test_get_random_edl_file(self):
        # This test is limited due to the dependency on external environment
        result = utilities.get_random_edl_file("test")
        self.assertIsInstance(result, str)

    def test_get_random_video(self):
        # This test is limited due to the dependency on external environment
        result = utilities.get_random_video()
        self.assertIsInstance(result, str)

    def test_get_length(self):
        result = utilities.get_length(self.media_file)
        self.assertEqual(result, "0")

    def test_minimum_length(self):
        result = utilities.minimum_length(self.media_file, min_length=0)
        self.assertTrue(result)

    def test_validate_edl(self):
        result = utilities.validate_edl(self.edl_file)
        self.assertEqual(result, 0)

    def test_convert_edl_file_content(self):
        player_file = os.path.join(self.test_dir.name, "player_file.sh")
        utilities.convert_edl_file_content(self.edl_file, player_file)
        with open(player_file, "r") as pf:
            content = pf.read()
            self.assertIn("--start=0 --length=10", content)

    def test_convert_edl_file(self):
        player_file = os.path.join(self.test_dir.name, "player_file.sh")
        utilities.convert_edl_file(self.edl_file, player_file=player_file, screen=0, profile=None)
        with open(player_file, "r") as pf:
            content = pf.read()
            self.assertIn("nohup mpv --screen=0 \\", content)

if __name__ == '__main__':
    unittest.main()
