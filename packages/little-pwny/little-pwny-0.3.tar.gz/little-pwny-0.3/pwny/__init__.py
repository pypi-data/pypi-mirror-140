import hashlib
import sys
import urllib.request
import pkg_resources
from argparse import ArgumentParser


__version__ = pkg_resources.get_distribution("little-pwny").version


GPL_TEXT = """
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    """


def print_version():
    """Output current version and other infos."""
    print("little-pwny %s" % __version__)
    print("Copyright (C) 2019 ulif")
    print("little-pwny relies on data from haveibeenpwned.com.")
    print("See https://haveibeenpwned.com/Passwords for details.")
    print(GPL_TEXT)


def handle_options(args):
    """Handle commandline arguments."""
    parser = ArgumentParser(
        description=(
            "Check, how often a passphrase appears on haveibeenpwned.com"
        )
    )
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--version",
        action="store_true",
        help="output version information and exit.",
    )
    g.add_argument("passphrase", metavar="PASSPHRASE", nargs="?")
    args = parser.parse_args(args)
    return args


def mkhash(password):
    """Create SHA1 hash from `password`.

    HIBP API requests SHA1 hashed password.
    """
    return hashlib.sha1(password.encode("utf-8")).hexdigest().upper()


def num_pwned(hash_val):
    """Lookup haveibeenpwned.com for `hash_val`.

    Returns the number of entries found starting with the first 5 chars of
    `hash_val`.
    """
    resp = urllib.request.urlopen(
        "https://api.pwnedpasswords.com/range/%s" % hash_val[:5]
    )
    entries = resp.read().decode("utf-8").split("\r\n")
    result = dict([x.split(":") for x in entries]).get(hash_val[5:], 0)
    return resp.status, int(result)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = handle_options(argv)
    if args.version:
        print_version()
        sys.exit(0)
    print(num_pwned(mkhash(args.passphrase))[1])
