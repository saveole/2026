# quick-note-posting Specification

## Purpose
Provide a command-line interface for quickly posting notes and thoughts to GitHub issue comments with minimal friction. The system supports automatic timestamp formatting, optional child age tracking, duplicate detection, and seamless integration with existing GitHub repositories. This enables users to maintain real-time notes alongside other automated data collection (e.g., Garmin sleep tracking) in their personal tracking system.
## Requirements
### Requirement: The system MUST accept note content and issue ID as input parameters
The system MUST accept note content and issue ID as required command-line arguments.

#### Scenario: Post note with minimal arguments
- Given a note content: "Quick thought: I should refactor the auth module"
- And an issue ID: 42
- And GITHUB_TOKEN environment variable is set
- When the user runs: `python scripts/quick_note.py "Quick thought: I should refactor the auth module" --issue 42`
- Then the script should validate the input parameters
- And proceed to post the comment to issue #42

#### Scenario: Post note with explicit repository
- Given a note content: "Remember to check API rate limits"
- And an issue ID: 15
- And a repository: "octocat/my-project"
- When the user runs: `python scripts/quick_note.py "Remember to check API rate limits" --issue 15 --repo octocat/my-project`
- Then the script should use the specified repository
- And post the comment to that repository's issue #15

#### Scenario: Handle missing required arguments
- Given the user runs the script without note content
- When the script executes
- Then it should display usage information
- And exit with a non-zero status code
- And the error message should indicate which argument is missing

### Requirement: The system MUST post notes to GitHub issues with metadata
The system MUST post the note content as a comment on the specified issue, including a metadata footer with timestamp and source.

#### Scenario: Successfully post a note
- Given a valid note content: "Tested the new feature, works great!"
- And issue #7 exists in the repository
- And the note is not a duplicate
- When the script posts to GitHub
- Then a new comment should be created on issue #7
- And the comment body should contain the exact note text
- And the comment should include a metadata footer with:
  - `data-source: quick-note`
  - `posted-at: <ISO 8601 timestamp in UTC>`
- And the script should output success message with issue URL

#### Scenario: Include metadata in comment format
- Given a note is being posted
- When the comment is created
- Then the comment format should be:
  ```
  <note content here>

  <!-- data-source: quick-note, posted-at: 2026-01-08T12:34:56Z -->
  ```

### Requirement: The system MUST prevent duplicate note postings
The system MUST detect and prevent posting of identical note content to the same issue.

#### Scenario: Detect and skip duplicate note
- Given a note with content: "Need to update documentation"
- And issue #3 already has a comment with identical content in the last 10 comments
- When the script attempts to post the note
- Then it should skip posting the comment
- And log an info message: "Skipped posting duplicate note to issue #3"
- And exit with success status (0)

#### Scenario: Allow similar but not identical notes
- Given a previous note: "Need to update documentation"
- And a new note: "Need to update documentation for API v2"
- When the script posts the new note
- Then it should create a new comment
- And both notes should exist on the issue

#### Scenario: Case-sensitive duplicate detection
- Given a previous note: "Fix the bug in auth module"
- And a new note with different case: "fix the bug in auth module"
- When the script checks for duplicates
- Then it should treat these as different notes
- And post the new note as a new comment

### Requirement: The system MUST validate GitHub authentication and issue existence
The system MUST verify that authentication is configured and the target issue exists before attempting to post.

#### Scenario: Missing GITHUB_TOKEN
- Given GITHUB_TOKEN environment variable is not set
- When the script attempts to initialize the GitHub client
- Then it should fail with a clear error message
- And the error should mention: "GITHUB_TOKEN environment variable is not set"
- And exit with non-zero status

#### Scenario: Invalid or expired token
- Given GITHUB_TOKEN is set but invalid or expired
- When the script attempts to post to GitHub
- Then it should receive a 401 authentication error
- And output: "Error: Invalid GitHub token"
- And exit with non-zero status

#### Scenario: Non-existent issue
- Given the user specifies issue #999
- And issue #999 does not exist in the repository
- When the script attempts to post
- Then it should fail with error message: "Issue #999 not found in repository <repo>"
- And exit with non-zero status
- And suggest verifying the issue number

### Requirement: The system MUST provide clear feedback on posting results
The system MUST output clear, actionable messages about the outcome of the posting operation.

#### Scenario: Success message with issue details
- Given a note was successfully posted to issue #12
- When the script completes
- Then it should output: "✓ Successfully posted note to issue #12"
- And optionally include the issue URL

#### Scenario: Duplicate skipped message
- Given a duplicate note was detected and skipped
- When the script completes
- Then it should output: "ℹ Note already exists on issue #8 (skipped)"
- And exit with success status (0)

#### Scenario: Error message with context
- Given the script encounters an error (e.g., network failure, API error)
- When the script fails
- Then it should output: "✗ Error: <specific error message>"
- And include actionable information if applicable
- And exit with non-zero status

