#!/usr/bin/env python3

import sys
import json
import pathlib
import argparse
import requests
import re
# import textwrap
import pdb
import logging
import http.client


apiurl = 'https://ranges.io/api/v1'
apipackage = '/package'
credentialfiledefault = pathlib.Path.home() / '.rio' / 'credentials'
apiserver = 'https://ranges.io'


def _summarizechallenge(challenge):
    """
    Accept a challenge object and make opinionated summary decisions,
    returning a multi-line string.

    Parameters
    ----------
    challenge: str, required
        The challenge object from the package
    """
    # challengetitle = f'{group["name"]} - {challenge["longTitle"]}'
    # challengebriefing = f'{challenge["briefing"]}'

    challengeanswers = ''
    for answer in challenge['answer']['answers']:
        # Sometimes answer['value'] is an empty string
        if answer['correct'] and answer['value']:
            # Ranges.io doesn't store the flag in flag format;
            # reconstruct flag format for player
            if challenge['answer']['mode'] == 'Prefixed':
                challengeanswers += f"* {challenge['answer']['prefix']}{{{answer['value']}}}, "
            else:
                challengeanswers += f"* {answer['value']}, "
    challengeanswers = challengeanswers[:-2]

    challengehints = ''
    for hint in challenge['hints']['options']:
        challengehints += f"{hint['title']} -- {hint['content']}\n\n"
    challengehints = challengehints[:-1]

    if challengeanswers and challengehints:
        debrief = f"""
## Answer(s)

{challengeanswers}

## Hint(s)

{challengehints}
"""
    elif challengeanswers and not challengehints:
        debrief = f"""
## Answer(s)

{challengeanswers}
"""
    elif challengehints and not challengeanswers:
        # I don't think there will be a time when there are hints but no answer /shrug
        debrief = f"""
## Hint(s)

{challengehints}
"""
    else:
        # No answers and no hints
        debrief = ''

    # Remove Windows CRLF before returning
    return debrief.replace('\r\n', '\n')


def deletedebriefs(token: str, uuid: str) -> None:
    """Retrieve the Ranges.io package using token and uuid and modify the JSON
    to remove debrief fields.

    Return None

    Parameters
    ----------
    token: str, required
        The token for author package access.

    uuid: str, required
        The Ranges.io package ID
    """
    p = json.loads(getpackage(token, uuid))
    if p is None:
        sys.stderr.write('Invalid response retrieving specified package (network error?)\n')
        return None

    try:
        for error in p['errors']:
            if error['code'] == 'PKGNOTFOUND':
                sys.stderr.write(f'Package not found for specified package ID ({uuid}).\n')
            return None
    except KeyError:
        # No key `error` in package
        pass

    # We want to work with the actual package, not the server response data
    package = p['package']['export']
    for group in package['groups']:
        for challenge in group['challenges']:
            challenge['debriefs'] = []

    requests.put(f'{apiurl}{apipackage}/{uuid}',
                 headers={'Authorization': f'Bearer {token}'},
                 data=json.dumps(package))


def adddebriefhints(token: str, uuid: str) -> str:
    """Retrieve the Ranges.io package using token and uuid and modify the JSON
    to replace debrief field with question, answer, and hints.

    Return modified JSON

    Parameters
    ----------
    token: str, required
        The token for author package access.

    uuid: str, required
        The Ranges.io package ID
    """
    p = json.loads(getpackage(token, uuid))
    if p is None:
        sys.stderr.write('Invalid response retrieving specified package (network error?)\n')
        return None

    try:
        for error in p['errors']:
            if error['code'] == 'PKGNOTFOUND':
                sys.stderr.write(f'Package not found for specified package ID ({uuid}).\n')
            return None
    except KeyError:
        # No key `error` in package
        pass

    # We want to work with the actual package, not the server response data
    package = p['package']['export']
    for group in package['groups']:
        for challenge in group['challenges']:
            briefing = _summarizechallenge(challenge)

            # If the briefing includes at least an `Answer` string, then make it the debrief
            if ('Answer' in briefing):
                debrief = {'title': f'Debrief: {challenge["briefing"]}',
                           'activationMode': 'Any correct answer',
                           'content': briefing}
                challenge['debriefs'] = [debrief]

    # with open('out.json', 'w') as f:
    #     f.write(json.dumps(package, indent=1))

    response = requests.put(f'{apiurl}{apipackage}/{uuid}',
                            headers={'Authorization': f'Bearer {token}'},
                            data=json.dumps(package))

    return response.text


def getpackagelist(token: str) -> str:
    """Get the list of Ranges.io packages for the supplied token

    Request and return the JSON for the package list endpoint.

    Parameters
    ----------
    token: str, required
        The token for author package access.
    """

    response = requests.get(apiurl + apipackage,
                            headers={'Authorization': f'Bearer {token}'})
    return response.text


