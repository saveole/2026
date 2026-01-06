"""GitHub API client using PyGithub library."""

import os
import logging
from datetime import datetime, timezone
from typing import Optional

from github import Github, GithubException
from github import Issue

logger = logging.getLogger(__name__)


class GitHubClientError(Exception):
    """Base exception for GitHub client errors."""
    pass


class GitHubAuthError(GitHubClientError):
    """Raised when GitHub authentication fails."""
    pass


class GitHubClient:
    """Client for interacting with GitHub API using PyGithub."""

    def __init__(self, token: str, repo: str):
        """
        Initialize GitHub client.

        Args:
            token: GitHub personal access token
            repo: Repository in format "owner/repo"
        """
        self.token = token
        self.repo_name = repo
        self.github = Github(token)
        self.repo = self.github.get_repo(repo)

    def post_comment(
        self,
        issue_number: int,
        body: str,
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Post a comment to a GitHub issue with duplicate detection.

        Args:
            issue_number: Issue number
            body: Comment body text
            metadata: Optional metadata to include in comment footer

        Returns:
            True if comment was posted, False if skipped (duplicate)

        Raises:
            GitHubAuthError: If authentication fails
            GitHubClientError: If API request fails
        """
        try:
            # Get the issue
            issue = self.repo.get_issue(issue_number)

            # Check for duplicates before posting
            if self._is_duplicate(issue, body):
                logger.info(
                    f"Skipped posting duplicate comment to issue #{issue_number}"
                )
                return False

            # Add metadata footer
            comment_body = self._add_metadata_footer(body, metadata)

            # Post the comment
            issue.create_comment(comment_body)
            logger.info(f"Successfully posted comment to issue #{issue_number}")
            return True

        except GithubException as e:
            if e.status == 401:
                raise GitHubAuthError("Invalid GitHub token")
            elif e.status == 404:
                raise GitHubClientError(
                    f"Issue #{issue_number} or repository not found"
                )
            else:
                raise GitHubClientError(f"Failed to post comment: {e}")

    def _is_duplicate(self, issue: Issue.Issue, body: str) -> bool:
        """
        Check if a comment with the same content already exists.

        Args:
            issue: PyGithub Issue object
            body: Comment body to check

        Returns:
            True if duplicate exists, False otherwise
        """
        try:
            import re

            # Extract the date pattern from the body (e.g., "2026-01-06:")
            date_match = re.search(r'\d{4}-\d{2}-\d{2}:', body)
            if not date_match:
                return False

            date_prefix = date_match.group(0)

            # Get recent comments and check for duplicates
            # PyGithub handles pagination automatically
            comments = list(issue.get_comments())[:10]  # Check last 10 comments

            for comment in comments:
                if date_prefix in comment.body:
                    logger.debug(f"Found duplicate comment with date {date_prefix}")
                    return True

            return False

        except Exception as e:
            logger.warning(f"Failed to check for duplicates: {e}")
            # Continue with posting if duplicate check fails
            return False

    def _add_metadata_footer(self, body: str, metadata: Optional[dict]) -> str:
        """
        Add metadata footer to comment body.

        Args:
            body: Original comment body
            metadata: Metadata dictionary

        Returns:
            Comment body with metadata footer
        """
        if metadata is None:
            metadata = {}

        # Default metadata
        default_metadata = {
            "data-source": "garmin",
            "fetched-at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }

        # Merge with provided metadata
        final_metadata = {**default_metadata, **metadata}

        # Build metadata string
        meta_parts = [f"{k}: {v}" for k, v in final_metadata.items()]
        meta_comment = "<!-- " + ", ".join(meta_parts) + " -->"

        # Append to body
        return f"{body}\n\n{meta_comment}"

    def verify_issue_exists(self, issue_number: int) -> bool:
        """
        Verify that an issue exists and is accessible.

        Args:
            issue_number: Issue number to verify

        Returns:
            True if issue exists, False otherwise

        Raises:
            GitHubAuthError: If authentication fails
        """
        try:
            self.repo.get_issue(issue_number)
            logger.info(f"Issue #{issue_number} exists and is accessible")
            return True

        except GithubException as e:
            if e.status == 401:
                raise GitHubAuthError("Invalid GitHub token")
            elif e.status == 404:
                logger.warning(f"Issue #{issue_number} not found")
                return False
            else:
                raise GitHubClientError(f"Failed to verify issue: {e}")

    @classmethod
    def from_env(cls, repo: str) -> "GitHubClient":
        """
        Create GitHub client using GITHUB_TOKEN environment variable.

        Args:
            repo: Repository in format "owner/repo"

        Returns:
            GitHubClient instance

        Raises:
            GitHubClientError: If GITHUB_TOKEN is not set
        """
        token = os.environ.get("GITHUB_TOKEN")

        if not token:
            raise GitHubClientError(
                "GITHUB_TOKEN environment variable is not set"
            )

        return cls(token, repo)
