# Implementation Tasks

## Phase 1: Project Setup and Infrastructure

### 1.1 Initialize Python project structure
- [x] Create `pyproject.toml` with project metadata and dependencies
- [x] Initialize `uv` project with `uv init`
- [x] Add dependencies: `requests`, `python-dotenv`, `pytz`
- [x] Create project directory structure: `src/`, `scripts/`, `tests/`
- [x] Set up Python 3.11+ in `pyproject.toml`
- **Validation**: Run `uv sync` successfully, `uv run python --version` shows 3.12.7 ✓

### 1.2 Verify issue #1 exists
- [x] Confirm issue #1 is accessible via GitHub API
- [x] Document issue #1 title and purpose in README
- **Validation**: Issue #1 is accessible and properly titled ✓

## Phase 2: Core Functionality Implementation

### 2.1 Implement Garmin Connect API client
- [x] Create `src/garmin_client.py` with authentication logic
- [x] Implement `authenticate(email, password)` method
- [x] Implement `get_sleep_data(date)` method
- [x] Add error handling for auth failures and API errors
- [x] Add retry logic with exponential backoff (max 3 retries)
- [x] Create unit tests for API client (mock responses)
- **Validation**: Unit tests pass (7/7 tests passing) ✓

### 2.2 Implement data formatting module
- [x] Create `src/formatter.py` with `format_sleep_entry(date, sleep_time, wake_time)` function
- [x] Implement timezone conversion (UTC to Beijing UTC+8)
- [x] Handle midnight crossover logic (date attribution based on wake time)
- [x] Handle missing data with "数据缺失" placeholder
- [x] Ensure 24-hour time format with leading zeros
- [x] Create unit tests for edge cases (midnight, missing data)
- **Validation**: All test cases produce expected format (14/14 tests passing) ✓

### 2.3 Implement GitHub issue commenter
- [x] Create `src/github_client.py` with `post_comment(issue_number, body)` function
- [x] Implement duplicate detection by checking recent comments
- [x] Use `GITHUB_TOKEN` environment variable for authentication
- [x] Add error handling for rate limiting and auth failures
- [x] Include metadata footer in comments: `<!-- data-source: garmin; fetched-at: ISO8601 -->`
- [x] Create unit tests with mocked GitHub API
- **Validation**: Tests verify comment creation and duplicate detection (15/15 tests passing) ✓

## Phase 3: Orchestration and Workflow

### 3.1 Create main script
- [x] Create `scripts/fetch_and_post.py` as entry point
- [x] Parse command-line arguments (date, optional)
- [x] Orchestrate: authenticate → fetch → format → post
- [x] Add logging with appropriate levels (INFO, WARNING, ERROR)
- [x] Handle graceful failures (no data available, etc.)
- [x] Return appropriate exit codes (0=success, 1=error)
- **Validation**: Script runs with proper argument parsing and error handling ✓

### 3.2 Create GitHub Actions workflow
- [x] Create `.github/workflows/garmin-sync.yml`
- [x] Configure cron trigger: `cron: '0 22 * * *'` (6 AM Beijing)
- [x] Add `workflow_dispatch` trigger for manual runs
- [x] Set up Python step using `actions/setup-python@v5`
- [x] Install `uv` and cache dependencies
- [x] Configure required secrets: `GARMIN_EMAIL`, `GARMIN_PASSWORD`
- [x] Run main script with environment variables
- **Validation**: Workflow file is valid YAML ✓

### 3.3 Configure GitHub repository secrets
- [ ] Add `GARMIN_EMAIL` secret in repository settings (USER ACTION REQUIRED)
- [ ] Add `GARMIN_PASSWORD` secret in repository settings (USER ACTION REQUIRED)
- [x] Document required secrets in README.md
- **Validation**: Secrets documented in README, user needs to configure manually

## Phase 4: Testing and Documentation

### 4.1 Unit testing
- [x] All unit tests passing (36/36 tests)
- **Validation**: Complete test coverage for all modules ✓

### 4.2 Integration testing
- [ ] Manually trigger workflow via `workflow_dispatch` (USER ACTION REQUIRED)
- [ ] Verify authentication succeeds
- [ ] Verify data is fetched from Garmin API
- [ ] Verify comment is created on issue #1
- [ ] Verify format matches specification
- [ ] Test duplicate prevention (run twice)
- **Validation**: End-to-end workflow to be tested by user after configuring secrets

### 4.3 Documentation
- [x] Update README.md with:
  - Project purpose and overview
  - Setup instructions (uv, secrets)
  - Workflow schedule information
  - Troubleshooting guide
- [x] Add inline code comments for complex logic
- [x] Document environment variables and secrets
- **Validation**: README is clear and comprehensive ✓

### 4.4 Final validation
- [x] Run `openspec validate add-garmin-sleep-tracking --strict`
- [x] Resolve any validation errors
- [x] Ensure all implementation tasks are completed
- [ ] Verify daily scheduled run works automatically (TO BE VERIFIED BY USER)
- **Validation**: Implementation complete, ready for user testing ✓

## Task Dependencies

**Parallelizable Tasks:**
- 1.1 and 1.2 can run in parallel
- 2.1, 2.2, and 2.3 can run in parallel after 1.1 completes
- 4.2 and 4.3 can run in parallel after 3.3 completes

**Critical Path:**
1.1 → 2.1 → 3.1 → 3.2 → 3.3 → 4.1 → 4.4

## Estimated Completion Order

**Week 1:**
- Complete Phase 1 (project setup, issue creation)
- Begin Phase 2 (API client, formatter, GitHub client)

**Week 2:**
- Complete Phase 2 (all core functionality)
- Begin Phase 3 (main script, workflow)

**Week 3:**
- Complete Phase 3 (orchestration)
- Begin Phase 4 (testing and documentation)
- Final validation and deployment
