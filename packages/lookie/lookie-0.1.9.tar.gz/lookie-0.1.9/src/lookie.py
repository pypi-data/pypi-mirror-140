import argparse
from src.version import get_version
from src.checks import ping_test, string_check


def main():
    parser = argparse.ArgumentParser(description='`lookie` is the tool to help you monitor '
                                                 'different kind of resources.',
                                     epilog='Example: lookie --help',
                                     prog=f'lookie')
    parser.add_argument('--version', action='version', version=f'%(prog)s v{get_version()}',
                        help="Print the version of the tool.")

    subparsers = parser.add_subparsers(help='sub-command help')

    parser_ping = subparsers.add_parser('ping', help='ping check to host.')
    parser_ping.add_argument('--hostname', type=str, required=True, help='Hostname or IP to ping check.')
    parser_ping.add_argument('--surname', type=str, required=True, help='Surname of the host.')
    parser_ping.add_argument('--count', type=int, required=True, help='How many times to check?')
    parser_ping.add_argument('--interval', type=int, required=True,
                             help='Between the checks, what will be the interval?')
    parser_ping.set_defaults(func=ping_test)

    parser_string = subparsers.add_parser('string', help='Check string exists when accessing the endpoint.')
    parser_string.add_argument('--url', type=str, required=True, help='Which url to check for the string?')
    parser_string.add_argument('--string', type=str, required=True,
                               help='Which string to check in the page of that url?')
    parser_string.set_defaults(func=string_check)

    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help()
        parser.exit()


if __name__ == "__main__":
    main()
