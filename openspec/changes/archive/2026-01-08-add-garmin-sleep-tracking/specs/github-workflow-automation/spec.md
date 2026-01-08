# Capability: GitHub Workflow Automation

## ADDED Requirements

### Requirement: The GitHub Actions workflow MUST execute on a daily schedule
The GitHub Actions workflow MUST execute automatically at a scheduled time each day.

#### Scenario: Daily scheduled run at 6 AM Beijing time
- Given the GitHub Actions workflow is configured with a cron schedule
- When the system time reaches 6 AM Beijing time (10 PM UTC)
- Then the workflow should trigger automatically
- And the workflow should run the Python script to fetch and post Garmin data

#### Scenario: Manual workflow trigger
- Given a developer wants to manually trigger the workflow
- When using the GitHub Actions `workflow_dispatch` event
- Then the workflow should execute immediately
- And it should fetch the previous day's data (or current day if specified)

### Requirement: The workflow MUST securely manage Garmin Connect API credentials
The workflow MUST securely manage Garmin Connect API credentials.

#### Scenario: Credentials stored as GitHub secrets
- Given Garmin email and password are stored as repository secrets
- When the workflow executes
- Then credentials should be passed to the Python script as environment variables
- And credentials should never be logged or exposed in workflow logs

#### Scenario: Missing credentials
- Given one or more required secrets are not configured
- When the workflow attempts to execute
- Then it should fail immediately with a clear error message
- And the error should indicate which secrets are missing

### Requirement: The workflow MUST set up Python environment using uv
The workflow MUST set up the Python runtime and install dependencies using `uv`.

#### Scenario: Initialize Python environment with uv
- Given the workflow starts execution
- When setting up the Python environment
- Then it should install Python 3.11 or later
- And it should use `uv` to install dependencies from `pyproject.toml`
- And dependency installation should complete within 60 seconds

#### Scenario: Cache uv dependencies
- Given the workflow has run previously
- When the workflow runs again
- Then it should restore cached dependencies from GitHub Actions cache
- And cache should be keyed by `uv.lock` file hash
- And this should reduce installation time

## MODIFIED Requirements
None - this is a new capability.

## REMOVED Requirements
None - this is a new capability.

## Cross-References
- Orchestrates: `garmin-api-integration`, `data-formatting`, and `issue-commenting` capabilities
- Depends on: `data-formatting` to format output before commenting
