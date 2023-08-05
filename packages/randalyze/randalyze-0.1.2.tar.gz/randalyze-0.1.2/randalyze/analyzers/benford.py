import sys
from math import log10
from typing import Sequence, Dict


class BenfordAnalyzer:

    def __init__(self):
        self._first_digit_counts = list(0 for i in range(10))
        self._second_digit_counts = list(0 for i in range(10))

        self._expected_distribution = None

    @staticmethod
    def digit_probability(digit: int) -> float:
        if digit < 1 or digit > 9:
            raise ValueError('digit must be in the range [1..9]')

        return log10(1 + (1 / digit))

    @property
    def expected_distribution(self) -> Sequence[float]:
        if not self._expected_distribution:
            self._expected_distribution = [0.0] + [log10(1 + (1 / d)) for d in range(1, 10)]

        return self._expected_distribution

    def add_number(self, number: float) -> None:
        """
        Add a number to the analyzer.
        :param number:
        :return:
        """

        number_string = str(number).replace('0', '').replace('.', '')
        first_digit = int(number_string[0]) if number_string else None
        second_digit = int(number_string[1]) if number_string and len(number_string) > 1 else None

        if first_digit:
            self._first_digit_counts[first_digit] = self._first_digit_counts[first_digit] + 1

        if second_digit:
            self._second_digit_counts[second_digit] = self._second_digit_counts[second_digit] + 1

    def add_numbers(self, numbers: Sequence[float]) -> None:
        """
        Add a collection of numbers to the analyzer.
        :param numbers:
        :return:
        """
        if numbers:
            for number in numbers:
                self.add_number(number)

    @property
    def first_digit_counts(self) -> Sequence[int]:
        """
        The counts of each of the first digits from 0..9 for all of the numbers added to the analyzer.
        :return: A list of ten integers, representing the total counts of each first digit from 0.9
        respectively.
        """
        return [d for d in self._first_digit_counts]

    @property
    def first_digit_distribution(self) -> Sequence[float]:
        """
        The proportions of the total count of first digits for all of the numbers added to the analyzer.
        :return: A list of ten floating point numbers, representing the proportion of the total
        count represented by each digit.
        """
        total = sum(self._first_digit_counts)
        return [count / total if total else 1 for count in self._first_digit_counts]

    @property
    def second_digit_counts(self) -> Sequence[int]:
        return [d for d in self._second_digit_counts]

    def calculate_match(self) -> Dict:
        """
        Returns the expected, actual and difference percentage for each digit.

        :return:
        """
        total_numbers = sum(self.first_digit_counts)
        expected_counts = [c * total_numbers for c in self.expected_distribution]

        result = {}

        for digit in range(1, 10):
            result[digit] = {'expected': expected_counts[digit],
                             'actual': self._first_digit_counts[digit],
                             'difference': (1.0 * self._first_digit_counts[digit] - expected_counts[digit]) /
                                           expected_counts[digit]}

        return result

    def matches_distribution(self, tolerance_percent: float = 5.0) -> bool:
        """
        Returns true if the distribution matches Benford's law.
        :param tolerance_percent:
        :return:
        """

        match_details = self.calculate_match()

        matches = True

        for d in range(1, 10):
            if abs(match_details[d]['difference'] * 100.0) > tolerance_percent:
                return False

        return True

    def write_text_report(self, tolerance: float) -> None:
        """
        Writes a text summary report about the series to stdout.

        :return:
        """
        match_details = self.calculate_match()

        max_difference = 0.0

        sys.stdout.write('\n')
        sys.stdout.write('Benford Analysis Result\n')
        sys.stdout.write('First Digits Expected vs Actual:\n')

        for d in range(1, 10):
            if abs(match_details[d]["difference"] * 100.0) > max_difference:
                max_difference = abs(match_details[d]["difference"] * 100.0)

            sys.stdout.write(f'{d}  {match_details[d]["expected"]:>10.3f}  :  '
                             f'{match_details[d]["actual"]:>6}  ->  '
                             f'{(match_details[d]["difference"] * 100.0):>5.1f}%\n')

        sys.stdout.write('\n')
        sys.stdout.write(f'Maximum difference: {max_difference:.1f}%\n')
        sys.stdout.write(f'Benford (tolerance {tolerance}%)? {self.matches_distribution(tolerance)}\n')
        sys.stdout.write('\n')
        sys.stdout.flush()
