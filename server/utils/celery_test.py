import sys
import os

# Ensure the project root is in PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))  # Adjust if needed
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the task
from utils.notification_tasks import test_task

# Trigger the test task asynchronously
result = test_task.delay()
print(f"Task triggered with ID: {result.id}")

# Wait for the result (optional)
print("Waiting for task result...")
print(f"Task result: {result.get(timeout=10)}")
