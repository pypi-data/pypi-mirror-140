"""A Python CLI that does the necessary math to balance two investment funds with a new deposit."""

__author__ = 'Matt Youngberg'
__version__ = '1.0.0'
__all__ = ['CONTEXT', 'TWO_PLACES', 'StorePercentageAction',
           'StoreFundBalanceAction', 'main']

from argparse import Action, ArgumentParser, Namespace, OPTIONAL
from decimal import Context, Decimal, DivisionByZero, InvalidOperation, \
    Overflow, ROUND_HALF_EVEN, setcontext
from pathlib import Path
from sys import exit
from typing import NamedTuple

# Decimal configuration

CONTEXT = Context(
    prec=20,
    rounding=ROUND_HALF_EVEN,
    Emin=-999999,
    Emax=999999,
    capitals=1,
    clamp=0,
    flags=[],
    traps=[InvalidOperation, DivisionByZero, Overflow]
)

TWO_PLACES = Decimal('1.00')  # for using in the `Decimal.quantize()` methods

setcontext(CONTEXT)


class _TargetBalances(NamedTuple):
    fund_one: Decimal
    fund_two: Decimal


class _FundDifferences(NamedTuple):
    fund_one: Decimal
    fund_two: Decimal


class _OutputLines(NamedTuple):
    name: str
    action: str
    to_move: str
    current_balance: str
    target_balance: str


class StorePercentageAction(Action):
    def __init__(self, option_strings, dest, nargs=None, type=Decimal,
                 **kwargs):
        if nargs is not None and nargs is not OPTIONAL:
            raise ValueError(f'A {self.__class__.__name__} can only be used with nargs set to `None` or "?"')

        self.min = 0
        self.max = 1

        super(StorePercentageAction, self).__init__(option_strings, dest, nargs=nargs, type=type, **kwargs)

    def __call__(self, parser, namespace, values: Decimal, option_string=None):
        if (values > self.max) or (values < self.min):
            raise ValueError(f'Value `{values}` is not between {self.min} and {self.max}')
        setattr(namespace, self.dest, values)


class StoreFundBalanceAction(Action):
    def __init__(self, option_strings, dest, nargs=None, type=Decimal, **kwargs):

        if nargs is not None and nargs is not OPTIONAL:
            raise ValueError(f'A {self.__class__.__name__} can only be used with nargs set to `None` or "?"')

        if type is not Decimal:
            raise ValueError(f'A {self.__class__.__name__} requires a type `Decimal` to mimic a money-like value')

        self.min = Decimal(0)

        super(StoreFundBalanceAction, self).__init__(option_strings=option_strings, dest=dest, nargs=nargs, type=type,
                                                     **kwargs)

    def __call__(self, parser, namespace, values: Decimal, option_string=None):
        if values < self.min:
            raise ValueError(f'Value {values} is not equal or greater than {self.min}')
        value_rounded = values.quantize(TWO_PLACES)
        setattr(namespace, self.dest, value_rounded)  # Round to two places


def main() -> None:
    ns: Namespace = parse_args()
    if not percentages_sum_to_one(ns):
        print('Target percentages should sum to 1.00. Please adjust your percentages.')
        exit(1)
    target_amounts: _TargetBalances = calculate_targets(ns)
    diff_amounts: _FundDifferences = calculate_fund_differences(target_amounts, ns)

    lines1: _OutputLines = create_output_lines(ns.fundOneName, ns.fundOneCurrentBalance, target_amounts.fund_one,
                                               diff_amounts.fund_one)
    lines2: _OutputLines = create_output_lines(ns.fundTwoName, ns.fundTwoCurrentBalance, target_amounts.fund_two,
                                               diff_amounts.fund_two)

    width = get_box_width(lines1, lines2)
    print_fund_output(lines1, width)
    print()
    print_fund_output(lines2, width)


