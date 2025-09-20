#!/usr/bin/env python3
"""
TaskMaster - A Powerful Task Management CLI Tool
Features:
- Task creation with priorities, categories, and due dates
- Time tracking and estimation
- Task dependencies and subtasks
- Analytics and reporting
- Search and filtering
- Data persistence with JSON
- Backup and restore
- Pomodoro timer integration
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
import time
import threading
from dataclasses import dataclass, asdict
from enum import Enum

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class Status(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"

@dataclass
class Task:
    id: str
    title: str
    description: str = ""
    priority: int = Priority.MEDIUM.value
    category: str = "general"
    status: str = Status.TODO.value
    created_at: str = ""
    updated_at: str = ""
    due_date: Optional[str] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    tags: List[str] = None
    dependencies: List[str] = None
    subtasks: List[str] = None
    notes: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []
        if self.subtasks is None:
            self.subtasks = []
        if self.notes is None:
            self.notes = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

class TaskManager:
    def __init__(self, data_file="tasks.json"):
        self.data_file = os.path.expanduser(f"~/.taskmaster/{data_file}")
        self.backup_dir = os.path.expanduser("~/.taskmaster/backups")
        self.ensure_data_dir()
        self.tasks: Dict[str, Task] = {}
        self.load_tasks()
        
    def ensure_data_dir(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def load_tasks(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = {
                        task_id: Task(**task_data) 
                        for task_id, task_data in data.items()
                    }
        except Exception as e:
            print(f"⚠️  Error loading tasks: {e}")
    
    def save_tasks(self):
        try:
            # Create backup before saving
            if os.path.exists(self.data_file):
                backup_file = os.path.join(
                    self.backup_dir, 
                    f"tasks_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(self.data_file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
            
            with open(self.data_file, 'w') as f:
                json.dump({
                    task_id: asdict(task) 
                    for task_id, task in self.tasks.items()
                }, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving tasks: {e}")
    
    def create_task(self, title: str, **kwargs) -> str:
        task_id = str(uuid.uuid4())[:8]
        task = Task(id=task_id, title=title, **kwargs)
        self.tasks[task_id] = task
        self.save_tasks()
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        # Try to find full task ID from partial ID first
        full_task_id = self.find_task_by_partial_id(task_id)
        if full_task_id:
            return self.tasks.get(full_task_id)
        # Fall back to direct lookup for full ID
        return self.tasks.get(task_id)
    
    def find_task_by_partial_id(self, partial_id: str) -> Optional[str]:
        """Find a task by partial ID (minimum 3 characters).
        Returns the full task ID if found, None if not found or ambiguous.
        """
        if len(partial_id) < 3:
            return None
            
        matching_ids = [task_id for task_id in self.tasks.keys() 
                       if task_id.startswith(partial_id)]
        
        if len(matching_ids) == 1:
            return matching_ids[0]
        elif len(matching_ids) > 1:
            print(f"❌ Ambiguous task ID '{partial_id}'. Matches: {', '.join(matching_ids)}")
            return None
        else:
            return None
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        # Try to find full task ID from partial ID
        full_task_id = self.find_task_by_partial_id(task_id)
        if not full_task_id:
            if task_id not in self.tasks:
                return False
            full_task_id = task_id
            
        task = self.tasks[full_task_id]
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        task.updated_at = datetime.now().isoformat()
        self.save_tasks()
        return True
    
    def delete_task(self, task_id: str) -> bool:
        # Try to find full task ID from partial ID
        full_task_id = self.find_task_by_partial_id(task_id)
        if not full_task_id:
            if task_id not in self.tasks:
                return False
            full_task_id = task_id
            
        del self.tasks[full_task_id]
        self.save_tasks()
        return True
    
    def list_tasks(self, filters: Dict = None) -> List[Task]:
        tasks = list(self.tasks.values())
        
        if filters:
            if 'status' in filters:
                tasks = [t for t in tasks if t.status == filters['status']]
            if 'priority' in filters:
                tasks = [t for t in tasks if t.priority >= filters['priority']]
            if 'category' in filters:
                tasks = [t for t in tasks if t.category == filters['category']]
            if 'tag' in filters:
                tasks = [t for t in tasks if filters['tag'] in t.tags]
            if 'due_soon' in filters and filters['due_soon']:
                tomorrow = (datetime.now() + timedelta(days=1)).date()
                tasks = [t for t in tasks if t.due_date and 
                        datetime.fromisoformat(t.due_date).date() <= tomorrow]
        
        # Sort by priority (high to low), then by due date
        tasks.sort(key=lambda t: (
            -t.priority,
            datetime.fromisoformat(t.due_date) if t.due_date else datetime.max
        ))
        
        return tasks
    
    def search_tasks(self, query: str) -> List[Task]:
        query_lower = query.lower()
        return [
            task for task in self.tasks.values()
            if query_lower in task.title.lower() or
               query_lower in task.description.lower() or
               any(query_lower in tag.lower() for tag in task.tags)
        ]
    
    def add_time_entry(self, task_id: str, hours: float) -> bool:
        # Try to find full task ID from partial ID
        full_task_id = self.find_task_by_partial_id(task_id)
        if not full_task_id:
            if task_id not in self.tasks:
                return False
            full_task_id = task_id
            
        self.tasks[full_task_id].actual_hours += hours
        self.tasks[full_task_id].updated_at = datetime.now().isoformat()
        self.save_tasks()
        return True
    
    def bulk_delete_tasks(self, task_ids: List[str]) -> Dict[str, bool]:
        """Delete multiple tasks. Returns dict of task_id -> success status."""
        results = {}
        deleted_tasks = []
        
        for task_id in task_ids:
            # Try to find full task ID from partial ID
            full_task_id = self.find_task_by_partial_id(task_id)
            if not full_task_id:
                if task_id not in self.tasks:
                    results[task_id] = False
                    continue
                full_task_id = task_id
            
            # Store for deletion
            deleted_tasks.append((task_id, full_task_id))
            results[task_id] = True
        
        # Delete all successful tasks
        for original_id, full_id in deleted_tasks:
            del self.tasks[full_id]
        
        if deleted_tasks:
            self.save_tasks()
        
        return results
    
    def bulk_complete_tasks(self, task_ids: List[str]) -> Dict[str, bool]:
        """Mark multiple tasks as complete. Returns dict of task_id -> success status."""
        results = {}
        updated_tasks = []
        
        for task_id in task_ids:
            # Try to find full task ID from partial ID
            full_task_id = self.find_task_by_partial_id(task_id)
            if not full_task_id:
                if task_id not in self.tasks:
                    results[task_id] = False
                    continue
                full_task_id = task_id
            
            # Update task status
            self.tasks[full_task_id].status = Status.DONE.value
            self.tasks[full_task_id].updated_at = datetime.now().isoformat()
            updated_tasks.append((task_id, full_task_id))
            results[task_id] = True
        
        if updated_tasks:
            self.save_tasks()
        
        return results
    
    def bulk_update_tasks(self, task_ids: List[str], **kwargs) -> Dict[str, bool]:
        """Update multiple tasks with same properties. Returns dict of task_id -> success status."""
        results = {}
        updated_tasks = []
        
        for task_id in task_ids:
            # Try to find full task ID from partial ID
            full_task_id = self.find_task_by_partial_id(task_id)
            if not full_task_id:
                if task_id not in self.tasks:
                    results[task_id] = False
                    continue
                full_task_id = task_id
            
            # Update task properties
            task = self.tasks[full_task_id]
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            task.updated_at = datetime.now().isoformat()
            updated_tasks.append((task_id, full_task_id))
            results[task_id] = True
        
        if updated_tasks:
            self.save_tasks()
        
        return results
    
    def get_analytics(self) -> Dict[str, Any]:
        tasks = list(self.tasks.values())
        total_tasks = len(tasks)
        
        if total_tasks == 0:
            return {"message": "No tasks found"}
        
        status_counts = {}
        priority_counts = {}
        category_counts = {}
        
        for task in tasks:
            status_counts[task.status] = status_counts.get(task.status, 0) + 1
            priority_counts[task.priority] = priority_counts.get(task.priority, 0) + 1
            category_counts[task.category] = category_counts.get(task.category, 0) + 1
        
        completed_tasks = [t for t in tasks if t.status == Status.DONE.value]
        total_estimated = sum(t.estimated_hours for t in tasks)
        total_actual = sum(t.actual_hours for t in tasks)
        
        overdue_tasks = []
        if tasks:
            today = datetime.now().date()
            overdue_tasks = [
                t for t in tasks 
                if t.due_date and datetime.fromisoformat(t.due_date).date() < today
                and t.status != Status.DONE.value
            ]
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": len(completed_tasks),
            "completion_rate": len(completed_tasks) / total_tasks * 100,
            "status_distribution": status_counts,
            "priority_distribution": priority_counts,
            "category_distribution": category_counts,
            "total_estimated_hours": total_estimated,
            "total_actual_hours": total_actual,
            "time_accuracy": (total_actual / total_estimated * 100) if total_estimated > 0 else 0,
            "overdue_tasks": len(overdue_tasks)
        }

class PomodoroTimer:
    def __init__(self, work_minutes=25, break_minutes=5):
        self.work_duration = work_minutes * 60
        self.break_duration = break_minutes * 60
        self.is_running = False
        
    def start_work_session(self, task_id: str, task_manager: TaskManager):
        if self.is_running:
            print("⚠️  Timer is already running!")
            return
            
        self.is_running = True
        print(f"🍅 Starting Pomodoro session for task {task_id}")
        print(f"⏰ Work time: {self.work_duration // 60} minutes")
        
        start_time = time.time()
        
        try:
            time.sleep(self.work_duration)
            end_time = time.time()
            actual_minutes = (end_time - start_time) / 60
            
            # Log time to task
            task_manager.add_time_entry(task_id, actual_minutes / 60)
            
            print(f"✅ Work session completed! Logged {actual_minutes:.1f} minutes")
            print(f"🧘 Take a {self.break_duration // 60} minute break!")
            
        except KeyboardInterrupt:
            end_time = time.time()
            actual_minutes = (end_time - start_time) / 60
            task_manager.add_time_entry(task_id, actual_minutes / 60)
            print(f"\n⏹️  Session stopped. Logged {actual_minutes:.1f} minutes")
        finally:
            self.is_running = False

def format_task(task: Task, detailed: bool = False) -> str:
    priority_symbols = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴"}
    status_symbols = {
        "todo": "⏳",
        "in_progress": "🔄", 
        "blocked": "🚫",
        "done": "✅",
        "cancelled": "❌"
    }
    
    priority_symbol = priority_symbols.get(task.priority, "⚪")
    status_symbol = status_symbols.get(task.status, "❓")
    
    output = f"{priority_symbol} {status_symbol} [{task.id}] {task.title}"
    
    if task.category != "general":
        output += f" ({task.category})"
    
    if task.due_date:
        due = datetime.fromisoformat(task.due_date)
        days_until = (due.date() - datetime.now().date()).days
        if days_until < 0:
            output += f" 🚨 OVERDUE by {-days_until} days"
        elif days_until == 0:
            output += " 📅 Due TODAY"
        elif days_until == 1:
            output += " 📅 Due TOMORROW"
        else:
            output += f" 📅 Due in {days_until} days"
    
    if detailed:
        output += f"\n  Description: {task.description or 'None'}"
        output += f"\n  Tags: {', '.join(task.tags) if task.tags else 'None'}"
        output += f"\n  Time: {task.actual_hours:.1f}h / {task.estimated_hours:.1f}h"
        output += f"\n  Created: {datetime.fromisoformat(task.created_at).strftime('%Y-%m-%d %H:%M')}"
        if task.dependencies:
            output += f"\n  Dependencies: {', '.join(task.dependencies)}"
        if task.subtasks:
            output += f"\n  Subtasks: {len(task.subtasks)} items"
    
    return output

def print_analytics(analytics: Dict[str, Any]):
    print("\n📊 TASK ANALYTICS")
    print("=" * 50)
    print(f"Total Tasks: {analytics['total_tasks']}")
    print(f"Completed: {analytics['completed_tasks']} ({analytics['completion_rate']:.1f}%)")
    print(f"Overdue Tasks: {analytics['overdue_tasks']}")
    print(f"Time Tracking: {analytics['total_actual_hours']:.1f}h actual / {analytics['total_estimated_hours']:.1f}h estimated")
    if analytics['total_estimated_hours'] > 0:
        print(f"Time Accuracy: {analytics['time_accuracy']:.1f}%")
    
    print("\n📋 Status Distribution:")
    for status, count in analytics['status_distribution'].items():
        print(f"  {status}: {count}")
    
    print("\n🎯 Priority Distribution:")
    priority_names = {1: "Low", 2: "Medium", 3: "High", 4: "Urgent"}
    for priority, count in analytics['priority_distribution'].items():
        name = priority_names.get(priority, f"Priority {priority}")
        print(f"  {name}: {count}")

def main():
    parser = argparse.ArgumentParser(description="TaskMaster - Powerful Task Management")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create task
    create_parser = subparsers.add_parser('create', help='Create a new task')
    create_parser.add_argument('title', help='Task title')
    create_parser.add_argument('-d', '--description', help='Task description')
    create_parser.add_argument('-p', '--priority', type=int, choices=[1,2,3,4], default=2, help='Priority (1=Low, 2=Medium, 3=High, 4=Urgent)')
    create_parser.add_argument('-c', '--category', default='general', help='Task category')
    create_parser.add_argument('--due', help='Due date (YYYY-MM-DD)')
    create_parser.add_argument('-e', '--estimate', type=float, help='Estimated hours')
    create_parser.add_argument('-t', '--tags', nargs='+', help='Tags')
    
    # List tasks
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('-s', '--status', help='Filter by status')
    list_parser.add_argument('-p', '--priority', type=int, help='Filter by minimum priority')
    list_parser.add_argument('-c', '--category', help='Filter by category')
    list_parser.add_argument('--tag', help='Filter by tag')
    list_parser.add_argument('--due-soon', action='store_true', help='Show tasks due soon')
    list_parser.add_argument('--detailed', action='store_true', help='Show detailed information')
    
    # Update task
    update_parser = subparsers.add_parser('update', help='Update a task')
    update_parser.add_argument('task_id', help='Task ID')
    update_parser.add_argument('-t', '--title', help='New title')
    update_parser.add_argument('-d', '--description', help='New description')
    update_parser.add_argument('-s', '--status', choices=['todo', 'in_progress', 'blocked', 'done', 'cancelled'], help='New status')
    update_parser.add_argument('-p', '--priority', type=int, choices=[1,2,3,4], help='New priority')
    update_parser.add_argument('-c', '--category', help='New category')
    update_parser.add_argument('--due', help='New due date (YYYY-MM-DD)')
    
    # Bulk update tasks
    bulk_update_parser = subparsers.add_parser('bulk-update', help='Update multiple tasks with same properties')
    bulk_update_parser.add_argument('task_ids', nargs='+', help='Task ID(s) - supports multiple IDs')
    bulk_update_parser.add_argument('-s', '--status', choices=['todo', 'in_progress', 'blocked', 'done', 'cancelled'], help='New status')
    bulk_update_parser.add_argument('-p', '--priority', type=int, choices=[1,2,3,4], help='New priority')
    bulk_update_parser.add_argument('-c', '--category', help='New category')
    bulk_update_parser.add_argument('--due', help='New due date (YYYY-MM-DD)')
    
    # Complete task
    complete_parser = subparsers.add_parser('complete', help='Mark task(s) as complete')
    complete_parser.add_argument('task_ids', nargs='+', help='Task ID(s) - supports multiple IDs')
    
    # Delete task
    delete_parser = subparsers.add_parser('delete', help='Delete task(s)')
    delete_parser.add_argument('task_ids', nargs='+', help='Task ID(s) - supports multiple IDs')
    
    # Add remove as alias for delete
    remove_parser = subparsers.add_parser('remove', help='Remove task(s) (alias for delete)')
    remove_parser.add_argument('task_ids', nargs='+', help='Task ID(s) - supports multiple IDs')
    
    # Search tasks
    search_parser = subparsers.add_parser('search', help='Search tasks')
    search_parser.add_argument('query', help='Search query')
    
    # Show task details
    show_parser = subparsers.add_parser('show', help='Show task details')
    show_parser.add_argument('task_id', help='Task ID')
    
    # Time tracking
    time_parser = subparsers.add_parser('time', help='Log time to a task')
    time_parser.add_argument('task_id', help='Task ID')
    time_parser.add_argument('hours', type=float, help='Hours worked')
    
    # Pomodoro timer
    pomodoro_parser = subparsers.add_parser('pomodoro', help='Start Pomodoro timer')
    pomodoro_parser.add_argument('task_id', help='Task ID')
    pomodoro_parser.add_argument('-w', '--work', type=int, default=25, help='Work minutes (default: 25)')
    pomodoro_parser.add_argument('-b', '--break', type=int, default=5, help='Break minutes (default: 5)')
    
    # Analytics
    subparsers.add_parser('analytics', help='Show analytics')
    
    # Export/Import
    export_parser = subparsers.add_parser('export', help='Export tasks')
    export_parser.add_argument('file', help='Export file path')
    
    import_parser = subparsers.add_parser('import', help='Import tasks')
    import_parser.add_argument('file', help='Import file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    tm = TaskManager()
    
    if args.command == 'create':
        kwargs = {}
        if args.description:
            kwargs['description'] = args.description
        if args.priority:
            kwargs['priority'] = args.priority
        if args.category:
            kwargs['category'] = args.category
        if args.due:
            kwargs['due_date'] = args.due
        if args.estimate:
            kwargs['estimated_hours'] = args.estimate
        if args.tags:
            kwargs['tags'] = args.tags
            
        task_id = tm.create_task(args.title, **kwargs)
        print(f"✅ Created task [{task_id}]: {args.title}")
    
    elif args.command == 'list':
        filters = {}
        if args.status:
            filters['status'] = args.status
        if args.priority:
            filters['priority'] = args.priority
        if args.category:
            filters['category'] = args.category
        if args.tag:
            filters['tag'] = args.tag
        if args.due_soon:
            filters['due_soon'] = True
            
        tasks = tm.list_tasks(filters)
        if tasks:
            print(f"\n📋 Found {len(tasks)} tasks:\n")
            for task in tasks:
                print(format_task(task, args.detailed))
        else:
            print("No tasks found.")
    
    elif args.command == 'update':
        kwargs = {}
        if args.title:
            kwargs['title'] = args.title
        if args.description:
            kwargs['description'] = args.description
        if args.status:
            kwargs['status'] = args.status
        if args.priority:
            kwargs['priority'] = args.priority
        if args.category:
            kwargs['category'] = args.category
        if hasattr(args, 'due') and args.due:
            kwargs['due_date'] = args.due
            
        # Find full task ID for display
        full_task_id = tm.find_task_by_partial_id(args.task_id)
        if not full_task_id and args.task_id not in tm.tasks:
            print(f"❌ Task [{args.task_id}] not found")
        elif tm.update_task(args.task_id, **kwargs):
            display_id = full_task_id if full_task_id else args.task_id
            print(f"✅ Updated task [{display_id}]")
        else:
            print(f"❌ Task [{args.task_id}] not found")
    
    elif args.command == 'bulk-update':
        kwargs = {}
        if args.status:
            kwargs['status'] = args.status
        if args.priority:
            kwargs['priority'] = args.priority
        if args.category:
            kwargs['category'] = args.category
        if hasattr(args, 'due') and args.due:
            kwargs['due_date'] = args.due
            
        if not kwargs:
            print("❌ No update properties specified. Use -s, -p, -c, or --due to specify changes.")
            return
            
        results = tm.bulk_update_tasks(args.task_ids, **kwargs)
        successful = [task_id for task_id, success in results.items() if success]
        failed = [task_id for task_id, success in results.items() if not success]
        
        if successful:
            # Show what properties were updated
            updates = []
            if args.status:
                updates.append(f"status={args.status}")
            if args.priority:
                updates.append(f"priority={args.priority}")
            if args.category:
                updates.append(f"category={args.category}")
            if hasattr(args, 'due') and args.due:
                updates.append(f"due={args.due}")
            
            update_str = ', '.join(updates)
            print(f"✅ Updated {len(successful)} task(s) with {update_str}: {', '.join(successful)}")
        if failed:
            print(f"❌ Failed to find {len(failed)} task(s): {', '.join(failed)}")
    
    elif args.command == 'complete':
        if len(args.task_ids) == 1:
            # Single task - existing logic
            task_id = args.task_ids[0]
            full_task_id = tm.find_task_by_partial_id(task_id)
            if not full_task_id and task_id not in tm.tasks:
                print(f"❌ Task [{task_id}] not found")
            elif tm.update_task(task_id, status=Status.DONE.value):
                display_id = full_task_id if full_task_id else task_id
                print(f"🎉 Completed task [{display_id}]")
            else:
                print(f"❌ Task [{task_id}] not found")
        else:
            # Multiple tasks - bulk operation
            results = tm.bulk_complete_tasks(args.task_ids)
            successful = [task_id for task_id, success in results.items() if success]
            failed = [task_id for task_id, success in results.items() if not success]
            
            if successful:
                print(f"🎉 Completed {len(successful)} task(s): {', '.join(successful)}")
            if failed:
                print(f"❌ Failed to find {len(failed)} task(s): {', '.join(failed)}")
    
    elif args.command == 'delete' or args.command == 'remove':
        if len(args.task_ids) == 1:
            # Single task - existing logic
            task_id = args.task_ids[0]
            full_task_id = tm.find_task_by_partial_id(task_id)
            if not full_task_id and task_id not in tm.tasks:
                print(f"❌ Task [{task_id}] not found")
            elif tm.delete_task(task_id):
                display_id = full_task_id if full_task_id else task_id
                print(f"🗑️  Deleted task [{display_id}]")
            else:
                print(f"❌ Task [{task_id}] not found")
        else:
            # Multiple tasks - bulk operation
            results = tm.bulk_delete_tasks(args.task_ids)
            successful = [task_id for task_id, success in results.items() if success]
            failed = [task_id for task_id, success in results.items() if not success]
            
            if successful:
                print(f"🗑️  Deleted {len(successful)} task(s): {', '.join(successful)}")
            if failed:
                print(f"❌ Failed to find {len(failed)} task(s): {', '.join(failed)}")
    
    elif args.command == 'search':
        tasks = tm.search_tasks(args.query)
        if tasks:
            print(f"\n🔍 Found {len(tasks)} tasks matching '{args.query}':\n")
            for task in tasks:
                print(format_task(task))
        else:
            print(f"No tasks found matching '{args.query}'")
    
    elif args.command == 'show':
        task = tm.get_task(args.task_id)
        if task:
            print(format_task(task, detailed=True))
        else:
            print(f"❌ Task [{args.task_id}] not found")
    
    elif args.command == 'time':
        # Find full task ID for display
        full_task_id = tm.find_task_by_partial_id(args.task_id)
        if not full_task_id and args.task_id not in tm.tasks:
            print(f"❌ Task [{args.task_id}] not found")
        elif tm.add_time_entry(args.task_id, args.hours):
            display_id = full_task_id if full_task_id else args.task_id
            print(f"⏱️  Logged {args.hours} hours to task [{display_id}]")
        else:
            print(f"❌ Task [{args.task_id}] not found")
    
    elif args.command == 'pomodoro':
        task = tm.get_task(args.task_id)
        if not task:
            print(f"❌ Task [{args.task_id}] not found")
            return
            
        # Find full task ID for the timer
        full_task_id = tm.find_task_by_partial_id(args.task_id)
        timer_task_id = full_task_id if full_task_id else args.task_id
        
        timer = PomodoroTimer(args.work, getattr(args, 'break'))
        timer.start_work_session(timer_task_id, tm)
    
    elif args.command == 'analytics':
        analytics = tm.get_analytics()
        print_analytics(analytics)
    
    elif args.command == 'export':
        try:
            with open(args.file, 'w') as f:
                json.dump({
                    task_id: asdict(task) 
                    for task_id, task in tm.tasks.items()
                }, f, indent=2)
            print(f"✅ Exported {len(tm.tasks)} tasks to {args.file}")
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    elif args.command == 'import':
        try:
            with open(args.file, 'r') as f:
                data = json.load(f)
                for task_id, task_data in data.items():
                    tm.tasks[task_id] = Task(**task_data)
            tm.save_tasks()
            print(f"✅ Imported {len(data)} tasks from {args.file}")
        except Exception as e:
            print(f"❌ Import failed: {e}")

if __name__ == "__main__":
    main()