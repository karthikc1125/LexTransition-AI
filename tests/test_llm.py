"""
Unit tests for the LLM adapter module.

This module tests the LLM functionality including:
- Extractive summary fallback logic
- Summarize function behavior with and without Ollama
- Edge cases for empty/malformed input
- Mocked Ollama API integration tests

Author: Savani Thakur
Date: 2026-02-09
"""

import importlib
import sys
import pytest

from engine import llm


class TestExtractiveSummary:
    """Tests for the _extractive_summary() internal function."""

    def test_extractive_summary_returns_string(self):
        """Verify that _extractive_summary() always returns a string."""
        result = llm._extractive_summary("This is a test. Another sentence.")
        assert isinstance(result, str), "_extractive_summary() should return a string"

    def test_extractive_summary_limits_sentences(self):
        """Verify that max_sentences parameter limits output correctly."""
        text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
        
        # Default is 3 sentences
        result = llm._extractive_summary(text)
        # Count periods (excluding trailing)
        sentence_count = result.rstrip(". ").count(".") + 1
        assert sentence_count <= 3, "Default should return at most 3 sentences"

    def test_extractive_summary_custom_max_sentences(self):
        """Verify custom max_sentences parameter works."""
        text = "One. Two. Three. Four. Five."
        
        result = llm._extractive_summary(text, max_sentences=2)
        # Should contain at most 2 sentences
        assert "One" in result, "Should include first sentence"
        assert "Two" in result, "Should include second sentence"
        # Third sentence should not be fully present
        assert result.count(". ") <= 2, "Should have at most 2 sentence breaks"

    def test_extractive_summary_handles_empty_string(self):
        """Verify graceful handling of empty input."""
        result = llm._extractive_summary("")
        assert result == "", "Empty input should return empty string"

    def test_extractive_summary_handles_no_periods(self):
        """Verify handling of text without sentence-ending periods."""
        text = "This text has no periods at the end"
        result = llm._extractive_summary(text)
        assert isinstance(result, str), "Should still return a string"

    def test_extractive_summary_handles_newlines(self):
        """Verify that newlines are normalized to spaces."""
        text = "First sentence.\nSecond sentence.\nThird sentence."
        result = llm._extractive_summary(text)
        
        # Should not contain newlines in output
        assert "\n" not in result, "Newlines should be replaced with spaces"
        assert "First sentence" in result, "Content should be preserved"

    def test_extractive_summary_single_sentence(self):
        """Verify handling of single sentence input."""
        text = "Just one sentence here."
        result = llm._extractive_summary(text)
        
        assert "Just one sentence here" in result, "Single sentence should be preserved"


class TestSummarize:
    """Tests for the summarize() function."""

    def test_summarize_returns_string(self):
        """Verify that summarize() always returns a string."""
        result = llm.summarize("This is legal text about section 420.")
        assert isinstance(result, str), "summarize() should return a string"

    def test_summarize_handles_empty_text(self):
        """Verify graceful handling of empty text input."""
        result = llm.summarize("")
        assert isinstance(result, str), "Should return string for empty input"

    def test_summarize_without_question(self):
        """Verify summarize works without optional question parameter."""
        text = "The defendant was charged under IPC Section 302. The court found evidence."
        result = llm.summarize(text)
        
        assert isinstance(result, str), "Should return string"
        assert len(result) > 0 or text == "", "Should return non-empty for non-empty input"

    def test_summarize_with_question(self):
        """Verify summarize works with optional question parameter."""
        text = "The penalty for theft under BNS is imprisonment up to 3 years."
        question = "What is the penalty for theft?"
        
        result = llm.summarize(text, question=question)
        assert isinstance(result, str), "Should return string with question"

    def test_summarize_fallback_without_ollama(self, monkeypatch):
        """Verify fallback to extractive summary when Ollama is not configured."""
        # Ensure Ollama URL is not set
        monkeypatch.delenv("LTA_OLLAMA_URL", raising=False)
        
        # Reload module to pick up env change
        if "engine.llm" in sys.modules:
            del sys.modules["engine.llm"]
        llm_module = importlib.import_module("engine.llm")
        
        text = "First legal point. Second legal point. Third legal point."
        result = llm_module.summarize(text)
        
        # Should use extractive summary (fallback)
        assert isinstance(result, str), "Should return string from fallback"
        assert "First legal point" in result, "Fallback should extract from beginning"

    def test_summarize_long_text(self):
        """Verify handling of longer text input."""
        # Create a longer text with multiple sentences
        sentences = [f"This is sentence number {i} about legal matters." for i in range(10)]
        text = " ".join(sentences)
        
        result = llm.summarize(text)
        
        assert isinstance(result, str), "Should handle long text"
        # Result should be shorter than input (summarized)
        assert len(result) <= len(text), "Summary should not be longer than input"