def getpermissions(token: str) -> list:
    """Get the Ranges.io permissions for the specified token.

    Return a list of the Ranges.io permissions for the specified token.

    Parameters
    ----------
    token: str, required
        The token for author package access.
    """

    packagedata = json.loads(getpackagelist(token))
    return packagedata['permissions']


def printpermissions(permissions: list) -> None:
    """Print the list of permissions returned by getpermissions()

    Use the list from getpermissionslist(), print the permissions one per line.

    Parameters
    ----------
    permissions: list, required
        The list of permissions as returned by getpermissions()
    """

    for permission in permissions:
        print(permission)


def getuser(token: str) -> list:
    """Get the Ranges.io user for the specified token.

    Return the user details associated with the specified token.

    Parameters
    ----------
    token: str, required
        The token for author package access.
    """

    packagedata = json.loads(getpackagelist(token))
    return packagedata['request']['requester']


def printuser(user: dict) -> None:
    """Print the user detailed returned by getuser()

    Use the dict from getuser(), print the user information details, one per line.

    Parameters
    ----------
    user: dict, required
        The dict of user details as returned by getuser()
    """

    print(f'Username:  {user["displayName"]}')
    print(f'Full name: {user["realName"]}')
    print(f'Email:     {user["email"]}')
    print(f'ID:        {user["id"]}')


def getpackage(token: str, uuid: str) -> str:
    """Get the specified Ranges.io package for the supplied package id and token

    Request and return the JSON for the Ranges.io package specified by the UUID
    (Ranges.io calls this the package ID).

    Parameters
    ----------
    token: str, required
        The token for author package access.

    uuid: str, required
        The Ranges.io package ID
    """

    response = requests.get(f'{apiurl}{apipackage}/{uuid}',
                            headers={'Authorization': f'Bearer {token}'})
    return response.text


def printpackage(package: str) -> None:
    """Print the packages returned by getpackage() as pretty JSON

    Use the response from getpackage() and print the JSON data.

    Parameters
    ----------
    packagee: str, required
        The JSON data from the /package/{UUID} API endpoint, retrieved by getpackage()
    """
    print(json.dumps(json.loads(package), indent=4))


def printpackagelist(response: str) -> None:
    """Print the list of packages returned by getpackagelist() as {UUID} -- Package Name

    Use the response JSON data from getpackagelist(), retrieve a list of package
    UUID values and package names. Display the package list using the format
    UUID -- Package Name.

    Parameters
    ----------
    response: str, required
        The JSON response from the /package API endpoint, retrieved by getpackagelist()
    """

    packagedata = json.loads(response)
    for package in packagedata['packages']:
        print(f'{package["id"]} -- {package["name"]}')


def readcredentials(credfile="") -> str:
    """ Get the token value from the specified credentials file

    Reads the token from the credentials file. Reads from ~/.rio/credentials
    unless otherwise specified.

    Parameters
    ----------
    credfile: str, optional
        The credentials file name; defaults to ~/.rio/credentials
    """

    if (credfile == ""):
        credfile = credentialfiledefault

    with open(credfile, 'r') as fp:
        return fp.readline().strip()


def _parser_help(parser):
    """ Display help information

    Return help information.

    Parameters
    ----------
    None
    """

    return f"""
NAME
       riocli

DESCRIPTION
       The Range.io Command Line Interface (riocli) is a tool to manage and
       manipulate your Ranges.io packages.

SYNOPSIS

       riocli [options] <command> [parameters]

       Use riocli <command> help for information on a  specific  command.  The
       synopsis for each command shows its parameters and their usage. Optional
       parameters are shown in square brackets.

USAGE

       {parser.format_usage()}

OPTIONS
       -c|--config (string)

       Specify an Ranges.io credentials file with the API token. Defaults to
       ~/.rio/credentials.

AVAILABLE SERVICES

       o add-debrief-hints
       o delete-debriefs
       o get-package
       o get-user-identity
       o help
       o list-packages
       o list-permissions
"""


def _parser_listpackages_help(parser):
    return f"""
DESCRIPTION

        list-packages will display a list of the packages available with the
        calling token including the ID and package name information.

USAGE

        {parser.format_usage()}

EXAMPLE

        riocli list-packages

"""


def _parser_getpackage_help(parser):
    return f"""
DESCRIPTION

        get-package will display the specified package contents. You must
        specify the ID value as a UUID.

        You can get a list of your packages using list-packages.

USAGE

        {parser.format_usage()}

EXAMPLE

        riocli get-package 9a511970-485d-471c-ab3f-b7214319a8b3

"""


