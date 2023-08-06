#!/usr/bin/env python

import pkg_resources  # part of setuptools
import json
import time
import sys
import os
import argparse

from terra_notebook_utils.drs import access
from terra_notebook_utils.cli import CLIConfig


def parse(input_string: str):
    """
    track type=bam db=hg38 name=exampleCRAM bigDataUrl=drs://dg.4503:dg.4503/17141a26-90e5-4160-9c20-89202b369431 bigDataIndex=drs://dg.4503:dg.4503/1447260e-654b-4f9a-9161-c511cbdd0f95

    :param input_string:
    :return:
    """
    workspace, google_billing_project = CLIConfig.resolve(None, None)
    args = input_string.split()
    new_args = []
    for arg in args:
        if arg.lower().startswith('bigdataurl='):
            uri = arg[len('bigDataUrl='):]
            if uri.startswith('drs:'):
                new_args.append('bigDataUrl=' + access(uri, workspace_name=workspace, workspace_namespace=google_billing_project))
            else:
                new_args.append(arg)
        elif arg.lower().startswith('bigdataindex='):
            uri = arg[len('bigDataIndex='):]
            if uri.startswith('drs:'):
                new_args.append('bigDataIndex=' + access(uri, workspace_name=workspace, workspace_namespace=google_billing_project))
            else:
                new_args.append(arg)
        else:
            new_args.append(arg)
    return ' '.join(new_args)


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="A visceral exploration of utility functions.")
    parser.add_argument('--input', '-i', type=str)
    parser.add_argument('--version', '-v', action='store_true', default=False)
    args = parser.parse_args(argv)

    if args.version:
        pkg = pkg_resources.require('lon')
        print(f'{sys.argv[0]} {pkg[0].version}')
        exit(0)

    print(parse(args.input).strip())


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
