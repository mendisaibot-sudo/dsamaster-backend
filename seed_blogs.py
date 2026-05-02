#!/usr/bin/env python3
"""Seed the blog database with sample posts."""

import os
import sys

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.blog_storage import create_post, get_all_posts
from app.models.blog import BlogPost

SAMPLE_POSTS = [
    {
        "slug": "arrays-101",
        "title": "Arrays 101: The Foundation of Data Structures",
        "content": """# Arrays 101: The Foundation of Data Structures

Arrays are one of the most fundamental data structures in computer science. They store elements in contiguous memory locations, allowing efficient access by index.

## Time Complexity

| Operation | Time |
|-----------|------|
| Access    | O(1) |
| Search    | O(n) |
| Insert    | O(n) |
| Delete    | O(n) |

## Common Problems
- Two Sum
- Best Time to Buy and Sell Stock
- Contains Duplicate
- Product of Array Except Self

Learning arrays well sets you up for success with more complex structures like strings, matrices, and even trees!""",
        "excerpt": "Master the fundamentals of arrays with this comprehensive beginner's guide.",
        "date": "2024-01-15",
        "readTime": 8,
        "tags": ["arrays", "data-structures", "beginner"],
        "difficulty": "Easy",
        "author": "Admin"
    },
    {
        "slug": "linked-lists-explained",
        "title": "Linked Lists Explained: Pointers & Nodes",
        "content": """# Linked Lists Explained

Unlike arrays, linked lists store elements in non-contiguous memory, connected by pointers. Each node contains data and a reference to the next node.

## Types of Linked Lists
- Singly Linked List
- Doubly Linked List
- Circular Linked List

## When to Use Linked Lists
- Frequent insertions/deletions
- Unknown data size
- Implementing stacks, queues, LRU cache

The key insight: linked lists sacrifice O(1) random access for O(1) insertion/deletion at known positions.""",
        "excerpt": "Understand when and why to use linked lists over arrays.",
        "date": "2024-01-22",
        "readTime": 12,
        "tags": ["linked-list", "data-structures", "pointers"],
        "difficulty": "Medium",
        "author": "Admin"
    },
    {
        "slug": "binary-search-masterclass",
        "title": "Binary Search Masterclass",
        "content": """# Binary Search Masterclass

Binary search is an O(log n) search algorithm that works on sorted arrays.

## The Pattern

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

## Variations
- Find first/last occurrence
- Find minimum in rotated array
- Search in 2D matrix
- Answer-the-answer problems

Master binary search and you unlock a whole category of problems!""",
        "excerpt": "Learn binary search patterns that go beyond the basic implementation.",
        "date": "2024-02-01",
        "readTime": 10,
        "tags": ["binary-search", "algorithms", "intermediate"],
        "difficulty": "Medium",
        "author": "Admin"
    },
    {
        "slug": "graphs-dfs-bfs",
        "title": "Graph Traversal: DFS vs BFS",
        "content": """# Graph Traversal: DFS vs BFS

Graphs are everywhere: social networks, maps, dependency trees. The two fundamental traversal strategies are DFS and BFS.

## Depth-First Search (DFS)
- Uses a stack (recursion or explicit)
- Explores as far as possible before backtracking
- Good for: path finding, topological sort, detecting cycles

## Breadth-First Search (BFS)
- Uses a queue
- Explores all neighbors before going deeper
- Good for: shortest path in unweighted graphs, level-order traversal

## Choosing Between Them
- Shortest path? → BFS
- All paths? → DFS
- Cycles detection? → Both work
- Memory concerns? → DFS typically uses less

## Common Patterns
- Island counting
- Clone graph
- Word ladder
- Course schedule""",
        "excerpt": "Choosing the right graph traversal strategy for your problem.",
        "date": "2024-02-15",
        "readTime": 15,
        "tags": ["graphs", "dfs", "bfs", "algorithms"],
        "difficulty": "Hard",
        "author": "Admin"
    },
    {
        "slug": "dynamic-programming-intro",
        "title": "Dynamic Programming: From Recursion to DP",
        "content": """# Dynamic Programming

Dynamic Programming (DP) is an optimization technique used when a problem can be broken into overlapping subproblems.

## The Two Approaches

### Top-Down (Memoization)
- Start from the original problem
- Cache results of subproblems
- Natural recursive thinking

### Bottom-Up (Tabulation)
- Start from smallest subproblems
- Build up to the original problem
- Often more space-efficient

## The 5 Step Framework
1. Define state (what does dp[i] represent?)
2. Identify the recurrence relation
3. Set base cases
4. Determine computation order
5. Extract the answer

## Classic Problems
- Fibonacci
- Climbing Stairs
- Longest Common Subsequence
- Edit Distance
- Knapsack

""",
        "excerpt": "A step-by-step framework for solving dynamic programming problems.",
        "date": "2024-03-01",
        "readTime": 20,
        "tags": ["dynamic-programming", "algorithms", "advanced"],
        "difficulty": "Hard",
        "author": "Admin"
    }
]


def seed():
    existing = get_all_posts(include_unpublished=True)
    if existing:
        print(f"Blogs already seeded ({len(existing)} posts found). Skipping.")
        return

    for post_data in SAMPLE_POSTS:
        post = BlogPost(**post_data)
        create_post(post)
        print(f"Created: {post.title}")

    print(f"\nSeeded {len(SAMPLE_POSTS)} blog posts successfully!")


if __name__ == "__main__":
    seed()
