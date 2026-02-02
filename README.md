# Tasklog

Lightweight task/issue tracking tool with JSON Lines storage. No daemon, no database - all operations in-memory.

## Installation

```bash
cd tasklog
uv sync
uv pip install -e .
```

This installs the `tl` command.

## Usage

### Create a task

```bash
tl create "Fix login bug" --type bug --priority 0
tl create "Add user profile" --type feature --priority 2 --assignee alice
tl create "Write docs" --type chore --labels "documentation,help-wanted"
```

### List tasks

```bash
# Default: show open and in_progress tasks
tl list

# Show all tasks
tl list --all

# Filter by status
tl list --status closed

# Filter by type
tl list --type bug

# Filter by assignee
tl list --assignee alice

# Filter by label
tl list --label documentation
```

### Show task details

```bash
tl show tl-1
```

### Update a task

```bash
# Change status
tl update tl-1 --status in_progress

# Update multiple fields
tl update tl-1 --title "New title" --priority P1 --assignee bob

# Add/remove labels
tl update tl-1 --add-label urgent --add-label frontend
tl update tl-1 --remove-label old-label

# Add notes
tl update tl-1 --notes "Working on this, needs API changes"
```

### Close tasks

```bash
# Close single task
tl close tl-1

# Close multiple tasks
tl close tl-1 tl-2 tl-3
```

### Show tasks ready to work on

Lists tasks with status=open and no unresolved dependencies, sorted by priority.

```bash
tl ready
```

### Manage dependencies

```bash
# Add dependency (tl-4 depends on tl-3, i.e., tl-3 blocks tl-4)
tl dep add tl-4 tl-3

# Remove dependency
tl dep remove tl-4 tl-3

# List dependencies for a task
tl dep list tl-4
```

### JSON output

All commands support `--json` flag for machine-readable output:

```bash
tl list --json | jq .
tl show tl-1 --json
tl create "New task" --json
```

## Data Model

Tasks are stored in `tasklog.jl` (JSON Lines format) in the current directory.

Each task has:
- `id`: Auto-incrementing ID (tl-1, tl-2, ...)
- `title`: Task title
- `description`: Detailed description
- `type`: task, bug, feature, epic, or chore
- `status`: open, in_progress, to_review, or closed
- `priority`: 0-4 (0=highest/critical, 2=medium, 4=backlog)
- `assignee`: Username or null
- `labels`: List of label strings
- `created_at`, `updated_at`, `closed_at`: ISO 8601 timestamps
- `dependencies`: List of task IDs this task depends on
- `notes`: Additional notes

## Priority Levels

- P0 (0): Critical - Highest priority
- P1 (1): High priority
- P2 (2): Medium priority (default)
- P3 (3): Low priority
- P4 (4): Backlog

Accept both formats: `--priority 0` or `--priority P0`

## File Format

Tasks are stored in append-only JSON Lines format:
- One JSON object per line
- Updates append new versions
- Latest version is used when loading
- No compaction needed for normal use

## Examples

```bash
# Create project tasks
tl create "Design API" --type feature --priority 1
tl create "Implement API" --type feature --priority 1
tl create "Write tests" --type task --priority 2
tl create "Deploy to staging" --type task --priority 2

# Set up dependencies
tl dep add tl-2 tl-1  # Implementation depends on design
tl dep add tl-3 tl-2  # Tests depend on implementation
tl dep add tl-4 tl-3  # Deploy depends on tests

# Check what's ready to work on
tl ready  # Shows tl-1 (Design API)

# Start working on it
tl update tl-1 --status in_progress --assignee alice

# Complete it
tl close tl-1

# Check again
tl ready  # Now shows tl-2 (Implement API)
```

## Development

Project structure:
```
tasklog/
├── pyproject.toml
├── README.md
└── src/
    └── tasklog/
        ├── __init__.py
        ├── __main__.py
        ├── cli.py          # CLI argument parsing
        ├── models.py       # Task data model
        ├── storage.py      # JSON Lines storage
        ├── utils.py        # Formatting helpers
        └── commands/       # Command implementations
            ├── create.py
            ├── list.py
            ├── show.py
            ├── update.py
            ├── close.py
            ├── ready.py
            └── dep.py
```

## License

MIT
