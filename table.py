#!/usr/bin/python3
# pylint: disable=E1120
import io
import json
import math
import operator
import functools
import operator
from typing import Dict, List
import ast

import click

#: Demo data set 1
PERFORMANCE = (
    "Performance in requests per second",
    ["Computer", "LPOP", "SADD", "LPUSH", "GET", "SET"],
    {
        "A": [415742.52, 342444.95, 306472, 416612.54, 322154.33],
        "B": [1253954.38, 958227.51, 925685.69, 1202972.44, 884748.25],
        "C": [1365233.67, 1017367.58, 963456.75, 1159709.04, 916889.68],
        "D": [415742.52, 342494.98, 306477.42, 416612.54, 322154.54]
    },
    "HIB"
)

#: Demo data set 2
TIME = (
    "Time of excecution in seconds",
    ["Computer", "mafft", "mrbayes", "build-mplayer", "build-php",
        "compress-gzip", "dcraw", "encode-flac", "gnupg"],
    {
        "A": [18.95, 42.51, 163.14, 87.3, 22.06, 109.64, 13.86, 14.79],
        "B": [20.81, 49.69, 287.17, 461.28, 19.47, 92.81, 10.68, 28.27],
        "C": [15.2, 800.96, 3.89, 289.57, 16.69, 76.23, 9.34, 17.34],
        "D": [37.45, 50.81, 751.93, 757.42, 33.53, 100.75, 29.2, 15.32]
    },
    "LIB"
)


class BenchmarkTable:
    def __init__(self, demo: str, input_file: str, new: bool):
        if demo:
            if demo == "t":
                data_set = TIME
            elif demo == "p":
                data_set = PERFORMANCE
        elif input_file:
            extension = input_file.split('.')[-1].lower()
            if extension == "json":
                with open(input_file) as data:
                    data_set = tuple(json.load(data))
            elif extension == "py":
                with open(input_file) as data:
                    data_set = ast.literal_eval(data.read())
        elif new:
            data_set = BenchmarkTable.new_data_set(new)
        else:
            error("run with --help for more information.")

        BenchmarkTable.validate_data_set(data_set)
        self.title, self.headers, self.data, self.type = data_set

    def print_table(self, items: Dict[str, List[float]],
                    output: io.IOBase = None):
        """Prints the data set as a markdown table.

        Args:
            items: data set that should be converted to a markdown table.
        """
        # Set output
        writer = compose(output.write, lambda s: s + "\n") if output else print

        writer(f"| {str.join(' | ', self.headers)} |")
        writer(f"| {str.join(' | ', [':---:' for _ in self.headers])} |")
        for k, v in items.items():
            writer(f"| {k} {('| %.2f ' * len(v)) % tuple(v)} |")

    def compared_to(self, ref_machine: str) -> Dict[str, List[float]]:
        """Returns a normalized version of :data:`self.data` with respect to a
        given machine

        Args:
            ref_machine: the machine we use to normalize the :data:`self.data`

        Returns:
            A dictionary that maps computers to the list of their normalized
            results with respect to :paramref:`ref_machine`
        """
        result = {}
        for k, v in self.data.items():
            normalized = []
            if self.type == "LIB":
                for i, m in enumerate(v):
                    normalized.append(self.data[ref_machine][i] / m)
            elif self.type == "HIB":
                for i, m in enumerate(v):
                    normalized.append(m / self.data[ref_machine][i])
            else:
                print("ERROR: INVALID CONFIGURATION!")
                exit(1)
            result[k] = normalized
        return result

    def print_markdown(self, output: io.IOBase = None):
        """Prints markdown tables with that compare all the machines relative to each
        other."""
        # Set output
        writer = compose(output.write, lambda s: s + "\n") if output else print

        # Document title
        writer(f"# {self.title}")

        # Start by showing the data
        writer("\nWe have the following data:\n")
        self.print_table(self.data, output)

        # Now we print the normalized versions
        for ref_machine in self.data.keys():
            # Section header
            writer(f"\n## With computer {ref_machine} as reference\n")
            # Subtitle
            writer("The normalized data looks like this\n")

            # Print table
            compared_to_ref_machine = self.compared_to(ref_machine)
            self.print_table(compared_to_ref_machine, output)

            # Write conclusions and summary
            writer("\nIf we order their geometric means in increasing " +
                   "order, we have that:\n")

            # Sort results
            geo_means = {comp: geo_mean(normals) for comp, normals in
                         compared_to_ref_machine.items()}
            geo_means = sorted(geo_means.items(), key=operator.itemgetter(1))

            # Print results
            results = []
            for computer, mean in geo_means:
                if computer != ref_machine:
                    adj = "fast" if self.type == "LIB" else "powerful"
                    result = (
                        f"- Computer {computer} is {mean:.2f} times" +
                        f" as {adj} as computer {ref_machine}."
                    )
                    results.append(result)
            writer(str.join('\n', results))

    @staticmethod
    def new_data_set(title: str = None) -> tuple:
        """Creates a usable data set from user input
            title (str, optional): Defaults to None. The data set's
                                   description.

        Returns:
            A data set tuple (title, headers, data, data_type).
        """

        if not title:
            title = input("Provide a title for your data set: ")
        headers = ["Computer"]
        num_tests = int(input("How many tests did you run?: "))
        for i in range(num_tests):
            headers.append(input(f"Name of the test number {i + 1}: "))
        data = {}
        num_machines = int(
            input("How many computers did you run your tests on?: "))
        for i in range(num_machines):
            letter = chr(i + 65)
            data[letter] = [
                float(input(f"Machine {letter}'s result in test {test}: "))
                for test in headers[1:]]
        data_type = input("Is your data LIB or HIB?: ")
        return (title, headers, data, data_type)

    @staticmethod
    def validate_data_set(data_set):
        """Validates a given data set.

        Args:
            data: a data set of the form (title, headers, data, data_type).
        """
        _, headers, data, data_type = data_set
        first = list(data.keys())[0]
        if len(headers) - 1 != len(data[first]):
            error("Column headers and data set don't match")
        for v in data.values():
            if len(v) != len(data[first]):
                error("Rows don't have the same number of data points")
        if not data_type == "LIB" and not data_type == "HIB":
            error(f"Invalid data type {data_type}. Must be either LIB or HIB")


