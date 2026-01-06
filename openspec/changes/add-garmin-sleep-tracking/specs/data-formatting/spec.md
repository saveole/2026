# Capability: Data Formatting

## ADDED Requirements

### Requirement: The system MUST format sleep/wake data in Chinese template
The system MUST format Garmin sleep data into the specified Chinese text format.

#### Scenario: Format standard sleep data
- Given sleep data with date "2026-01-06", sleep time "23:30", and wake time "07:00"
- When the data is formatted
- Then it should produce: `2026-01-06: 睡觉 23:30 起床 07:00`
- And the format should match exactly: `{date}: 睡觉 {sleep_time} 起床 {wake_time}`

#### Scenario: Handle midnight crossover
- Given sleep data where sleep time is after midnight (e.g., "01:00")
- When the data is formatted
- Then it should correctly attribute the date based on wake time (not sleep time)
- Example: Wake at 07:00 on 2026-01-06 after sleeping at 01:00 should format as `2026-01-06: 睡觉 01:00 起床 07:00`

#### Scenario: Handle missing or null times
- Given sleep data where either sleep or wake time is null or unavailable
- When the data is formatted
- Then it should use placeholder text "数据缺失" for missing values
- Example: `2026-01-06: 睡觉 数据缺失 起床 07:00`

#### Scenario: Preserve 24-hour format
- Given sleep time "23:30" and wake time "07:15"
- When formatting times
- Then times should maintain 24-hour format with leading zeros
- And minutes should always be two digits
- And no AM/PM indicators should be included

### Requirement: The system MUST convert timestamps to Beijing timezone
The system MUST convert Garmin API timestamps to Beijing local time.

#### Scenario: Convert UTC to Beijing time
- Given a timestamp from Garmin API in UTC (e.g., "2026-01-05T18:30:00Z")
- When converting to Beijing timezone (UTC+8)
- Then it should correctly calculate the local time (e.g., "2026-01-06T02:30:00+08:00")
- And extract only the time component for formatting (e.g., "02:30")

#### Scenario: Handle daylight saving time edge cases
- Given timestamps during potential DST transition periods
- When converting to Beijing timezone
- Then it should correctly handle that China does not observe DST
- And offset should always be UTC+8 regardless of date

## MODIFIED Requirements
None - this is a new capability.

## REMOVED Requirements
None - this is a new capability.

## Cross-References
- Used by: `issue-commenting` capability to prepare data for GitHub comments
- Depends on: `garmin-api-integration` for raw data input
