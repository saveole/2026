#!/usr/bin/env python3
"""Quick script to post notes to GitHub issue comments.

This script allows posting real-time thoughts and notes to GitHub issues
with minimal friction. It accepts note content and issue ID as parameters,
handles authentication via environment variables, and includes duplicate
detection and metadata tracking.
"""

import argparse
import logging
import os
import subprocess
import sys

# Add project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.github_client import GitHubClient, GitHubClientError, GitHubAuthError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Post quick notes to GitHub issue comments or create new issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Quick thought: I should refactor the auth module" --issue 42
  %(prog)s "Remember to check API rate limits" --issue 15 --repo octocat/my-project
  %(prog)s "Test note" --issue 1 --dry-run

Behavior:
  - If issue exists: Posts note as a comment
  - If issue does not exist: Creates new issue with note as title
        """
    )
    parser.add_argument(
        "note",
        type=str,
        help="Note content to post"
    )
    parser.add_argument(
        "--issue",
        type=int,
        required=True,
        help="GitHub issue number"
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="Repository in format 'owner/repo'. Defaults to GITHUB_REPOSITORY env var or git remote.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Display what would be posted without actually posting",
    )
    parser.add_argument(
        "--child",
        action="store_true",
        help="Include child age information in the comment",
    )

    return parser.parse_args()


def calculate_child_age() -> str:
    """
    Calculate child's age in years, months, and days.

    Returns:
        Age string in format "X岁Y个月Z天"

    Reads child's birthday from CHILD_BIRTHDAY environment variable.
    Defaults to 2025-05-10 if not set.
    """
    from datetime import date

    # Get child's birthday from environment variable
    birthday_str = os.environ.get("CHILD_BIRTHDAY", "2025-05-10")
    try:
        birthday = date.fromisoformat(birthday_str)
    except ValueError:
        logger.warning(f"Invalid CHILD_BIRTHDAY format: {birthday_str}, using default 2025-05-10")
        birthday = date.fromisoformat("2025-05-10")

    today = date.today()

    # Calculate years, months, days
    years = today.year - birthday.year
    months = today.month - birthday.month
    days = today.day - birthday.day

    # Adjust for negative days
    if days < 0:
        # Borrow days from previous month
        months -= 1
        # Get days in the previous month
        if today.month == 1:
            prev_month = 12
            prev_year = today.year - 1
        else:
            prev_month = today.month - 1
            prev_year = today.year

        # Get the last day of the previous month
        if prev_month == 12:
            days_in_prev_month = 31
        else:
            import calendar
            days_in_prev_month = calendar.monthrange(prev_year, prev_month)[1]

        days += days_in_prev_month

    # Adjust for negative months
    if months < 0:
        years -= 1
        months += 12

    # Build age string
    age_parts = []
    if years > 0:
        age_parts.append(f"{years}岁")
    if months > 0:
        age_parts.append(f"{months}个月")
    if days > 0 or not age_parts:
        age_parts.append(f"{days}天")

    return "".join(age_parts)


def get_repository() -> str:
    """
    Get repository from environment variable or git config.

    Returns:
        Repository in format 'owner/repo'

    Exits with error if repository cannot be determined.
    """
    # Check environment variable first
    repo = os.environ.get("GITHUB_REPOSITORY")
    if repo:
        return repo

    # Try to get from git remote
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # Convert git@github.com:owner/repo.git to owner/repo
            if url.startswith("git@github.com:"):
                repo = url[len("git@github.com:"):].replace(".git", "")
                return repo
            # Convert https://github.com/owner/repo.git to owner/repo
            elif url.startswith("https://github.com/"):
                repo = url[len("https://github.com/"):].replace(".git", "")
                return repo
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass

    logger.error(
        "Could not determine repository. Set GITHUB_REPOSITORY environment variable "
        "or run from a git repository with a GitHub remote."
    )
    sys.exit(1)


def main():
    """Main entry point."""
    args = parse_arguments()

    # Validate note content
    if not args.note or not args.note.strip():
        logger.error("Note content cannot be empty")
        sys.exit(1)

    note_content = args.note.strip()
    logger.info(f"Preparing to post note to issue #{args.issue}")
    logger.debug(f"Note content: {note_content[:50]}...")

    # Get repository
    repo = args.repo or get_repository()
    logger.info(f"Using repository: {repo}")

    try:
        # Initialize GitHub client
        github_client = GitHubClient.from_env(repo)

        # Check if issue exists
        if not github_client.verify_issue_exists(args.issue):
            # Issue doesn't exist - create it with note content as title
            logger.info(f"Issue #{args.issue} does not exist. Creating new issue...")

            if args.dry_run:
                print(f"\n[DRY RUN] Would create issue with title:")
                print(f"{note_content}")
                return 0

            # Create issue with note content as title
            new_issue_number = github_client.create_issue(title=note_content, body="")
            print(f"✓ Created issue #{new_issue_number}")
            return 0

        # Issue exists - post as comment
        # Calculate child age if needed
        age_info = calculate_child_age() if args.child else ""

        # Dry run mode - just output what would be posted
        if args.dry_run:
            logger.info("DRY RUN MODE - Skipping GitHub post")
            from datetime import datetime
            now = datetime.now()
            if age_info:
                comment_preview = f"{now.strftime('%Y-%m-%d %H:%M:%S')} - {note_content} - {age_info}"
            else:
                comment_preview = f"{now.strftime('%Y-%m-%d %H:%M:%S')} - {note_content}"
            print(f"\nNote to post to issue #{args.issue}:")
            print(f"{comment_preview}")
            return 0

        # Prepare metadata
        from datetime import datetime, timezone
        now = datetime.now()
        metadata = {
            "data-source": "quick-note",
            "posted-at": now.isoformat(),
        }

        # Format comment with timestamp and optional age info
        if age_info:
            comment_content = f"{now.strftime('%Y-%m-%d %H:%M:%S')} - {note_content} - {age_info}"
        else:
            comment_content = f"{now.strftime('%Y-%m-%d %H:%M:%S')} - {note_content}"

        # Post comment with exact match duplicate detection
        posted = github_client.post_comment(args.issue, comment_content, metadata, exact_match=True)

        if posted:
            print(f"✓ Successfully posted note to issue #{args.issue}")
            return 0
        else:
            print(f"ℹ Note already exists on issue #{args.issue} (skipped)")
            return 0

    except GitHubAuthError as e:
        logger.error(f"Authentication error: {e}")
        print("✗ Error: Invalid GitHub token")
        sys.exit(1)
    except GitHubClientError as e:
        logger.error(f"Client error: {e}")
        print(f"✗ Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.exception("Detailed error information:")
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
