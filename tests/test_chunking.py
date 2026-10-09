import unittest
from helpdesk.chunking import chunk_text


class TestChunkText(unittest.TestCase):

    def test_basic_chunking(self):
        """1. Standard case: Text fits within chunk_size, returning a single chunk."""
        text = "Hello world! This is a simple test."
        result = chunk_text(text, chunk_size=100, overlap=0, separator=" ")
        self.assertEqual(result, [text])

    def test_chunk_size_exceeded_splits_correctly(self):
        """2. Splitting case: Text exceeding chunk_size splits on natural boundaries."""
        text = "Line 1\nLine 2\nLine 3\nLine 4"
        result = chunk_text(text, chunk_size=13, overlap=0, separator="\n")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "Line 1\nLine 2")
        self.assertEqual(result[1], "Line 3\nLine 4")

    def test_overlap_preserves_context(self):
        """3. Overlap case: Trailing context carries over to the next chunk."""
        text = "Alpha\nBeta\nGamma\nDelta"
        result = chunk_text(text, chunk_size=12, overlap=6, separator="\n")
        self.assertTrue(len(result) > 1)
        self.assertIn("Beta", result[1])


if __name__ == "__main__":
    unittest.main()