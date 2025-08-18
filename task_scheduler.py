#!/usr/bin/env python3
import argparse, csv, sys, time, threading
from collections import defaultdict, deque

class Task:
    def __init__(self, name, duration, dependencies):
        self.name = name
        self.duration = duration
        self.dependencies = dependencies
        self.start_time = None
        self.end_time = None
        self.actual_duration = None

class TaskScheduler:
    def __init__(self):
        self.tasks = {}
        self.execution_order = []
        self.expected_runtime = 0
        self.actual_runtime = 0
    
    def add_task(self, task):
        self.tasks[task.name] = task
    
    def validate_tasks(self):
        errors = []
        for task_name, task in self.tasks.items():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    errors.append(f"Task '{task_name}' depends on missing task '{dep}'")
        
        if errors:
            return False, errors
        
        try:
            self._topological_sort()
        except ValueError as e:
            errors.append(f"Circular dependency detected: {e}")
            return False, errors
        
        return True, []
    
    def _topological_sort(self):
        in_degree = {name: 0 for name in self.tasks}
        graph = defaultdict(list)
        
        for task_name, task in self.tasks.items():
            for dep in task.dependencies:
                graph[dep].append(task_name)
                in_degree[task_name] += 1
        
        queue = deque([name for name, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(self.tasks):
            raise ValueError("Circular dependency detected")
        
        self.execution_order = result
        return result
    
    def calculate_expected_runtime(self):
        if not self.execution_order:
            self._topological_sort()
        
        start_times = {}
        for task_name in self.execution_order:
            task = self.tasks[task_name]
            if not task.dependencies:
                start_times[task_name] = 0
            else:
                start_times[task_name] = max(
                    start_times[dep] + self.tasks[dep].duration 
                    for dep in task.dependencies
                )
        
        total_runtime = 0
        for task_name in self.execution_order:
            task = self.tasks[task_name]
            end_time = start_times[task_name] + task.duration
            total_runtime = max(total_runtime, end_time)
        
        self.expected_runtime = total_runtime
        return total_runtime
    
    def run_tasks(self):
        if not self.execution_order:
            self._topological_sort()
        
        self.start_time = time.time()
        active_tasks = {}
        completed_tasks = set()
        
        for task_name in self.execution_order:
            task = self.tasks[task_name]
            if not task.dependencies:
                self._start_task(task, active_tasks)
        
        while len(completed_tasks) < len(self.tasks):
            completed = []
            for task_name, (thread, start_time) in active_tasks.items():
                if not thread.is_alive():
                    completed.append(task_name)
                    task = self.tasks[task_name]
                    task.end_time = time.time()
                    task.actual_duration = task.end_time - start_time
                    completed_tasks.add(task_name)
            
            for task_name in completed:
                del active_tasks[task_name]
            
            for task_name in self.execution_order:
                task = self.tasks[task_name]
                if (task_name not in active_tasks and 
                    task_name not in completed_tasks and
                    all(dep in completed_tasks for dep in task.dependencies)):
                    self._start_task(task, active_tasks)
            
            time.sleep(0.01)
        
        self.end_time = time.time()
        self.actual_runtime = self.end_time - self.start_time
        return self.actual_runtime
    
    def _start_task(self, task, active_tasks):
        task.start_time = time.time()
        
        def task_worker():
            time.sleep(task.duration)
        
        thread = threading.Thread(target=task_worker)
        thread.start()
        active_tasks[task.name] = (thread, task.start_time)
    
    def print_execution_plan(self):
        print(f"Expected total runtime: {self.expected_runtime} seconds")
        print("Execution order:")
        for i, task_name in enumerate(self.execution_order, 1):
            task = self.tasks[task_name]
            deps_str = ", ".join(task.dependencies) if task.dependencies else "none"
            print(f"{i}. {task_name} (duration: {task.duration}s, dependencies: {deps_str})")
    
    def print_execution_results(self):
        print("Execution Results:")
        print(f"Expected runtime: {self.expected_runtime:.2f} seconds")
        print(f"Actual runtime: {self.actual_runtime:.2f} seconds")
        print(f"Difference: {self.actual_runtime - self.expected_runtime:.2f} seconds")
        
        print("Task execution details:")
        for task_name in self.execution_order:
            task = self.tasks[task_name]
            if task.actual_duration is not None:
                diff = task.actual_duration - task.duration
                print(f"{task_name}: expected {task.duration}s, actual {task.actual_duration:.2f}s, diff {diff:.2f}s")

def parse_task_file(filename):
    tasks = []
    
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row_num, row in enumerate(reader, 1):
                if not row or row[0].strip().startswith('#'):
                    continue
                
                if len(row) < 2:
                    print(f"Warning: Skipping invalid row {row_num}: {row}")
                    continue
                
                name = row[0].strip()
                try:
                    duration = int(row[1].strip())
                except ValueError:
                    print(f"Warning: Invalid duration in row {row_num}: {row[1]}")
                    continue
                
                dependencies = []
                if len(row) > 2 and row[2].strip():
                    dependencies = [dep.strip() for dep in row[2].split(',') if dep.strip()]
                
                tasks.append(Task(name, duration, dependencies))
    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    return tasks

def main():
    parser = argparse.ArgumentParser(
        description="Task Scheduler - Schedule and run tasks in parallel according to dependencies"
    )
    parser.add_argument(
        "task_file", 
        help="CSV file containing task definitions (name, duration, dependencies)"
    )
    parser.add_argument(
        "--validate", 
        action="store_true",
        help="Validate the task list and show expected runtime without running tasks"
    )
    parser.add_argument(
        "--run", 
        action="store_true",
        help="Run the tasks and show actual vs expected runtime"
    )
    
    args = parser.parse_args()
    
    tasks = parse_task_file(args.task_file)
    if not tasks:
        print("No valid tasks found in file")
        sys.exit(1)
    
    scheduler = TaskScheduler()
    for task in tasks:
        scheduler.add_task(task)
    
    is_valid, errors = scheduler.validate_tasks()
    if not is_valid:
        print("Task validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    
    expected_runtime = scheduler.calculate_expected_runtime()
    
    if args.validate:
        scheduler.print_execution_plan()
        return
    
    if args.run:
        print("Running tasks...")
        scheduler.print_execution_plan()
        print("Starting execution...")
        
        actual_runtime = scheduler.run_tasks()
        scheduler.print_execution_results()
        return
    
    scheduler.print_execution_plan()
    print("Use --run to execute tasks or --validate to just validate")

if __name__ == "__main__":
    main()
