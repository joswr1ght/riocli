#!/usr/bin/env python3

import sys
import json
import pathlib
import pdb

import requests


apiurl = 'https://ranges.io/api/v1'
apipackage = '/package'


def getpackagelist(token:str) -> str:
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


def getpermissions(token:str) -> list:
    """Get the Ranges.io permissions for the specified token.

    Return a list of the Ranges.io permissions for the specified token.

    Parameters
    ----------
    token: str, required
        The token for author package access.
    """

    packagedata = json.loads(getpackagelist(token))
    return packagedata['permissions']


def printpermissions(permissions:list) -> None:
    """Print the list of permissions returned by getpermissions()

    Use the list from getpermissionslist(), print the permissions one per line.

    Parameters
    ----------
    permissions: list, required
        The list of permissions as returned by getpermissions()
    """

    for permission in permissions:
        print(permission)


def getuser(token:str) -> list:
    """Get the Ranges.io user for the specified token.

    Return the user details associated with the specified token.

    Parameters
    ----------
    token: str, required
        The token for author package access.
    """

    packagedata = json.loads(getpackagelist(token))
    return packagedata['request']['requester']


def printuser(user:dict) -> None:
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


def getpackage(token:str, uuid:str) -> str:
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


def printpackage(package:str) -> None:
    """Print the packages returned by getpackage() as pretty JSON

    Use the response from getpackage() and print the JSON data.

    Parameters
    ----------
    packagee: str, required
        The JSON data from the /package/{UUID} API endpoint, retrieved by getpackage()
    """
    print(json.dumps(json.loads(package), indent=4))


def printpackagelist(response:str) -> None:
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
        credfile = pathlib.Path.home() / '.rio' / 'credentials'

    with open(credfile, 'r') as fp:
        return fp.readline().strip()


def usage():
    """ Display usage information

    Display usage information.

    Parameters
    ----------
    None
    """

    print ("""
usage: riocli [options] <command> [parameters]
To see help text, you can run:

  riocli help
  riocli <command> help

""")


def showhelp():
    """ Display help information

    Display help information.

    Parameters
    ----------
    None
    """

    print("""
NAME
       riocli

DESCRIPTION
       The  Range.io Command Line Interface is a tool to manage your Ranges.io
       packages.

SYNOPSIS
          riocli [options] <command> [parameters]

       Use riocli <command> help for information on a  specific  command.  The
       synopsis for each command shows its parameters and their usage. Optional
       parameters are shown in square brackets.

OPTIONS
       --config (string)

       Specify an Ranges.io credentials file with the API token. Defaults to
       ~/.rio/credentials.

       --debug (boolean)

       Turn on debug logging.

       --endpoint-url (string)

       Override the command's default URL with the given URL.

AVAILABLE SERVICES

       o add-debrief-hints
       o delete-debrief
       o delete-debriefs
       o get-package
       o get-user-identity
       o help
       o list-packages
       o list-permissions
""")


def showhelplistpackages():
    """ Display help information for list-packages connabd

    Display help information for the list-packages command.

    Parameters
    ----------
    None
    """

    print("""
DESCRIPTION

        list-packages will display a list of the packages available with the
        calling token including the ID and package name information.

EXAMPLE

        riocli list-packages

""")


def showhelpgetpackage():
    """ Display help information for get-package connabd

    Display help information for the get-package command.

    Parameters
    ----------
    None
    """

    print("""
DESCRIPTION

        get-package will display the specified package contents. You must
        specify the ID value as a UUID.

        You can get a list of your packages using list-packages.

EXAMPLE

        riocli get-package 9a511970-485d-471c-ab3f-b7214319a8b3

""")


if __name__ == '__main__':

    rioclicommands = [
            'add-package',
            'list-packages',
            'list-permissions',
            'get-user-identity',
            'get-package',
            'add-debrief-hints',
            'delete-debrief',
            'delete-debriefs',
            'delete-package'
            ]

    if (len(sys.argv) == 1):
        usage()
        print('riocli: error: the following arguments are required: <command>')
        sys.exit(-1)

    # TODO: Process -c argument for credentials
    token = readcredentials()

    # TODO: Figure out a way to test command line arguments and support help requests
    command = sys.argv[1]
    if (command == 'help'):
        showhelp()
    elif (command == 'list-packages'):
        printpackagelist(getpackagelist(token))
    elif (command == 'list-permissions'):
        printpermissions(getpermissions(token))
    elif (command == 'get-user-identity'):
        printuser(getuser(token))
    elif (command == 'get-package'):
        # TODO: This is a mess
        if (len(sys.argv) > 2 and sys.argv[2] == "help"):
            showhelpgetpackage()
        elif (len(sys.argv) < 3):
            showhelpgetpackage()
            print('riocli: error: the following arguments are required: <UUID>')
        else:
            printpackage(getpackage(token, sys.argv[2]))
    # TODO
    elif (command == 'add-debrief-hints'):
        print('Not yet implemented.')
    elif (command == 'delete-debrief'):
        print('Not yet implemented.')
    elif (command == 'delete-debriefs'):
        print('Not yet implemented.')
    elif (command == 'delete-package'):
        print('Not yet implemented.')
    elif (command == 'add-package'):
        print('Not yet implemented.')
    else:
        usage()
        print(f'riocli: invalid command "{command}", valid choices are:')
        for command in rioclicommands:
            print(f'    o {command}')
