# Proposal: Add Garmin Sleep/Wake Tracking

## Summary
Integrate Garmin watch sleep/wake data with GitHub Issues via automated GitHub Actions, enabling automatic daily tracking of sleep and wake times appended to issue #1.

## Motivation
This project serves as a personal log for 2026 activities including early rising records and weekly reports. Currently, data entry is manual. By automating the collection of sleep/wake data from Garmin watches, we can:
- Eliminate manual data entry overhead
- Ensure consistent and accurate daily tracking
- Build a foundation for future personal analytics
- Leverage GitHub Issues as a simple, accessible data store

## Proposed Solution
Implement a GitHub Actions workflow that:
1. Runs daily at 6 AM (Beijing time)
2. Authenticates with Garmin Connect API using stored secrets
3. Fetches the previous day's sleep and wake times
4. Formats data as `YYYY-MM-DD: 睡觉 HH:MM 起床 HH:MM`
5. Appends a new comment to issue #1

### Technical Approach
- **Language**: Python 3.11+
- **Dependency Management**: `uv` for fast, modern Python package management
- **Authentication**: Garmin Connect API credentials stored as GitHub Actions secrets
- **Scheduling**: GitHub Actions cron trigger (`cron: '0 22 * * *'` for 6 AM Beijing/UTC+8)
- **Data Format**: Simple Chinese text format for easy reading

## Scope

### In Scope
- Garmin Connect API integration for sleep data retrieval
- GitHub Actions workflow setup and scheduling
- Python script with `uv` dependency management
- Automatic comment creation on issue #1
- Error handling and retry logic
- Basic logging for debugging

### Out of Scope
- Other health metrics (steps, heart rate, etc.) - future enhancement
- Data visualization or dashboards
- Historical data backfill
- Multiple issue tracking (only issue #1)
- Webhook integration (manual trigger support only)

## Success Criteria
- ✅ GitHub Actions successfully runs daily at scheduled time
- ✅ Sleep/wake data accurately retrieved from Garmin Connect API
- ✅ Data appended to issue #1 in the specified format
- ✅ Dependencies managed via `uv` with minimal setup
- ✅ Clear error messages if API authentication fails or data is unavailable

## Open Questions
1. Should we implement de-duplication to prevent duplicate comments if the workflow runs multiple times?
2. What should happen if Garmin API is temporarily unavailable?
3. Should we add a manual workflow_dispatch trigger for on-demand updates?

## Related Changes
None - this is the initial automation feature for this repository.
