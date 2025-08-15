#!/usr/bin/env python3

"""Debug script to analyze the AST structure of the routing service"""

import ast
import sys
import os

# Read the file fresh
file_path = "/Users/frank/RouteForceRouting/app/services/routing_service.py"
print(f"Reading file: {file_path}")

with open(file_path, "r") as f:
    content = f.read()

print(f"File size: {len(content)} characters")
print(f"File lines: {len(content.split(chr(10)))} lines")

# Parse the AST
tree = ast.parse(content)

# Find the RoutingService class
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "RoutingService":
        print(f"Found RoutingService class at line {node.lineno}")

        # Find the __init__ method
        for method in node.body:
            if (
                isinstance(method, ast.FunctionDef)
                and method.name == "__init__"
            ):
                print(f"Found __init__ method at line {method.lineno}")
                print(f"Method ends at line {method.end_lineno}")

                # Print the method body lines
                lines = content.split("\n")
                print("Method body:")
                for i in range(method.lineno - 1, method.end_lineno):
                    if i < len(lines):
                        print(f"{i+1:3d}: {lines[i]}")

                break
        break
