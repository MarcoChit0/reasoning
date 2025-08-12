import sys

size = int(sys.argv[1]) if len(sys.argv) > 1 else 1

"""
size == 1

R..W..G
...W...
...L...

size == 2

R..W...L...
...W...W...
...L...W..G

size == 3

R..W...L...W..G
...W...W...W...
...L...W...L...

continue
"""

grid = 1