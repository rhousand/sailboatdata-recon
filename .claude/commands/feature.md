# Feature Request Workflow

Automate the complete workflow for implementing a feature request:
1. Create GitHub issue
2. Create branch
3. Implement changes
4. Test changes
5. Commit and push
6. Create pull request (WITHOUT auto-merging)

## Instructions for Claude

When the user invokes this command with a feature description, follow these steps automatically:

### Step 1: Create GitHub Issue
- Use `gh issue create` with:
  - Clear, descriptive title based on user's request
  - Detailed description of the feature/change
  - Acceptance criteria
- Capture the issue number for the next steps

### Step 2: Create Branch
- Create branch named: `issue-{number}-{short-slug}`
  - Example: `issue-9-add-color-flag`
- Switch to the new branch with `git checkout -b`

### Step 3: Plan Implementation
- Use TodoWrite tool to create task list including:
  - Code changes needed
  - Documentation updates
  - Testing steps
  - Commit and PR creation

### Step 4: Implement Changes
- Make all necessary code changes
- Update documentation files:
  - README.md (if user-facing changes)
  - CLAUDE.md (if development-related changes)
  - requirements.txt, environment.yml, flake.nix (if dependencies change)
- Follow existing code style and patterns

### Step 5: Test Changes
- Test in Nix development environment if applicable: `nix develop --command python ...`
- Verify core functionality works
- **CRITICAL**: If tests fail with non-zero exit status, DO NOT create PR
- Mark appropriate todos as completed after testing

### Step 6: Commit Changes
- Stage relevant changes with `git add`
- **Exclude** `.claude/settings.local.json` unless specifically requested
- Create commit message following this format:
  ```
  <descriptive title>

  <detailed description of changes>

  Changes:
  - <change 1>
  - <change 2>

  Testing:
  - <test result 1>
  - <test result 2>

  Closes #<issue-number>

  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude <noreply@anthropic.com>
  ```
- Push to remote: `git push -u origin <branch-name>`

### Step 7: Create Pull Request
- Use `gh pr create` with:
  - Clear title matching the feature
  - Detailed description including:
    - Summary of changes
    - List of modifications
    - Testing results
    - "Closes #<issue-number>"
- **DO NOT USE** `gh pr merge` - wait for user approval
- Inform user that PR is ready for review

### Important Guidelines

1. **Progress Tracking**: Use TodoWrite tool throughout to track all steps
2. **Testing Required**: Always test before creating PR
3. **No Auto-Merge**: NEVER automatically merge PRs - user must approve
4. **Ask Questions**: If request is ambiguous, ask for clarification before starting
5. **Documentation**: Update all relevant docs (README, CLAUDE.md, etc.)
6. **Error Handling**: If any step fails, stop and report the issue to user
7. **Version Control**: Exclude settings files unless explicitly requested

### Example Workflow

**User Input:**
```
/feature Add --quiet flag to suppress all output except errors
```

**Automated Steps:**
1. ✅ Creates issue #9: "Add --quiet flag to suppress all output except errors"
2. ✅ Creates branch: `issue-9-quiet-flag`
3. ✅ Plans tasks with TodoWrite
4. ✅ Implements --quiet flag in sailboat_compare.py
5. ✅ Updates README.md with new flag documentation
6. ✅ Tests with: `nix develop --command python sailboat_compare.py "Catalina 30" "Hunter 33" --quiet`
7. ✅ Commits and pushes changes
8. ✅ Creates PR #10
9. ✅ Reports: "PR #10 ready for review at https://github.com/..."

**User then decides whether to merge the PR**
