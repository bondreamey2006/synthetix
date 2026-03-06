import unittest
from unittest.mock import patch

from app.services.rag_pipeline import NOT_FOUND_MESSAGE, run_rag_pipeline


class RagPipelineTests(unittest.TestCase):
    @patch("app.services.rag_pipeline.retrieve_context", return_value=[])
    def test_returns_mandatory_fallback_when_no_context(self, _mock_retrieve):
        result = run_rag_pipeline("Any question")
        self.assertEqual(result["answer"], NOT_FOUND_MESSAGE)
        self.assertEqual(result["sources"], [])
        self.assertEqual(result["confidence"], "low")
        self.assertEqual(result["score"], 0.0)

    @patch("app.services.rag_pipeline._select_supported_sentences", return_value=[])
    @patch(
        "app.services.rag_pipeline.retrieve_context",
        return_value=[{"document": "doc.txt", "chunk_text": "hello", "sentences": ["hello world."], "score": 0.8}],
    )
    def test_returns_mandatory_fallback_when_generator_abstains(self, _mock_retrieve, _mock_supported):
        result = run_rag_pipeline("What is hello?")
        self.assertEqual(result["answer"], NOT_FOUND_MESSAGE)
        self.assertEqual(result["confidence"], "low")
        self.assertGreaterEqual(result["score"], 0.0)

    @patch(
        "app.services.rag_pipeline._select_supported_sentences",
        return_value=[
            {
                "document": "doc.txt",
                "snippet": "Hello world is a greeting.",
                "score": 0.81,
            }
        ],
    )
    @patch(
        "app.services.rag_pipeline.retrieve_context",
        return_value=[{"document": "doc.txt", "chunk_text": "hello world", "sentences": ["Hello world is a greeting."], "score": 0.82}],
    )
    def test_returns_answer_with_sources(self, _mock_retrieve, _mock_supported):
        result = run_rag_pipeline("What is hello?")
        self.assertEqual(result["answer"], "Hello world is a greeting.")
        self.assertEqual(result["confidence"], "high")
        self.assertEqual(result["sources"][0]["document"], "doc.txt")
        self.assertEqual(result["sources"][0]["snippet"], "Hello world is a greeting.")
        self.assertGreater(result["score"], 0.0)


if __name__ == "__main__":
    unittest.main()
