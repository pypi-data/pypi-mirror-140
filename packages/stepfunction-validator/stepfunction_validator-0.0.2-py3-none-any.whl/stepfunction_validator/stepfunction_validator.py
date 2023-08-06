import json
import os

from jsonschema import validate
import yaml
import sys
import click
from yaml import FullLoader


def load_json_schema(json_schema_file):
    with open(json_schema_file) as f:
        json_schema = json.load(f)
    return json_schema


def load_yaml(yaml_file):
    with open(yaml_file, "r") as f:
        stepfunction_yaml = yaml.load(f, Loader=FullLoader)
    return stepfunction_yaml


def validate_stepfunction(yamldata, json_schema):
    validate(
        instance=yamldata, schema=json_schema
    )  # if 0 message is received in terminal then validation is successful performed
    return True


# c and s are the parameters for the command line arguments that are required
# click is a library to create this whole command line tool
@click.command()
@click.option("-c", default="File", help="Your YAML file/schema")
@click.option("-s", help="Your JSON file/schema")
def main(c, s):
    """
    YAML validator for the CLI

    Example: python app.py -c <test.yaml> [-s <stepfunctions_schema.json>]
    This will validate a YAML file against the schema you provided in CLI

    Created by Nilesh
    https://github.com/NileshDebix
    """

    # Load the step_function_yaml_file from the command line that was given as a argument
    step_function_yaml_file = sys.argv[2]
    if not step_function_yaml_file:
        print("error no json file")

    # Load the json_file from the command line that was given as a argument
    if len(sys.argv) > 3:
        json_file = sys.argv[4]
    else:
        schema_path = os.path.dirname(os.path.realpath(__file__))
        json_file = os.path.join(schema_path, "stepfunctions_schema.json")

    # Open the json schema and yaml file with a nested "with open"
    json_schema = load_json_schema(json_file)

    # load the file data into a variable
    stepfunction_data = load_yaml(step_function_yaml_file)

    # insert loaded variables into the validator, this line will validate the file
    validate_stepfunction(stepfunction_data, json_schema)


if __name__ == "__main__":
    main()
