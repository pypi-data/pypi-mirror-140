import argparse
import json
import os.path
import sys
from enum import Enum
from typing import TextIO

from randalyze.analyzers import BenfordAnalyzer
from randalyze.generators import BenfordRandom


class OutputFormat(Enum):
    TEXT = 1
    JSON = 2


def check_percentage(value):
    percentage = float(value)

    if percentage < 0 or percentage > 100:
        raise argparse.ArgumentTypeError('%s in an invalid floating percentage value (0-100)' % percentage)

    return percentage


def parse_arguments():
    parser = argparse.ArgumentParser(description='Random number generator and analyzer.')

    subparsers = parser.add_subparsers(dest='command')

    generate_parser = subparsers.add_parser('generate',
                                            help='Generate a series of random numbers')

    generate_parser.add_argument('generator',
                                 choices=['benford'],
                                 default='benford',
                                 help='The type of generator to use')

    generate_parser.add_argument('-c', '--count',
                                 type=int,
                                 default=100,
                                 help='The number of values to generate')

    generate_parser.add_argument('-f', '--format',
                                 choices=['text', 'json'],
                                 default='text',
                                 help='The format of the output')

    analyze_parser = subparsers.add_parser('analyze',
                                           help='Analyze a series of random numbers')

    analyze_parser.add_argument('analyzer',
                                choices=['benford'],
                                default='benford',
                                help='The type of analyzer to use')

    analyze_parser.add_argument('-t', '--tolerance',
                                type=check_percentage,
                                default=5,
                                help='The pattern matching tolerance, in percent')

    analyze_parser.add_argument('-f', '--format',
                                choices=['text', 'json'],
                                default='text',
                                help='The format of the output')

    analyze_parser.add_argument('input_file',
                                metavar='FILE',
                                nargs='?',
                                default='-',
                                help='The file to use as a source of numbers for analysis, or - for stdin.')

    return parser.parse_args()


# Press Ctrl+F5 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def generator_function(generator, count: int):
    for _ in range(0, count):
        yield generator.random()


def generate_numbers(count: int, output_format: OutputFormat):
    generator = BenfordRandom()

    if output_format == OutputFormat.JSON:
        sys.stdout.write('[')
        format_string = '{},'
    else:
        format_string = '{}\n'

    for n in generator_function(generator, count):
        sys.stdout.write(format_string.format(generator.random()))

    if output_format == OutputFormat.JSON:
        sys.stdout.write(']')

    sys.stdout.flush()


def populate_analyzer(analyzer, source: TextIO):
    for line in source:
        try:
            value = float(line.strip())
            analyzer.add_number(value)
        except Exception as ex:
            print(f'Stuff: {ex}')


def main():
    arguments = parse_arguments()

    if arguments.command == 'generate':

        output_format = OutputFormat[arguments.format.upper()]
        generate_numbers(arguments.count, output_format)

    elif arguments.command == 'analyze':
        analyzer = BenfordAnalyzer()

        output_format = OutputFormat[arguments.format.upper()]

        if arguments.input_file and arguments.input_file != '-':
            # Check the specified file exists
            if not os.path.isfile(arguments.input_file):
                raise IOError(f'Input file does not exist at: {arguments.input_file}')

        if not arguments.input_file or arguments.input_file == '-':
            populate_analyzer(analyzer, sys.stdin)
        else:
            with open(arguments.input_file, mode='r') as source:
                populate_analyzer(analyzer, source)

        if output_format == OutputFormat.JSON:
            result = {'distributions': [{'name': 'benford',
                                         'matches': analyzer.matches_distribution(arguments.tolerance),
                                         'first_digit': {
                                             'distribution': {i: analyzer.first_digit_distribution[i] for i
                                                              in range(10)},
                                             'counts': {i: analyzer.first_digit_counts[i] for i in
                                                        range(10)}
                                         }}]}
            sys.stdout.write(json.dumps(result))
            sys.stdout.flush()
        else:
            analyzer.write_text_report(arguments.tolerance)


if __name__ == '__main__':
    main()
