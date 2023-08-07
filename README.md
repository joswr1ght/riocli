# riocli

Ranges.io CLI (`riocli`) automates cumbersome actions using the API.
Modeled after the AWS CLI utility, `riocli` allows Ranges.io authors to perform several actions that make it easier for the author to maintain and leverage the platform.

```
$ riocli -h
usage: riocli [-h] [-c CONFIG]
              {add-debrief-hints,delete-debriefs,add-package,list-packages,list-permissions,get-package,get-user-identity}
              ...

positional arguments:
  {add-debrief-hints,delete-debriefs,add-package,list-packages,list-permissions,get-package,get-user-identity}

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG

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

       usage: riocli.py [-h] [-c CONFIG]

OPTIONS
       -c|--config (string)

       Specify an Ranges.io credentials file with the API token. Defaults to
       ~/.rio/credentials.

AVAILABLE SERVICES

       o add-debrief-hints
       o delete-debriefs
       o get-package
       o add-package
       o get-user-identity
       o help
       o list-packages
       o list-permissions
```

