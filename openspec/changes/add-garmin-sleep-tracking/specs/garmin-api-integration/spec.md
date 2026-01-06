# Capability: Garmin API Integration

## ADDED Requirements

### Requirement: The system MUST authenticate with Garmin Connect API
The system MUST authenticate with Garmin Connect API using credentials to access sleep data.

#### Scenario: Successful authentication
- Given valid Garmin credentials (email/password) are stored as GitHub Actions secrets
- When the Python script initializes
- Then it should successfully authenticate and receive a valid session token
- And the token should be usable for subsequent API requests

#### Scenario: Invalid credentials
- Given invalid or expired Garmin credentials
- When the Python script attempts to authenticate
- Then it should fail with a clear error message indicating authentication failure
- And the GitHub Action should mark the run as failed

### Requirement: The system MUST fetch daily sleep data from Garmin Connect API
The system MUST retrieve sleep and wake times for a specific date from Garmin Connect API.

#### Scenario: Fetch previous day's sleep data
- Given the user is authenticated with Garmin Connect API
- When requesting sleep data for the previous calendar day
- Then the system should return sleep start time and wake end time
- And times should be in the user's local timezone (Beijing UTC+8)
- And data should include date, sleep time, and wake time

#### Scenario: Handle missing data
- Given the user is authenticated with Garmin Connect API
- When requesting sleep data for a date with no recorded sleep data
- Then the system should return null or empty values
- And the workflow should gracefully skip creating a comment
- And a warning should be logged indicating no data available

#### Scenario: API rate limiting or temporary unavailability
- Given the Garmin Connect API returns rate limit errors (429) or service unavailable (503)
- When the Python script makes a request
- Then it should implement exponential backoff retry logic
- And retry up to 3 times with increasing delays
- And fail permanently after exhausting retries with a clear error message

## MODIFIED Requirements
None - this is a new capability.

## REMOVED Requirements
None - this is a new capability.

## Cross-References
- Depends on: `data-formatting` capability to format retrieved data
- Used by: `github-workflow-automation` capability for scheduled execution
