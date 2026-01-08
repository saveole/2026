# Implementation Tasks

## Phase 1: Script Skeleton and Argument Parsing
- [x] Create `scripts/quick_note.py` with shebang and basic imports
- [x] Implement `parse_arguments()` function with argparse
  - Add positional argument for note content
  - Add `--issue` required argument for issue number
  - Add `--repo` optional argument for repository override
  - Add `--dry-run` optional flag for testing
- [x] Implement `get_repository()` helper function (reuse from fetch_and_post.py)
- [x] Add basic logging configuration

## Phase 2: GitHub Integration
- [x] Import GitHubClient and related exceptions from existing module
- [x] Implement main() function skeleton
- [x] Add GitHub client initialization using `GitHubClient.from_env()`
- [x] Implement issue existence validation using `verify_issue_exists()`
- [x] Add error handling for missing GITHUB_TOKEN and invalid issues

## Phase 3: Duplicate Detection Enhancement
- [x] Review existing `_is_duplicate()` method in GitHubClient
- [x] Determine if quick notes need different duplicate logic (current logic checks for date patterns)
- [x] Implement duplicate check for exact content matching if needed
- [x] Add logging for duplicate detection results

## Phase 4: Note Posting with Metadata
- [x] Implement metadata dictionary construction for quick notes:
  - `data-source: quick-note`
  - `posted-at: <current UTC timestamp>`
- [x] Call `post_comment()` with note content and metadata
- [x] Add success/failure output messages with appropriate formatting
- [x] Implement dry-run mode that displays what would be posted

## Phase 5: Error Handling and User Feedback
- [x] Add try-except blocks for GitHubAuthError
- [x] Add try-except blocks for GitHubClientError
- [x] Implement clear error messages for each failure scenario
- [x] Add success message with issue number and optional URL
- [x] Add duplicate skipped message with info icon
- [x] Ensure appropriate exit codes (0 for success, 1 for errors)

## Phase 6: Testing and Validation
- [x] Test with valid note and issue (dry-run mode first)
- [x] Test actual posting to a test issue
- [x] Test duplicate detection by posting same note twice
- [x] Test error cases:
  - Missing GITHUB_TOKEN
  - Invalid issue number
  - Invalid repository format
  - Empty note content
- [x] Verify metadata footer is correctly formatted
- [x] Test with explicit --repo argument
- [x] Test without --repo argument (auto-detection)

## Phase 7: Documentation
- [x] Add docstring to script explaining purpose and usage
- [x] Add --help output examples
- [x] Update README.md (if needed) with usage example
- [x] Add example to quick_start.md showing typical usage

## Dependencies
- None - this is standalone work that reuses existing infrastructure

## Notes
- Reuse existing `GitHubClient.from_env()` pattern for consistency
- Follow logging and error handling patterns from `fetch_and_post.py`
- Keep script simple and focused on single responsibility
- Consider whether exact content matching needs to ignore metadata footer
