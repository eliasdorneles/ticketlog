# Ticketlog

Lightweight task/issue tracking tool

No daemon, no database - all operations done in-memory, then persisted into a JSON Lines storage.

## Why?

This is heavily inspired by [beads](https://github.com/steveyegge/beads).

I tried `beads`, found it a bit too much for my needs and with weird failure modes.
So I decided to make my own version of it, using the JSON Lines as a log file storing everything.

## Installation

```bash
pip install ticketlog
```

This installs the `tl` command.


Alternatively, if you use [uv](https://docs.astral.sh/uv/):

```bash
uv tool install ticketlog
```

## Features

- **Condensed Output**: Clean, readable list format without heavy dependencies
- **Smart IDs**: 3-letter alphanumeric IDs with configurable prefix
- **Deduplication**: Built-in clean command to dedupe the log file
- **Dependency Tracking**: Manage task dependencies and find ready-to-work tasks
- **JSON Support**: All commands support `--json` flag for scripting
- **Import Support**: Import tasks from beads JsonLines format

## Usage


```bash
tl init    #  initialize a .ticketlog.toml config file

# or, use a custom prefix:
tl init --prefix myproj
```

The prefix is auto-generated from the project directory name by default.

### Create a task

```bash
tl create "Fix login bug" --type bug --priority 0
tl create "Add user profile" --type feature --priority 2 --assignee alice
tl create "Write docs" --type chore --labels "documentation,help-wanted"
```

### List tasks

```bash
# Default: show open and in_progress tasks
tl list   # or use the alias: tl ls

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
tl show tl-ab1
```

### Update a task

```bash
# Change status
tl update tl-a1b --status in_progress

# Update multiple fields
tl update tl-a1b --title "New title" --priority P1 --assignee bob

# Add/remove labels
tl update tl-a1b --add-label urgent --add-label frontend
tl update tl-a1b --remove-label old-label

# Add notes
tl update tl-a1b --notes "Working on this, needs API changes"
```

### Close tasks

```bash
# Close single task
tl close tl-a1b

# Close multiple tasks
tl close tl-a1b tl-bca tl-zyx
```

### Import from beads JsonLines

Import tasks from a beads-format JsonLines file:

```bash
tl import beads tasks.jsonl
```

### Clean and deduplicate log

Remove duplicate entries from the ticketlog file:

```bash
tl clean
```

### Show tasks ready to work on

Lists tasks with status=open and no unresolved dependencies, sorted by priority.

```bash
tl ready
```

### Manage dependencies

```bash
# Add dependency (tl-fds depends on tl-zyx, i.e., tl-zyx blocks tl-fds)
tl dep add tl-fds tl-zyx

# Remove dependency
tl dep remove tl-fds tl-zyx

# List dependencies for a task
tl dep list tl-fds
```

### JSON output

All commands support `--json` flag for machine-readable output:

```bash
tl list --json | jq .
tl show tl-a1b --json
tl create "New task" --json
```

## Data Model

Tasks are stored in `ticketlog.jsonl` (JSON Lines format) in the current directory.

Each task has:

- `id`: Generated ID with configurable prefix and 3-letter alphanumeric code (e.g., tl-a1b, tl-xyz)
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

## Configuration

You can customize ticketlog behavior with a `.ticketlog.toml` configuration file in your project directory. Use `tl init` to create one automatically, or create it manually:

```toml
[project]
# Prefix for ticket IDs
# New tickets will have format: {prefix}-{3-letter-random-id}
prefix = "myproj"
```

This allows you to customize the prefix used in ticket IDs (e.g., change from `tl-a1b` to `myproj-abc`).

The configuration file can be placed at:
- Your git repository root (automatically detected)
- Any parent directory (walks up the tree to find config)
- The current directory

## File Format

Tasks are stored in append-only JSON Lines format:
- One JSON object per line
- Updates append new versions
- Latest version is used when loading
- No compaction needed for normal use

## Examples

```bash
# Initialize project with custom prefix
tl init --prefix api

# Create project tasks
tl create "Design API" --type feature --priority 1
tl create "Implement API" --type feature --priority 1
tl create "Write tests" --type task --priority 2
tl create "Deploy to staging" --type task --priority 2

# Set up dependencies
tl dep add api-bca api-a1b  # Implementation depends on design
tl dep add api-zyx api-bca  # Tests depend on implementation
tl dep add api-fds api-zyx  # Deploy depends on tests

# Check what's ready to work on
tl ready  # Shows api-a1b (Design API)

# Start working on it
tl update api-a1b --status in_progress --assignee alice

# Complete it
tl close api-a1b

# Check again
tl ready  # Now shows api-bca (Implement API)
```

## Development

Project structure:
```
ticketlog/
├── pyproject.toml
├── README.md
└── src/
    └── ticketlog/
        ├── __init__.py
        ├── __main__.py
        ├── cli.py          # CLI argument parsing
        ├── config.py       # Configuration management
        ├── models.py       # Task data model
        ├── storage.py      # JSON Lines storage
        ├── utils.py        # Formatting helpers
        └── commands/       # Command implementations
            ├── init.py
            ├── create.py
            ├── list.py
            ├── show.py
            ├── update.py
            ├── close.py
            ├── ready.py
            ├── start.py
            ├── dep.py
            ├── import_beads.py
            └── clean.py
```

## License

MIT
