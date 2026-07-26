"""Test cases for the logger module."""

import logging
import os
import tempfile
import unittest

import concurrent_log_handler

from core_tools import logger


class TestCreateLogger(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = "test.log"
        self.log_path = os.path.join(self.temp_dir, self.log_file)

    def tearDown(self):
        for name in list(logging.Logger.manager.loggerDict.keys()):
            log = logging.getLogger(name)
            log.handlers.clear()
        for f in os.listdir(self.temp_dir):
            try:
                os.remove(os.path.join(self.temp_dir, f))
            except OSError:
                pass

    def test_returns_logger_instance(self):
        result = logger.create_logger("test_instance", self.log_file, output_dir=self.temp_dir)
        self.assertIsInstance(result, logging.Logger)

    def test_logger_name(self):
        result = logger.create_logger("my_logger", self.log_file, output_dir=self.temp_dir)
        self.assertEqual(result.name, "my_logger")

    def test_default_level_is_info(self):
        result = logger.create_logger("test_level_default", self.log_file, output_dir=self.temp_dir)
        self.assertEqual(result.level, logging.INFO)

    def test_custom_level(self):
        result = logger.create_logger("test_level_debug", self.log_file, level=logging.DEBUG, output_dir=self.temp_dir)
        self.assertEqual(result.level, logging.DEBUG)

    def test_handler_is_added(self):
        result = logger.create_logger("test_handler", self.log_file, output_dir=self.temp_dir)
        self.assertGreater(len(result.handlers), 0)

    def test_handler_level_matches(self):
        result = logger.create_logger("test_handler_level", self.log_file, level=logging.WARNING, output_dir=self.temp_dir)
        self.assertEqual(result.handlers[0].level, logging.WARNING)

    def test_log_file_created(self):
        result = logger.create_logger("test_file_created", self.log_file, output_dir=self.temp_dir)
        result.info("test message")
        self.assertTrue(os.path.exists(self.log_path))

    def test_message_written_to_file(self):
        result = logger.create_logger("test_file_write", self.log_file, output_dir=self.temp_dir)
        result.info("hello from test")
        result.handlers[0].flush()
        with open(self.log_path, "r") as f:
            content = f.read()
        self.assertIn("hello from test", content)

    def test_warning_not_written_at_info_level_below(self):
        result = logger.create_logger("test_level_filter", self.log_file, level=logging.WARNING, output_dir=self.temp_dir)
        result.info("should not appear")
        result.handlers[0].flush()
        if os.path.exists(self.log_path):
            with open(self.log_path, "r") as f:
                content = f.read()
            self.assertNotIn("should not appear", content)

    def test_custom_max_size_accepted(self):
        result = logger.create_logger("test_max_size", self.log_file, max_size=1000, output_dir=self.temp_dir)
        self.assertIsNotNone(result)

    def test_custom_log_versions_accepted(self):
        result = logger.create_logger("test_versions", self.log_file, log_versions=3, output_dir=self.temp_dir)
        self.assertIsNotNone(result)

    def test_handler_is_concurrent_rotating(self):
        result = logger.create_logger("test_handler_type", self.log_file, output_dir=self.temp_dir)
        self.assertIsInstance(result.handlers[0], concurrent_log_handler.ConcurrentRotatingFileHandler)

    def test_multiple_loggers_independent(self):
        logger_a = logger.create_logger("logger_a", "a.log", output_dir=self.temp_dir)
        logger_b = logger.create_logger("logger_b", "b.log", output_dir=self.temp_dir)
        self.assertIsNot(logger_a, logger_b)
        self.assertEqual(logger_a.name, "logger_a")
        self.assertEqual(logger_b.name, "logger_b")


if __name__ == "__main__":
    unittest.main()