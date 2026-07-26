import unittest

from core_tools import file_management
from core_tools import object_management


class TestApiCompatibility(unittest.TestCase):
    def test_file_management_aliases(self):
        self.assertEqual(file_management.get_json_dict.__defaults__, file_management.getJsonDict.__defaults__)
        self.assertTrue(callable(file_management.update_json_file))
        self.assertTrue(callable(file_management.archive_files))

    def test_object_management_alias_outputs(self):
        self.assertEqual(object_management.make_text_json("abc{test}"), object_management.makeTextJson("abc{test}"))
        self.assertEqual(object_management.list_to_csv(("a", "b")), object_management.list2csv(("a", "b")))
        wrapped = object_management.large_sentence_display("x" * 20, max_length=5)
        legacy_wrapped = object_management.largeSentenceDisplay("x" * 20, maxLength=5)
        self.assertEqual(wrapped, legacy_wrapped)
        self.assertEqual(
            object_management.execute_function_in_string("hello"),
            object_management.executeFunctionInString("hello"),
        )


if __name__ == "__main__":
    unittest.main()