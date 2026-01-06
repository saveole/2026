# Capability: Issue Commenting

## ADDED Requirements

### Requirement: The system MUST append formatted data to GitHub issue
The system MUST append formatted sleep/wake data as a new comment on issue #1.

#### Scenario: Successfully append comment
- Given formatted sleep data: `2026-01-06: 睡觉 23:30 起床 07:00`
- And issue #1 exists in the repository
- When the script posts to GitHub API
- Then a new comment should be created on issue #1
- And the comment body should contain exactly the formatted text
- And the comment should be attributed to the GitHub Actions bot

#### Scenario: Handle non-existent issue
- Given issue #1 does not exist in the repository
- When the script attempts to post a comment
- Then it should fail with a clear error message
- And the workflow should be marked as failed
- And the error should suggest creating issue #1 first

#### Scenario: Duplicate prevention
- Given a comment with the same date already exists on issue #1
- When the script attempts to post a new comment
- Then it should skip creating a duplicate comment
- And it should log an info message indicating data already recorded
- And the workflow should succeed without posting

#### Scenario: Rate limiting on GitHub API
- Given the GitHub API returns a rate limit error (403)
- When the script attempts to post a comment
- Then it should implement exponential backoff retry logic
- And retry up to 3 times
- And fail permanently after exhausting retries

### Requirement: The system MUST authenticate with GitHub API
The system MUST authenticate with GitHub API to create comments.

#### Scenario: Authenticate with GitHub token
- Given a GitHub token is provided as `GITHUB_TOKEN` environment variable
- When the script initializes the GitHub client
- Then it should use the token for API requests
- And the token should have `repo` or `issues` scope permissions

#### Scenario: Handle invalid or expired token
- Given an invalid or expired GitHub token
- When the script attempts to create a comment
- Then it should fail with authentication error (401)
- And the workflow should mark the run as failed
- And error logs should indicate authentication problem

### Requirement: The system MUST include metadata in comments for data integrity
The system MUST include minimal metadata in comments for data integrity.

#### Scenario: Include timestamp in comment
- Given a new sleep/wake entry is being posted
- When creating the comment
- Then the comment should include a hidden metadata footer with timestamp
- Example: `<!-- data-source: garmin; fetched-at: 2026-01-06T06:00:00Z -->`
- And this metadata should aid in duplicate detection

## MODIFIED Requirements
None - this is a new capability.

## REMOVED Requirements
None - this is a new capability.

## Cross-References
- Uses: Formatted data from `data-formatting` capability
- Triggered by: `github-workflow-automation` capability
- Independent of: `garmin-api-integration` (could use other data sources)
