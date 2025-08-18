#!/bin/bash
echo "Testing Task Scheduler..."
echo "1. Testing validation..."
python3 task_scheduler.py sample_tasks.csv --validate
echo -e "\n2. Testing execution..."
python3 task_scheduler.py sample_tasks.csv --run
echo -e "\n3. Testing complex parallel execution..."
python3 task_scheduler.py complex_tasks.csv --validate
