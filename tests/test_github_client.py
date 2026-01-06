"""Unit tests for GitHub client."""

import os
import pytest
from unittest.mock import Mock, MagicMock, patch

from src.github_client import (
    GitHubClient,
    GitHubAuthError,
    GitHubClientError,
)


class TestGitHubClientInit:
    """Tests for GitHub client initialization."""

    @patch('src.github_client.Github')
    def test_init_with_token_and_repo(self, mock_github):
        """Test successful initialization."""
        mock_repo = Mock()
        mock_github.return_value.get_repo.return_value = mock_repo

        client = GitHubClient("test_token", "owner/repo")

        assert client.token == "test_token"
        assert client.repo_name == "owner/repo"
        assert client.repo == mock_repo

    def test_from_env(self):
        """Test creating client from environment variable."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"}):
            with patch('src.github_client.Github') as mock_github:
                mock_repo = Mock()
                mock_github.return_value.get_repo.return_value = mock_repo

                client = GitHubClient.from_env("owner/repo")

                assert client.token == "env_token"
                assert client.repo_name == "owner/repo"

    def test_from_env_missing_token(self):
        """Test from_env fails when GITHUB_TOKEN is not set."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(GitHubClientError, match="GITHUB_TOKEN.*not set"):
                GitHubClient.from_env("owner/repo")


class TestPostComment:
    """Tests for posting comments."""

    @patch('src.github_client.Github')
    def test_post_comment_success(self, mock_github_class):
        """Test successfully posting a comment."""
        # Setup mocks
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_issue = Mock()
        mock_issue.get_comments.return_value = []
        mock_issue.create_comment.return_value = Mock()

        mock_repo = Mock()
        mock_repo.get_issue.return_value = mock_issue
        mock_github.get_repo.return_value = mock_repo

        client = GitHubClient("test_token", "owner/repo")

        result = client.post_comment(1, "Test comment")

        assert result is True
        mock_issue.create_comment.assert_called_once()

    @patch('src.github_client.Github')
    def test_post_comment_duplicate_skip(self, mock_github_class):
        """Test skipping duplicate comment."""
        # Setup mocks
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        # Mock existing comment with same date
        mock_existing_comment = Mock()
        mock_existing_comment.body = "2026-01-06: 睡觉 23:30 起床 07:00"

        mock_issue = Mock()
        mock_issue.get_comments.return_value = [mock_existing_comment]

        mock_repo = Mock()
        mock_repo.get_issue.return_value = mock_issue
        mock_github.get_repo.return_value = mock_repo

        client = GitHubClient("test_token", "owner/repo")

        result = client.post_comment(1, "2026-01-06: 睡觉 23:30 起床 07:00")

        assert result is False  # Skipped due to duplicate

    @patch('src.github_client.Github')
    def test_post_comment_with_metadata(self, mock_github_class):
        """Test posting comment with custom metadata."""
        # Setup mocks
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_issue = Mock()
        mock_issue.get_comments.return_value = []
        mock_issue.create_comment.return_value = Mock()

        mock_repo = Mock()
        mock_repo.get_issue.return_value = mock_issue
        mock_github.get_repo.return_value = mock_repo

        client = GitHubClient("test_token", "owner/repo")

        metadata = {"custom": "value"}
        client.post_comment(1, "Test", metadata=metadata)

        # Verify metadata was added to body
        call_args = mock_issue.create_comment.call_args
        body = call_args[0][0]
        assert "custom: value" in body
        assert "<!--" in body


class TestVerifyIssue:
    """Tests for issue verification."""

    @patch('src.github_client.Github')
    def test_verify_issue_exists(self, mock_github_class):
        """Test verifying an existing issue."""
        # Setup mocks
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        mock_repo = Mock()
        mock_repo.get_issue.return_value = Mock()
        mock_github.get_repo.return_value = mock_repo

        client = GitHubClient("test_token", "owner/repo")

        result = client.verify_issue_exists(1)

        assert result is True

    @patch('src.github_client.Github')
    def test_verify_issue_not_found(self, mock_github_class):
        """Test verifying a non-existent issue."""
        from github import GithubException

        # Setup mocks
        mock_github = Mock()
        mock_github_class.return_value = mock_github

        error = GithubException(status=404, data={})
        mock_repo = Mock()
        mock_repo.get_issue.side_effect = error
        mock_github.get_repo.return_value = mock_repo

        client = GitHubClient("test_token", "owner/repo")

        result = client.verify_issue_exists(1)

        assert result is False
