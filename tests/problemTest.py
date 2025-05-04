import unittest
from src.entities.problem import *

class TestProblemParameter(unittest.TestCase):
    """Test the ProblemParameter class."""
    
    def test_basic_validation(self):
        intParameter = Parameter("intParameter", int)
        boolParameter = Parameter("boolParameter", bool)
        listParameter = Parameter("listParameter", list)
        dictParameter = Parameter("dictParameter", dict)
        tupleParameter = Parameter("tupleParameter", tuple)

        # Validations that should work
        self.assertEqual(
            3,
            intParameter.validate(3)
        )
        self.assertEqual(
            True,
            boolParameter.validate(True)
        )
        self.assertEqual(
            [3, 4],
            listParameter.validate([3, 4])
        )
        self.assertEqual(
            {"hi": 3, "bye": 4},
            dictParameter.validate({"hi": 3, "bye": 4})
        )
        self.assertEqual(
            (3, 4),
            tupleParameter.validate((3, 4))
        )

        # Validations that should work because of implicit type conversion
        self.assertEqual(
            1,
            intParameter.validate(True)
        )

        # Validations that should raise an exception
        self.assertRaises(
            ValueError,
            listParameter.validate,
            True
        )
        self.assertRaises(
            ValueError,
            listParameter.validate,
            ()
        )
        self.assertRaises(
            ValueError,
            boolParameter.validate,
            0
        )
        self.assertRaises(
            ValueError,
            intParameter.validate,
            "4"
        )

    def test_validation_with_generics(self):
        listOfIntParameter = Parameter("listofIntParameter", list[int])
        listOfListOfIntParameter = Parameter("listOfListOfIntParameter", list[list[int]])
        complexDictParameter = Parameter("complexDictParameter", dict[tuple[int, str, bool], dict[int, list[dict[tuple[int, str], bool]]]])

        # Validations that should work
        self.assertEqual(
            [1],
            listOfIntParameter.validate([1])
        )
        self.assertEqual(
            [[1, 2]],
            listOfListOfIntParameter.validate([[1, 2]])
        )
        self.assertEqual(
            [],
            listOfListOfIntParameter.validate([])
        )
        goodDict = {
            (1, "", True) : {
                1 : [
                    {
                        (1, "hi") :
                        True
                    }
                ]
            }
        }
        self.assertEqual(
            goodDict,
            complexDictParameter.validate(goodDict)
        )
        
        # Validations that should raise an exception
        self.assertRaises(
            ValueError,
            listOfIntParameter.validate,
            ["42", "32"]
        )
        self.assertRaises(
            ValueError,
            listOfIntParameter.validate,
            [43, "42"]
        )
        self.assertRaises(
            ValueError,
            listOfListOfIntParameter.validate,
            [[""]]
        )
        self.assertRaises(
            ValueError,
            listOfListOfIntParameter.validate,
            [1]
        )
        badDict = {
            (1, "", True) : {
                1 : [
                    {
                        ("", "hi") :
                        True
                    }
                ]
            }
        }
        self.assertRaises(
            ValueError,
            complexDictParameter.validate,
            badDict
        )
    
    def test_validation_with_constraints(self):
        listOfIntParameter = Parameter(
            "listOfIntParameter",
            list[int],
            [
                (
                    "Length of listOfIntParameter should be greater that 0",
                    lambda v: len(v) > 0
                )
            ]
        )

        self.assertEqual(
            [1],
            listOfIntParameter.validate([1])
        )
        self.assertRaises(
            ValueError,
            listOfIntParameter.validate,
            []
        )

    def test_basic_parsing(self):
        tupleParameter = Parameter("tupleParameter", tuple[int, bool, str])
        listOfIntParameter = Parameter("listOfIntParameter", list[int])
        
        # Parsing that should work
        self.assertEqual(
            [1],
            listOfIntParameter.parse("[1]")
        )
        self.assertEqual(
            (1, True, "hello"),
            tupleParameter.parse("(1, True, 'hello')")
        )

        # Parsing that should raise an error
        self.assertRaises(
            ValueError,
            tupleParameter.parse,
            "(1, 2"
        )