def _parser_adddebriefhints_help(parser):
    return f"""
DESCRIPTION

        add-debrief-hints will add a debrief for successfully-answered
        questions. Existing debriefs are not modified (use delete-debriefs if
        you want to purge and create debrief hints as the only debrief for each
        question.

        By default, add-debrief-hints will display the debrief using the following format:

        Debrief: {{debrief-title}}

        ## Answer(s)

        {{answers}}

        ## Hints(s)

        Hint 1 -- {{hint1}}

        Hint 2 -- {{hint2}}

        ... repeated for all hints

USAGE

        {parser.format_usage()}

EXAMPLE

        riocli add-debrief-hints --packageid 9a511970-485d-471c-ab3f-b7214319a8b3

"""


def _parser_deletedebriefs_help(parser):
    return f"""
DESCRIPTION

        delete-debriefs will remove all debriefs from the specified package.

USAGE

        {parser.format_usage()}

EXAMPLE

        riocli delete-debriefs --packageid 9a511970-485d-471c-ab3f-b7214319a8b3

"""


def _parser_addpackage_help(parser):
    return """
    TODO
"""


def _parser_listpermissions_help(parser):
    return """
    TODO
"""


def _parser_getuseridentity_help(parser):
    return """
    TODO
"""


class RiocliParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f'ERROR: {message}')
        self.print_help()
        sys.exit(2)


def _parse_process():

    parser = RiocliParser(formatter_class=argparse.RawTextHelpFormatter)

    # These are core arguments to riocli
    parser.add_argument('-c', '--config', type=str)
    # TODO
    # parser.add_argument('-u','--endpoint-url', type=str, nargs='?', const=apiserver)
    # parser.add_argument('--debug', action='store_true')
    parser.set_defaults(config=credentialfiledefault)
    parser.epilog = _parser_help(parser)

    # Add the subparser for riocli commands
    subparser = parser.add_subparsers(dest='command')

    # add-debrief-hints
    parser_adddebriefhints = subparser.add_parser('add-debrief-hints',
                                                  formatter_class=argparse.RawTextHelpFormatter)
    parser_adddebriefhints.add_argument('-p', '--packageid', type=str, required=True)
    parser_adddebriefhints.epilog = _parser_adddebriefhints_help(parser_adddebriefhints)

    # delete-debriefs
    parser_deletedebriefs = subparser.add_parser('delete-debriefs',
                                                 formatter_class=argparse.RawTextHelpFormatter)
    parser_deletedebriefs.add_argument('-p', '--packageid', type=str, required=True)
    parser_deletedebriefs.epilog = _parser_deletedebriefs_help(parser_deletedebriefs)

    # add-package
    parser_addpackage = subparser.add_parser('add-package',
                                             formatter_class=argparse.RawTextHelpFormatter)
    parser_addpackage.add_argument('-f', '--packagefile', type=str, required=True)
    parser_addpackage.epilog = _parser_addpackage_help(parser_addpackage)

    # list-packages
    parser_listpackages = subparser.add_parser('list-packages',
                                               formatter_class=argparse.RawTextHelpFormatter)
    parser_listpackages.epilog = _parser_listpackages_help(parser_listpackages)

    # list-permissions
    parser_listpermissions = subparser.add_parser('list-permissions',
                                                  formatter_class=argparse.RawTextHelpFormatter)
    parser_listpermissions.epilog = _parser_listpermissions_help(parser_listpermissions)

    # get-package
    parser_getpackage = subparser.add_parser('get-package',
                                             formatter_class=argparse.RawTextHelpFormatter)
    parser_getpackage.add_argument('-p', '--packageid', type=str, required=True)
    parser_getpackage.epilog = _parser_getpackage_help(parser_getpackage)

    # get-user-identity
    parser_getuseridentity = subparser.add_parser('get-user-identity',
                                                  formatter_class=argparse.RawTextHelpFormatter)
    parser_getuseridentity.epilog = _parser_getuseridentity_help(parser_getuseridentity)

    # Override the default argparse behavior to show nothing when run without
    # arguments; instead, we show the default argparse `--help` output
    if (len(sys.argv) == 1):
        parser.print_usage()
        sys.exit(0)

    args = parser.parse_args()

    token = readcredentials()

    if args.command == 'add-debrief-hints':
        adddebriefhints(token, args.packageid)
    elif args.command == 'list-packages':
        printpackagelist(getpackagelist(token))
    elif args.command == 'list-permissions':
        printpermissions(getpermissions(token))
    elif args.command == 'get-user-identity':
        printuser(getuser(token))
    elif args.command == 'get-package':
        printpackage(getpackage(token, args.packageid))
    elif args.command == 'delete-debriefs':
        deletedebriefs(token, args.packageid)


if __name__ == '__main__':

    _parse_process()
