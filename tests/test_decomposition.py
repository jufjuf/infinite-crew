#!/usr/bin/env python3
"""
Test task decomposition functionality
"""

import os
import sys
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from master.main import decompose

# Test cases
test_cases = [
    {
        "name": "Simple task",
        "prompt": "Write a hello world program",
        "expected_count": 1
    },
    {
        "name": "Medium complexity",
        "prompt": "Create a website for a restaurant including menu, about page, and contact form",
        "expected_count": (2, 4)  # Between 2-4 subtasks
    },
    {
        "name": "Complex mission",
        "prompt": "Research quantum computing, write a beginner's guide, create code examples, and design a presentation",
        "expected_count": (3, 4)  # Between 3-4 subtasks
    }
]

print("Testing task decomposition...\n")

for test in test_cases:
    print(f"Test: {test['name']}")
    print(f"Prompt: {test['prompt']}")
    
    try:
        result = decompose(test['prompt'])
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Check result count
        if isinstance(test['expected_count'], int):
            if len(result) == test['expected_count']:
                print("✅ PASS: Correct number of subtasks")
            else:
                print(f"❌ FAIL: Expected {test['expected_count']} subtasks, got {len(result)}")
        else:
            min_count, max_count = test['expected_count']
            if min_count <= len(result) <= max_count:
                print(f"✅ PASS: Subtask count in range [{min_count}, {max_count}]")
            else:
                print(f"❌ FAIL: Expected {min_count}-{max_count} subtasks, got {len(result)}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("-" * 60 + "\n")

print("Decomposition tests complete!")