def parse_args() -> Namespace:
    parser = ArgumentParser(description=__doc__,
                            epilog='This program is maintained by Matt Youngberg. Feel free to email him at matt_youngberg@outlook.com.')
    parser.add_argument('-v', '--version', action='version', version=f'{Path(__file__).name} {__version__}')
    parser.add_argument('fundOneCurrentBalance', action=StoreFundBalanceAction,
                        help='The current value of the first fund to be rebalanced')
    parser.add_argument('fundOneTargetPercentage', action=StorePercentageAction,
                        help='The desired percentage of how much the first fund should contribute to the total balance between the two funds')
    parser.add_argument('fundTwoCurrentBalance', action=StoreFundBalanceAction,
                        help='The current value of the second fund to be rebalanced')
    parser.add_argument('fundTwoTargetPercentage', action=StorePercentageAction,
                        help='The desired percentage of how much the second fund should contribute to the total balance between the two funds')
    parser.add_argument('-d', '--deposit', action=StoreFundBalanceAction, default='0.00',
                        help='An amount deposited to be accounted for the in the rebalancing')
    parser.add_argument('-n1', '--fundOneName', default='Fund One',
                        help='A name for the first fund to be used in the program output')
    parser.add_argument('-n2', '--fundTwoName', default='Fund Two',
                        help='A name for the second fund to be used in the program output')
    return parser.parse_args()


def percentages_sum_to_one(ns: Namespace) -> bool:
    return ns.fundOneTargetPercentage + ns.fundTwoTargetPercentage == Decimal('1')


def calculate_targets(ns: Namespace) -> _TargetBalances:
    total_fund_amount: Decimal = ns.fundOneCurrentBalance + ns.fundTwoCurrentBalance + ns.deposit
    return _TargetBalances(
        (total_fund_amount * ns.fundOneTargetPercentage).quantize(TWO_PLACES),
        (total_fund_amount * ns.fundTwoTargetPercentage).quantize(TWO_PLACES)
    )


def calculate_fund_differences(target_balances: _TargetBalances, namespace: Namespace) -> _FundDifferences:
    return _FundDifferences(
        target_balances.fund_one - namespace.fundOneCurrentBalance,
        target_balances.fund_two - namespace.fundTwoCurrentBalance
    )


def create_output_lines(name: str, balance: Decimal, target: Decimal, difference: Decimal) -> _OutputLines:
    if difference < 0:
        action = 'SELL'
    elif difference == 0:
        action = 'HOLD'
    else:
        action = 'BUY'

    return _OutputLines(
        name=name.upper(),
        action=f'ACTION: {action}',
        to_move=f'MOVE: {difference}',
        current_balance=f'Current: {balance}',
        target_balance=f'Target: {target}'
    )


def get_box_width(lines1: _OutputLines, lines2: _OutputLines) -> int:
    max1 = max(map(len, lines1))
    max2 = max(map(len, lines2))
    return max(max1, max2)


def print_fund_output(output_lines: _OutputLines, width: int) -> None:
    width = width + 2
    print('\u2552' + ('\u2550' * width) + '\u2555')
    space, end_space = get_spacers(width, output_lines.name)
    print('\u2502' + space + output_lines.name + space + end_space + '\u2502')
    print('\u255E' + ('\u2550' * width) + '\u2561')
    space, end_space = get_spacers(width, output_lines.action)
    print('\u2502' + space + output_lines.action + space + end_space + '\u2502')
    space, end_space = get_spacers(width, output_lines.to_move)
    print('\u2502' + space + output_lines.to_move + space + end_space + '\u2502')
    print('\u251C' + ('\u2500' * width) + '\u2524')
    space, end_space = get_spacers(width, output_lines.current_balance)
    print('\u2502' + space + output_lines.current_balance + space + end_space + '\u2502')
    space, end_space = get_spacers(width, output_lines.target_balance)
    print('\u2502' + space + output_lines.target_balance + space + end_space + '\u2502')
    print('\u2514' + ('\u2500' * width) + '\u2518')


def get_spacers(width: int, string: str):
    if len(string) > width:
        raise ValueError('Cannot call `get_spacers` with a string longer than the given width')
    space = (width - len(string)) // 2
    spaced = ' ' * space
    end_space = '' if space * 2 + len(string) == width else ' '
    return spaced, end_space


if __name__ == '__main__':
    main()
