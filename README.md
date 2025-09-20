# TaskMaster 🚀

> A powerful, feature-rich command-line task management system built with Python

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/Author-abdelhamidbouazi-purple.svg)](https://github.com/abdelhamidbouazi)

TaskMaster is an intuitive CLI tool that helps you manage tasks efficiently with features like priority levels, time tracking, Pomodoro timer integration, and powerful analytics. Say goodbye to complex task management apps and hello to simplicity!

## ✨ Features

- 🎯 **Smart Task Management**: Create, update, complete, and delete tasks with ease
- 📊 **Priority System**: 4-level priority system (Low, Medium, High, Urgent) with visual indicators
- ⏱️ **Time Tracking**: Track estimated vs. actual time spent on tasks
- 🍅 **Pomodoro Timer**: Built-in Pomodoro timer for focused work sessions
- 🔍 **Search & Filter**: Find tasks by title, description, tags, status, or category
- 📈 **Analytics**: Get insights into your productivity with detailed analytics
- 🏷️ **Categories & Tags**: Organize tasks with custom categories and tags
- 📅 **Due Dates**: Set and track due dates with overdue warnings
- 💾 **Auto Backup**: Automatic backup system to prevent data loss
- 🚀 **Partial Task IDs**: Use just 3 characters instead of full task IDs for quick actions
- 🔥 **Bulk Operations**: Delete, complete, or update multiple tasks at once
- 📦 **Export/Import**: Backup and restore your tasks in JSON format

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/abdelhamidbouazi/TaskMaster.git
   cd TaskMaster
   ```

2. **Make the setup script executable and run it:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Restart your terminal or source your shell configuration:**
   ```bash
   source ~/.zshrc   # for zsh users
   # or
   source ~/.bashrc  # for bash users
   ```

4. **Start using TaskMaster:**
   ```bash
   tasks list  # Show all tasks
   ```

### Manual Installation (Alternative)

If you prefer manual installation:

```bash
# Make the script executable
chmod +x taskmaster.py

# Add alias to your shell configuration
echo "alias tasks='python3 $(pwd)/taskmaster.py'" >> ~/.zshrc
source ~/.zshrc
```

## 📖 Usage Guide

### Basic Commands

#### Creating Tasks
```bash
# Simple task
tasks create "Review project documentation"

# Task with priority, category, and due date
tasks create "Fix critical bug" -p 4 -c "development" --due 2024-01-15

# Task with description and tags
tasks create "Team meeting" -d "Discuss Q1 goals" -t meeting urgent

# Task with time estimation
tasks create "Code review" -e 2.5
```

#### Viewing Tasks
```bash
# List all tasks
tasks list

# List with detailed information
tasks list --detailed

# Filter by status
tasks list -s todo
tasks list -s in_progress
tasks list -s done

# Filter by priority (minimum level)
tasks list -p 3  # Shows high and urgent priority tasks

# Filter by category
tasks list -c development

# Show tasks due soon
tasks list --due-soon

# Show specific task details
tasks show abc  # Using partial ID
```

#### Managing Tasks
```bash
# Update task title
tasks update abc -t "New task title"

# Change task status
tasks update abc -s in_progress

# Update priority and category
tasks update abc -p 4 -c "urgent-fixes"

# Mark task as complete
tasks complete abc

# Delete a task
tasks delete abc
```

#### Bulk Operations
```bash
# Delete multiple tasks at once
tasks delete abc def ghi
tasks remove abc def ghi  # 'remove' is an alias for 'delete'

# Complete multiple tasks at once
tasks complete abc def ghi

# Update multiple tasks with same properties
tasks bulk-update abc def ghi -s in_progress -p 3
tasks bulk-update abc def -c development --due 2024-02-01
```

#### Time Tracking
```bash
# Log time spent on a task
tasks time abc 2.5  # Log 2.5 hours

# Start a Pomodoro session (25 min work, 5 min break)
tasks pomodoro abc

# Custom Pomodoro timings (30 min work, 10 min break)
tasks pomodoro abc -w 30 -b 10
```

#### Search & Analytics
```bash
# Search tasks
tasks search "bug"
tasks search "meeting"

# View productivity analytics
tasks analytics

# Export tasks to backup
tasks export my-tasks-backup.json

# Import tasks from backup
tasks import my-tasks-backup.json
```

### Priority Levels

TaskMaster uses a 4-level priority system with visual indicators:

| Level | Name | Symbol | Usage |
|-------|------|--------|--------|
| 1 | Low | 🟢 | Nice-to-have tasks |
| 2 | Medium | 🟡 | Regular tasks (default) |
| 3 | High | 🟠 | Important tasks |
| 4 | Urgent | 🔴 | Critical tasks |

### Status Types

- **todo** ⏳ - Not started
- **in_progress** 🔄 - Currently working on
- **blocked** 🚫 - Waiting for dependency
- **done** ✅ - Completed
- **cancelled** ❌ - Cancelled

## 🎯 Smart Features

### Partial Task IDs
Instead of typing the full 8-character task ID, you can use just the first 3 characters:

```bash
# Instead of: tasks delete a1b2c3d4
tasks delete a1b  # Much easier!

# Works for all commands
tasks update a1b -s done
tasks show a1b
tasks time a1b 1.5
```

### Due Date Management
TaskMaster automatically tracks and warns about due dates:

- 🚨 **OVERDUE** - Tasks past their due date
- 📅 **Due TODAY** - Tasks due today
- 📅 **Due TOMORROW** - Tasks due tomorrow
- 📅 **Due in X days** - Future due dates

### Bulk Operations
Perform operations on multiple tasks at once for maximum efficiency:

```bash
# Delete multiple tasks
tasks delete a1b c2d e3f

# Complete multiple tasks
tasks complete a1b c2d e3f

# Update multiple tasks with same properties
tasks bulk-update a1b c2d e3f -s in_progress -p 4
```

All bulk operations support partial task IDs and provide clear feedback about successful and failed operations.

### Automatic Backups
Every time you save changes, TaskMaster automatically creates timestamped backups in `~/.taskmaster/backups/` to prevent data loss.

## 📊 Analytics Dashboard

Get insights into your productivity:

```bash
tasks analytics
```

This shows:
- ✅ Total and completed tasks
- 📈 Completion rate
- 🚨 Overdue tasks count
- ⏱️ Time tracking accuracy
- 📊 Distribution by status, priority, and category

## 🗂️ Data Storage

TaskMaster stores your data in:
- **Main data file**: `~/.taskmaster/tasks.json`
- **Backups**: `~/.taskmaster/backups/`

All data is stored locally on your machine - no cloud dependency!

## 🔧 Configuration

### Custom Alias
You can customize the command alias by editing your shell configuration:

```bash
# In ~/.zshrc or ~/.bashrc
alias tm='python3 /path/to/taskmaster.py'      # Short alias
alias todo='python3 /path/to/taskmaster.py'    # Alternative alias
```

### Pomodoro Settings
Customize default Pomodoro timings by modifying the PomodoroTimer class in the script.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Ideas for Contributions
- [ ] Web dashboard interface
- [ ] Calendar integration
- [ ] Notification system
- [ ] Collaboration features
- [ ] Mobile companion app
- [ ] Integration with external tools (GitHub, Slack, etc.)

## 🐛 Troubleshooting

### Common Issues

**Q: Command `tasks` not found**
- Make sure you ran `./setup.sh` and restarted your terminal
- Check if the alias was added: `grep "alias tasks" ~/.zshrc`

**Q: Permission denied when running setup**
- Make setup executable: `chmod +x setup.sh`

**Q: Tasks not saving**
- Check if `~/.taskmaster/` directory exists and is writable
- Ensure you have disk space available

**Q: Partial task ID conflicts**
- Use more characters (4-5) if multiple tasks start with same 3 characters
- The system will show you all matching IDs when there's ambiguity

## 📝 Examples & Use Cases

### Daily Workflow
```bash
# Start your day
tasks list --due-soon

# Add today's tasks
tasks create "Code review for PR #123" -p 3 -c development
tasks create "Team standup meeting" -p 2 -t meeting --due 2024-01-15

# Work on tasks with Pomodoro
tasks pomodoro abc  # Start focused work session

# Track your progress
tasks time abc 1.5  # Log time spent
tasks update abc -s done  # Mark as complete

# End of day review
tasks analytics
```

### Project Management
```bash
# Set up project tasks
tasks create "Setup development environment" -p 3 -c setup -e 4
tasks create "Design database schema" -p 3 -c design -e 6
tasks create "Implement user authentication" -p 4 -c development -e 8

# Track project progress
tasks list -c development
tasks analytics
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Abdelhamid Bouazi**
- GitHub: [@abdelhamidbouazi](https://github.com/abdelhamidbouazi)
- Created with ❤️ for productivity enthusiasts

## 🙏 Acknowledgments

- Built with Python 3 and love for simplicity
- Inspired by the need for a lightweight, powerful task manager
- Thanks to the open-source community for inspiration

---

**Happy Task Managing! 🎉**

*If you find TaskMaster helpful, please consider giving it a ⭐ on GitHub!*