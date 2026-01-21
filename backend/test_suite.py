import unittest
from backend.services.ingestion import parse_vtt, parse_summary
from backend.services.intelligence import cluster_meetings

class TestBackend(unittest.TestCase):
    def test_vtt_parsing(self):
        vtt_content = """WEBVTT

1
00:00:01.000 --> 00:00:02.000
Speaker 1: Hello

2
00:00:02.100 --> 00:00:03.000
Speaker 1: World
"""
        chunks = parse_vtt(vtt_content)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]['text'], "Hello World")

    def test_clustering(self):
        embeddings = [[1, 0], [0.9, 0.1], [0, 1]]
        labels = cluster_meetings(embeddings, distance_threshold=0.5)
        self.assertEqual(labels[0], labels[1])
        self.assertNotEqual(labels[0], labels[2])

if __name__ == '__main__':
    unittest.main()
