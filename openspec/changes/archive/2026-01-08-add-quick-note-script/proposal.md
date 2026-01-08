# Proposal: Add Quick Note Script

## Summary
Add a command-line script `quick_note.py` that allows posting real-time thoughts and notes to GitHub issue comments with minimal friction. The script will accept content and issue ID as parameters, handle authentication via environment variables, and include duplicate detection and metadata tracking.

## Motivation
Currently, the codebase has automation for posting Garmin sleep data to GitHub issues, but there's no easy way to manually post quick thoughts or notes to issues. Users need a simple, fast way to capture and record real-time insights, ideas, or notes without manually navigating to GitHub.

## Scope
This change adds a new standalone script that:
- Accepts note content and issue ID as command-line arguments
- Uses existing `GitHubClient` for API interactions
- Implements duplicate detection to prevent identical comments
- Includes timestamp metadata in posted comments
- Provides clear error messages for common failure scenarios

### Out of Scope
- Web interface or interactive mode
- Note editing or deletion
- Attachment support (images, files)
- Multi-line note formatting beyond basic markdown
- Integration with external note-taking tools

## Proposed Solution
Create `scripts/quick_note.py` that:
1. Parses command-line arguments (content, issue number, optional repo)
2. Authenticates using `GITHUB_TOKEN` environment variable (reuse existing pattern)
3. Validates issue exists before posting
4. Checks for duplicate content in recent comments
5. Posts comment with metadata footer if not duplicate
6. Provides clear feedback on success/failure

## Success Criteria
- Script can successfully post a note to any issue in the repository
- Duplicate notes are detected and skipped with appropriate logging
- Clear error messages for missing token, invalid issue, or API failures
- Metadata footer is included in all posted comments
- Script follows existing code patterns and conventions

## Alternatives Considered
1. **GitHub CLI extension**: Would require users to install and configure additional tooling
2. **Interactive Python script**: Would be slower for quick notes; CLI args are more efficient
3. **Web service**: Overkill for this use case; introduces security and deployment complexity

## Dependencies
- Existing `src/github_client.py` module
- `GITHUB_TOKEN` environment variable must be configured
- Target issue must exist in repository

## Impact Assessment
- **Low risk**: New script doesn't modify existing functionality
- **Backwards compatible**: No changes to existing code or workflows
- **Maintenance burden**: Minimal; reuses existing GitHub client infrastructure