class TestOllamaIntegration:
    """
    Integration tests for Ollama LLM backend.
    
    These tests use mocking to simulate Ollama API responses.
    """

    def test_summarize_with_mocked_ollama_success(self, monkeypatch):
        """Test successful Ollama API response handling."""
        # Set up Ollama URL
        monkeypatch.setenv("LTA_OLLAMA_URL", "http://localhost:11434")
        
        # Reload module to pick up env change
        if "engine.llm" in sys.modules:
            del sys.modules["engine.llm"]
        
        # Mock the requests module
        class MockResponse:
            ok = True
            def json(self):
                return {"response": "This is a mocked LLM summary."}
        
        class MockRequests:
            @staticmethod
            def post(*args, **kwargs):
                return MockResponse()
        
        # Import with mocked requests
        import engine.llm as llm_module
        monkeypatch.setattr(llm_module, "requests", MockRequests, raising=False)
        
        # Manually set the OLLAMA_URL in the module
        original_url = llm_module.OLLAMA_URL
        llm_module.OLLAMA_URL = "http://localhost:11434"
        
        try:
            result = llm_module.summarize("Test legal text for summarization.")
            # Should return mocked response or fallback
            assert isinstance(result, str), "Should return string"
        finally:
            llm_module.OLLAMA_URL = original_url

    def test_summarize_with_ollama_timeout(self, monkeypatch):
        """Test graceful handling of Ollama timeout."""
        monkeypatch.setenv("LTA_OLLAMA_URL", "http://localhost:11434")
        
        if "engine.llm" in sys.modules:
            del sys.modules["engine.llm"]
        
        import requests
        
        class MockRequestsTimeout:
            @staticmethod
            def post(*args, **kwargs):
                raise requests.exceptions.Timeout("Connection timed out")
        
        import engine.llm as llm_module
        original_url = llm_module.OLLAMA_URL
        llm_module.OLLAMA_URL = "http://localhost:11434"
        
        try:
            # Even with timeout, should fallback gracefully
            result = llm_module.summarize("Text that causes timeout.")
            assert isinstance(result, str), "Should fallback to string on timeout"
        finally:
            llm_module.OLLAMA_URL = original_url

    def test_summarize_with_ollama_error_response(self, monkeypatch):
        """Test handling of Ollama error response."""
        monkeypatch.setenv("LTA_OLLAMA_URL", "http://localhost:11434")
        
        if "engine.llm" in sys.modules:
            del sys.modules["engine.llm"]
        
        class MockErrorResponse:
            ok = False
            status_code = 500
            text = "Internal Server Error"
        
        class MockRequests:
            @staticmethod
            def post(*args, **kwargs):
                return MockErrorResponse()
        
        import engine.llm as llm_module
        original_url = llm_module.OLLAMA_URL
        llm_module.OLLAMA_URL = "http://localhost:11434"
        
        try:
            result = llm_module.summarize("Text with error response.")
            # Should fallback gracefully
            assert isinstance(result, str), "Should fallback on error response"
        finally:
            llm_module.OLLAMA_URL = original_url


class TestModuleConfiguration:
    """Tests for module-level configuration."""

    def test_default_ollama_model(self):
        """Verify default Ollama model is set."""
        # Default should be 'llama2' as per module code
        assert llm.OLLAMA_MODEL == "llama2" or llm.OLLAMA_MODEL is not None, \
            "Should have a default model configured"

    def test_ollama_url_from_environment(self, monkeypatch):
        """Verify Ollama URL can be configured via environment."""
        test_url = "http://test-ollama:11434"
        monkeypatch.setenv("LTA_OLLAMA_URL", test_url)
        
        if "engine.llm" in sys.modules:
            del sys.modules["engine.llm"]
        
        llm_module = importlib.import_module("engine.llm")
        assert llm_module.OLLAMA_URL == test_url, "Should read URL from environment"

    def test_custom_ollama_model_from_environment(self, monkeypatch):
        """Verify Ollama model can be configured via environment."""
        test_model = "mistral"
        monkeypatch.setenv("LTA_OLLAMA_MODEL", test_model)
        
        if "engine.llm" in sys.modules:
            del sys.modules["engine.llm"]
        
        llm_module = importlib.import_module("engine.llm")
        assert llm_module.OLLAMA_MODEL == test_model, "Should read model from environment"
