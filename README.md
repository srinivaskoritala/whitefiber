# Task Scheduler

A command line tool to schedule and optionally run a series of tasks in parallel, according to a task list specification with dependencies.

**Author**: Srinivas k

## Features

- **Dependency Management**: Tasks can depend on other tasks, ensuring proper execution order
- **Parallel Execution**: Independent tasks run simultaneously for optimal performance
- **Validation**: Check task lists for circular dependencies and missing references
- **Runtime Analysis**: Compare expected vs actual execution times
- **CSV Input**: Simple text-based task specification format
- **Error Handling**: Comprehensive validation with clear error messages

## Quick Start

```bash
# Clone the repository
git clone git@github.com:srinivasaskoritala/whitefiber.git
cd whitefiber

# Run all tests (recommended first step)
./test_scheduler.sh

# Test individual functionality
python3 task_scheduler.py sample_tasks.csv --validate
python3 task_scheduler.py sample_tasks.csv --run
```

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## Installation

1. Clone or download the repository
2. Ensure Python 3.6+ is installed
3. Make the script executable (optional):
   ```bash
   chmod +x task_scheduler.py
   ```

## Usage

### Basic Syntax

```bash
python3 task_scheduler.py <task_file> [options]
```

### Options

- `--validate`: Validate the task list and show expected runtime without running tasks
- `--run`: Execute the tasks and show actual vs expected runtime
- No options: Default behavior - validate and show execution plan

### Task File Format

The task file should be a CSV file with the following columns:

1. **Task Name**: Unique identifier for the task
2. **Duration**: Expected execution time in seconds
3. **Dependencies**: Comma-separated list of task names that must complete first (optional)

Example:
```csv
setup,2,
compile,5,setup
test,3,compile
deploy,2,test
```

### Examples

#### Validate a task list
```bash
python3 task_scheduler.py sample_tasks.csv --validate
```

#### Run tasks and measure performance
```bash
python3 task_scheduler.py sample_tasks.csv --run
```

#### Just view the execution plan
```bash
python3 task_scheduler.py sample_tasks.csv
```

## Sample Task Files

- `sample_tasks.csv`: Simple linear dependency chain (5 tasks, 12s total)
- `complex_tasks.csv`: Demonstrates parallel execution with multiple independent task chains (12 tasks, 13s total)

## How It Works

1. **Parsing**: Reads CSV file and creates Task objects
2. **Validation**: Checks for circular dependencies using topological sort
3. **Scheduling**: Calculates optimal execution order and expected runtime
4. **Execution**: Runs tasks in parallel threads, respecting dependencies
5. **Analysis**: Compares actual vs expected performance

## Algorithm Details

- **Topological Sort**: Uses Kahn's algorithm to determine execution order
- **Critical Path**: Calculates expected runtime based on longest dependency chain
- **Parallel Execution**: Starts tasks as soon as their dependencies are satisfied
- **Thread Management**: Uses Python threading for concurrent task execution

## Testing

### Quick Test Script

Run all tests at once:
```bash
./test_scheduler.sh
```

### Individual Test Commands

```bash
# Test validation
python3 task_scheduler.py sample_tasks.csv --validate

# Test execution (will take ~12 seconds)
python3 task_scheduler.py sample_tasks.csv --run

# Test complex parallel execution
python3 task_scheduler.py complex_tasks.csv --run
```


## Error Handling

The tool provides clear error messages for common issues:

- **Missing dependencies**: When a task references a non-existent task
- **Circular dependencies**: When tasks form dependency cycles
- **Invalid file format**: When CSV parsing fails
- **Invalid durations**: When duration values are not integers

### Error Examples

```bash
# Missing dependency
$ python3 task_scheduler.py invalid_tasks.csv --validate
Task validation failed:
  - Task 'invalid_task' depends on missing task 'missing_task'

# Circular dependency
$ python3 task_scheduler.py circular_tasks.csv --validate
Task validation failed:
  - Circular dependency detected: Circular dependency detected
```
