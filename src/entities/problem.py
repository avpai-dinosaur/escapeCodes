"""
problem.py
Representations of LeetCode problems
"""

import ast
from abc import ABC, abstractmethod

class Parameter:
    """Class representing parameter in a problem's input."""
    
    def __init__(self, name: str, type: type, constraints: list = []):
        """Constructor.
        
            name: Name of the parameter
            type: Expected type of the parameter
            constraints: Functions which a valid value for this parameter must satisfy
        """
        self.name = name
        self.expectedType = type
        self.constraints = constraints

    def parse(self, input: str):
        """Parse and validate an input string for this parameter."""
        try:
            parsedVal = ast.literal_eval(input)
        except (ValueError, SyntaxError):
            raise ValueError(f"Failed to parse input for {self.name}: {input}")
        return self.validate(parsedVal)

    def validate(self, value):
        """Determine if given value is valid for this parameter."""
        try:
            value = self.expectedType(value)
        except Exception:
            raise ValueError(f"{self.name} must be of type {self.expectedType.__name__}")
        
        for constraint in self.constraints:
            constraint(value)
        
        return value


class ProblemFactory:
    """Maps url slugs to the problem class."""
    _registry = {}

    @classmethod
    def register(cls, slug: str, problemCls):
        """Associate the given slug with the given problem class."""
        if slug in cls._registry:
            raise ValueError(f"Problem slug '{slug}' already registered.")
        cls._registry[slug] = problemCls
    
    @classmethod
    def create(cls, slug: str):
        """Create an instance of the problem class the slug is associated with."""
        if slug not in cls._registry:
            raise ValueError(f"Problem slug '{slug}' not found.")
        return cls._registry[slug]()
    
    def register_problem(slug):
        def decorator(cls):
            ProblemFactory.register(slug, cls)
            return cls
        return decorator


class Problem(ABC):
    """Base class for all problems."""
    
    def __init__(self, slug: str, parameters: list[Parameter]):
        """Constructor.
        
            slug: Url slug assigned to this problem by Leetcode
            parameters: Input parameters for this problem
        """
        self.slug = slug
        self.parameters = parameters

    @abstractmethod
    def buggy_solution(self, **parsedInputs):
        pass

    @abstractmethod
    def correct_solution(self, **parsedInputs):
        pass

    def parse_inputs(self, **kwargs):
        """Parse and validate user supplied input parameters for this problem.
        
        This function ignores any keyword arguments which aren't present
        in the problem's parameter list.
        """
        parsed = {}
        for param in self.parameters:
            if param.name not in kwargs:
                raise ValueError(f"Missing input: {param.name}")
            parsed[param.name] = param.parse(kwargs[param.name])
        return parsed
    
    def check_input(self, **parsedInputs):
        """Check if an input exposes a bug in the buggy solution.
        
        This function performs a value comparison between the results of
        the correct and buggy solution.
        """
        return self.correct_solution(**parsedInputs) != self.buggy_solution(**parsedInputs)


@ProblemFactory.register_problem("two-sum")
class TwoSum(Problem):
    """Class representing 1. TwoSum"""

    def __init__(self):
        super().__init__(
            "two_sum",
            [
                Parameter(
                    "nums", list[int],
                    [
                        lambda v : len(v) >= 2 and len(v) <= 10000
                    ]
                ),
                Parameter("target", int)
            ]
        )
    
    def buggy_solution(self, **parsedInputs):
        """Buggy solution for TwoSum uses the same element twice.

        Test Case:
            nums = [3, 4]
            target = [6]
        """
        nums = parsedInputs["nums"]
        target = parsedInputs["target"]
        for i in range(len(nums)):
            for j in range(len(nums)):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []
        
    def correct_solution(self, **parsedInputs):
        """Correct solution for TwoSum."""
        nums = parsedInputs["nums"]
        target = parsedInputs["target"]
        hashmap = {}
        for i in range(len(nums)):
            complement = target - nums[i]
            if complement in hashmap:
                return [i, hashmap[complement]]
            hashmap[nums[i]] = i
        return []

    def check_input(self, **parsedInputs):
        """Check if an input exposes the buggy TwoSum solution."""
        buggyRes = self.buggy_solution(**parsedInputs)
        correctRes = self.correct_solution(**parsedInputs)
        return buggyRes.sort() != correctRes.sort()
