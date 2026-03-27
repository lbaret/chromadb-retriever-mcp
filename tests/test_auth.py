import os
import unittest
from unittest.mock import patch

from src.database import get_chroma_client

class TestChromaAuth(unittest.TestCase):
    @patch('src.database.chromadb.HttpClient')
    def test_get_chroma_client_with_auth_http(self, mock_http_client):
        with patch.dict(os.environ, {"CHROMA_HOST": "localhost", "CHROMA_PORT": "8000"}):
            client = get_chroma_client(
                auth_provider="chromadb.auth.token.TokenAuthClientProvider",
                auth_credentials="test_token"
            )
            
            mock_http_client.assert_called_once()
            call_kwargs = mock_http_client.call_args.kwargs
            self.assertEqual(call_kwargs.get("host"), "localhost")
            self.assertEqual(call_kwargs.get("port"), "8000")
            
            settings = call_kwargs.get("settings")
            self.assertIsNotNone(settings)
            self.assertEqual(settings.chroma_client_auth_provider, "chromadb.auth.token_authn.TokenAuthClientProvider")
            self.assertEqual(settings.chroma_client_auth_credentials, "test_token")

    @patch('src.database.chromadb.PersistentClient')
    def test_get_chroma_client_with_auth_persistent(self, mock_persistent_client):
        # Ensure CHROMA_PORT is empty or unset
        with patch.dict(os.environ, {"CHROMA_PORT": ""}):
            client = get_chroma_client(
                auth_provider="chromadb.auth.token.TokenAuthClientProvider",
                auth_credentials="test_token"
            )
            
            mock_persistent_client.assert_called_once()
            call_kwargs = mock_persistent_client.call_args.kwargs
            
            settings = call_kwargs.get("settings")
            self.assertIsNotNone(settings)
            self.assertEqual(settings.chroma_client_auth_provider, "chromadb.auth.token.TokenAuthClientProvider")
            self.assertEqual(settings.chroma_client_auth_credentials, "test_token")

    @patch('src.database.chromadb.HttpClient')
    def test_get_chroma_client_without_auth_http(self, mock_http_client):
        with patch.dict(os.environ, {"CHROMA_HOST": "localhost", "CHROMA_PORT": "8000"}):
            get_chroma_client()
            
            mock_http_client.assert_called_once()
            call_kwargs = mock_http_client.call_args.kwargs
            
            settings = call_kwargs.get("settings")
            self.assertIsNotNone(settings)
            # Default settings should not have auth provider populated over default or set by us
            # We just verify it hasn't been set to custom test values
            self.assertNotEqual(getattr(settings, "chroma_client_auth_credentials", None), "test_token")

if __name__ == '__main__':
    unittest.main()
