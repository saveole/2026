#!/usr/bin/env python3
"""Main script to fetch Garmin sleep data and post to GitHub issue."""

import argparse
import logging
import os
import sys
from datetime import date, timedelta

from src.garmin_client import GarminClient
from src.formatter import format_sleep_entry, determine_entry_date
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
        description="Fetch Garmin sleep data and post to GitHub issue"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Target date in ISO format (YYYY-MM-DD). Defaults to yesterday.",
    )
    parser.add_argument(
        "--issue",
        type=int,
        default=1,
        help="GitHub issue number (default: 1)",
    )
    parser.add_argument(
        "--repo",
        type=str,
        help="Repository in format 'owner/repo'. Defaults to GITHUB_REPO env var.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and format data without posting to GitHub",
    )

    return parser.parse_args()


def get_target_date(date_str: str = None, default_to_today: bool = False) -> date:
    """
    Get the target date for fetching sleep data.

    Args:
        date_str: Optional date string in ISO format
        default_to_today: If True, default to today instead of yesterday

    Returns:
        Target date (defaults to yesterday, or today if default_to_today is True)
    """
    if date_str:
        try:
            return date.fromisoformat(date_str)
        except ValueError as e:
            logger.error(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")
            sys.exit(1)
    else:
        # Default to today or yesterday
        if default_to_today:
            return date.today()
        else:
            return date.today() - timedelta(days=1)


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
        import subprocess
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

    # Get target date (default to today)
    target_date = get_target_date(args.date, default_to_today=True)
    logger.info(f"Fetching sleep data for {target_date.isoformat()}")

    # Get repository
    repo = args.repo or get_repository()
    logger.info(f"Using repository: {repo}")

    try:

        # Get Garmin domain configuration (for China vs international)

        garmin_client = GarminClient(
            domain="garmin.cn",
            ssl_verify=False
        )
        garmin_client.authenticate()

        # Step 2: Fetch sleep data
        logger.info(f"Fetching sleep data for {target_date.isoformat()}...")
        sleep_data = garmin_client.get_sleep_data(target_date)

        if not sleep_data:
            logger.warning(f"No sleep data available for {target_date.isoformat()}")
            return 0  # Exit gracefully if no data

        # Step 3: Format sleep data
        logger.info("Formatting sleep data...")
        entry_date = determine_entry_date(
            sleep_data["sleep_time"],
            sleep_data["wake_time"]
        )
        formatted_entry = format_sleep_entry(
            entry_date,
            sleep_data["sleep_time"],
            sleep_data["wake_time"]
        )
        logger.info(f"Formatted entry: {formatted_entry}")

        # Dry run mode - just output the formatted data
        if args.dry_run:
            logger.info("DRY RUN MODE - Skipping GitHub post")
            print(f"\n{formatted_entry}")
            return 0

        # Step 4: Post to GitHub issue
        logger.info(f"Posting to issue #{args.issue}...")
        github_client = GitHubClient.from_env(repo)

        # Verify issue exists
        if not github_client.verify_issue_exists(args.issue):
            logger.error(f"Issue #{args.issue} does not exist in repository {repo}")
            return 1

        # Post comment
        posted = github_client.post_comment(args.issue, formatted_entry)

        if posted:
            logger.info(f"Successfully posted comment to issue #{args.issue}")
            return 0
        else:
            logger.info(f"Comment was not posted (likely a duplicate)")
            return 0

    except Exception as e:
        logger.error(f"Error: {e}")
        logger.exception("Detailed error information:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
