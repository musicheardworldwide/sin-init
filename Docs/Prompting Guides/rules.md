# Influencing Code Generation Through Instruction Rules

## Overview
System instructions can precisely control code generation [[sin/1. Initialization/Docs/Prompting Guides/output]] by specifying documentation requirements. This guide demonstrates how requiring docstrings affects Python code quality and usability.

## Code Generation Examples

### Scenario: A* Pathfinding Algorithm Implementation

---

## With Docstring Requirements

**System Instructions:**
```python
When generating code, make sure to include docstrings explaining:
- Inputs and their types
- Outputs and their types
- Usage examples
- Class/method purposes
```

**Model Output Characteristics:**
- **Documentation:** Comprehensive docstrings
- **Readability:** High (self-documenting)
- **Maintainability:** Excellent
- **Usage Clarity:** Explicit examples provided
- **Structure:** Well-organized components

**Example Response:**
````python
import heapq

class Node:
    """
    Represents a node in the grid for A* pathfinding.
    
    Attributes:
        x (int): The x-coordinate of the node
        y (int): The y-coordinate of the node  
        parent (Node): Parent node in path (default None)
        g (int): Cost from start node (default 0)
        h (int): Heuristic to end node (default 0)
    """
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent
        self.g = 0
        self.h = 0

    def __lt__(self, other):
        """Node comparison based on f-score (g + h)"""
        return (self.g + self.h) < (other.g + other.h)


def a_star(grid, start, end):
    """
    Implements A* pathfinding algorithm.
    
    Args:
        grid (list[list[int]]): 2D array where 0=walkable, 1=obstacle
        start (tuple[int, int]): (x,y) start coordinates  
        end (tuple[int, int]): (x,y) end coordinates
        
    Returns:
        list[tuple[int, int]]: Path as coordinate list, or None if no path
        
    Example:
        >>> grid = [[0,0], [0,1]]
        >>> a_star(grid, (0,0), (1,0))
        [(0, 0), (1, 0)]
    """
    # Implementation...
````

**Key Advantages:**
✅ Self-documenting code  
✅ Clear parameter expectations  
✅ Example usage provided  
✅ Easier maintenance  
✅ Better IDE support (type hints)  

---

## Without Docstring Requirements

**System Instructions:**
```python
Only generate code, do not include any docstrings
```

**Model Output Characteristics:**
- **Documentation:** None
- **Readability:** Requires code analysis  
- **Maintainability:** Poor long-term
- **Usage Clarity:** Must infer from implementation
- **Structure:** Functional but opaque

**Example Response:**
````python
import heapq

class Node:
    def __init__(self, pos, parent=None):
        self.pos = pos
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f

def astar(maze, start, end):
    open = []
    closed = set()
    heapq.heappush(open, Node(start))
    
    while open:
        current = heapq.heappop(open)
        if current.pos == end:
            path = []
            while current:
                path.append(current.pos)
                current = current.parent
            return path[::-1]
        
        closed.add(current.pos)
        for move in [(0,1),(1,0),(0,-1),(-1,0)]:
            next_pos = (current.pos[0]+move[0], current.pos[1]+move[1])
            # ...continued implementation
````

**Key Limitations:**
✗ No usage documentation  
✗ Parameter purposes unclear  
✗ No examples provided  
✗ Harder to modify later  
✗ Type expectations ambiguous  

---

## Comparison Table

| Feature                | With Docstrings | Without Docstrings |
|------------------------|-----------------|--------------------|
| Self-documenting       | ✅ Yes          | ✗ No               |
| Type Hints             | ✅ Included     | ✗ Missing          |
| Usage Examples         | ✅ Provided     | ✗ None             |
| Maintenance Cost       | ✅ Low          | ✗ High             |
| Onboarding Time        | ✅ Fast         | ✗ Slow             |
| IDE Support            | ✅ Excellent    | ✗ Limited          |
| Collaboration Friendly | ✅ Yes          | ✗ No               |

---

## Best Practices for Code Generation Rules

1. **Always Require:**
   ```markdown
   - Function/method docstrings
   - Parameter/return type hints  
   - Usage examples for complex functions
   - Class-level documentation
   ```

2. **Recommended Structure:**
   ````python
   def function_name(param: type) -> return_type:
       """Brief description
       
       Extended explanation if needed
       
       Args:
           param (type): Description
           
       Returns:
           return_type: Description
           
       Raises:
           ErrorType: When/why raised
           
       Example:
           >>> sample_usage()
           expected_output
       """
   ````

3. **Special Cases:**
   ```markdown
   - For internal/private methods: "_single_leading_underscore"
   - For property decorators: Include attribute docs
   - For abstract methods: Document expected behavior
   ```

4. **Validation Rules:**
   ````markdown
   ```system
   When generating Python code:
   1. Verify all functions/methods have docstrings
   2. Confirm type hints exist for all parameters/returns
   3. Validate example usage matches function signature
   4. Reject any code submissions missing these elements
   ```
   ````

---

## Instruction Templates

### Basic Template
````markdown
```system
You are a Python code generation assistant. All output must:

1. Include Google-style docstrings for all:
   - Classes
   - Methods  
   - Functions
   - Properties

2. Provide type hints for:
   - Parameters
   - Return values
   - Class attributes

3. Show 1-2 usage examples per public function

4. Document all:
   - Edge cases
   - Error conditions
   - Special behaviors
```
````

### Advanced Template
````markdown
```system
You are a senior Python engineer generating production-ready code. 

Code Requirements:
- NumPy-style docstrings with:
  • Parameters section
  • Returns section
  • Examples section
  • Notes section where applicable

- Type hints must:
  • Use Python 3.10+ syntax (| for unions)
  • Include generics (list[str] etc)
  • Specify None possibilities

- Include:
  • Doctest examples
  • Error case documentation
  • Performance characteristics
  • Thread safety notes

Validation:
1. Lint with pycodestyle
2. Verify types with mypy
3. Confirm examples execute
```
````

This structured comparison demonstrates how explicit documentation requirements in system instructions significantly impact code quality and long-term maintainability.