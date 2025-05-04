"""
problem.py
Representations of LeetCode problems
"""

import ast
from abc import ABC, abstractmethod
from typing import get_origin, get_args

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
        if not Parameter.validate_type(value, self.expectedType):
            raise ValueError(f"{self.name} must be of type {self.expectedType}")
        
        for constraint in self.constraints:
            if not constraint[1](value):
                raise ValueError(f"Constraint failed: {constraint[0]}")
        
        return value
    
    def validate_type(value, expectedType) -> bool:
        """Determine if value is an instance of the expected type.
        
            value: Instance to check
            expectedType: Type we expect value to be
        """
        origin = get_origin(expectedType)
        args = get_args(expectedType)

        if origin is None:
            return isinstance(value, expectedType)
        elif origin is list:
            return isinstance(value, list) and all(Parameter.validate_type(v, args[0]) for v in value)
        elif origin is tuple:
            return (
                isinstance(value, tuple)
                and len(args) == len(value)
                and all(Parameter.validate_type(v, t) for v, t in zip(value, args))
            )
        elif origin is dict:
            key_type, val_type = args
            return (
                isinstance(value, dict)
                and all(Parameter.validate_type(k, key_type) and Parameter.validate_type(v, val_type) for k, v in value.items())
            )
        else:
            return isinstance(value, origin)


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
                        (
                            "nums length must be between 2 and 10^4",
                            lambda v : len(v) >= 2 and len(v) <= 10000
                        )
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