def compose(*functions):
    def compose2(f, g):
        return lambda x: f(g(x))
    return functools.reduce(compose2, functions, lambda x: x)


def error(message: str):
    print(message)
    exit(1)


def geo_mean(data: List[float]):
    """Gets the geometric mean of a list of floats.

    Args:
        data: the list of floats.
    """
    return math.pow(functools.reduce(operator.mul, data), 1/len(data))


def valid_file(ctx, param, value):
    """Callback function for the "--load" option.

    Args:
        ctx:   the application's context.
        param: "--load".
        value: the value assigned to this option.
    """
    if value is not None and not value.endswith((".py", ".json", ".JSON")):
        raise click.BadParameter('Should be a .py or .json file')
    return value


def valid_demo(ctx, param, value):
    """Callback function for the "--demo" option.

    Args:
        ctx:   the application's context.
        param: "--demo".
        value: the value assigned to this option.
    """
    if value is not None and value not in ["p", "t"]:
        raise click.BadParameter('Should be either "t" for the time demo,' +
                                 ' or "p" for the performance demo')
    return value


@click.command()
@click.option('--demo', default=None, callback=valid_demo,
              help='selects a demo accepts "p" or "t"')
@click.option('--load', default=None, callback=valid_file,
              help='loads the specified json or py file')
@click.option('--new', default=None,
              help='creates a new data set with the provided title')
@click.option('--output', default=None,
              help='saves output to the specified file')
def cli(demo: str, load: str, new: bool, output: str):
    """Click application

    Args:
        demo:   What the user passed with the --demo flag. Used for selecting
                a demo accepts "p" or "t".
        load:   What the user passed with the --load flag. Used to specify if
                a python or json file should be loaded.
        new:    What the user passed with the --new flag. Used to specify if
                the user wants to a new table, this parameter would then be
                this new data set's title.
        output: What the user passed with the --output flag. Used to specify
                if and to which file the output should be saved.
    """
    benchmark = BenchmarkTable(demo, load, new)
    if output:
        with open(output, 'w') as output_file:
            benchmark.print_markdown(output_file)
    else:
        benchmark.print_markdown()


if __name__ == '__main__':
    cli()
