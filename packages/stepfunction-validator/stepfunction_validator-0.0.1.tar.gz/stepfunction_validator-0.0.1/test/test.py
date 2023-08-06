import unittest

import jsonschema
import yaml

from stepfunction_validator.stepfunction_validator import load_json_schema, load_yaml, validate_stepfunction


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.json_schema = load_json_schema("../stepfunction_validator/stepfunctions_schema.json")

    def test_ValidStepFunction(self):
        invalid = load_yaml("test_scenarios/step_function_invalid.yml")
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            result = validate_stepfunction(invalid, self.json_schema)
            self.assertEqual(result, True)

    def test_InvalidStepFunction(self):
        invalid = load_yaml("test_scenarios/step_function_invalid.yml")
        with self.assertRaises(jsonschema.exceptions.ValidationError):
            result = validate_stepfunction(invalid, self.json_schema)

    def test_SyntaxErrorStepFunction(self):
        with self.assertRaises(yaml.parser.ParserError):
            invalid = load_yaml("test_scenarios/step_function_syntax.yml")
