#!/usr/bin/env python

import os
import subprocess
import sys
import commands
from optparse import OptionParser
import logging
import unittest
import tempfile
import shutil
import ignition
from ignition.django import DjangoCreator
import ignition.common

PROJECT_TEMPLATES = [
    'django',
]

# logging vars
LOG_LEVEL=logging.DEBUG
LOG_FILE='ignition.log'
LOG_CONFIG=logging.basicConfig(level=logging.DEBUG, # always log debug to file
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d-%Y %H:%M:%S',
    filename=LOG_FILE,
    filemode='a')
                
logging.config=LOG_CONFIG
console = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s')
console.setFormatter(formatter)
console.setLevel(LOG_LEVEL)
logging.getLogger('').addHandler(console)

def main(opts=None):
    if not opts:
        logging.error('You must specify options to main')
    root_dir = opts.root_dir
    project_name = opts.project_name.strip().lower()
    modules = opts.modules
    user = opts.user
    port = opts.port
    force = opts.force
    # select template
    template = opts.template.lower()
    if template == 'django':
        prj = DjangoCreator(project_name=project_name, root_dir=root_dir,\
modules=modules, user=user, port=port, force=force, shared_hosting=opts.shared_hosting)
    else:
        logging.error('Unknown template')
        sys.exit(1)
    prj.create()
    logging.info('Project {0} created'.format(project_name))
    sys.exit(0)


if __name__ == '__main__':
    op = OptionParser()
    op.add_option('-d', '--root-directory', dest='root_dir', help='Root directory for projects')
    op.add_option('-n', '--name', dest='project_name', help='Name of project')
    op.add_option('-m', '--modules', dest='modules', help='Comma separated list of Virtualenv packages')
    op.add_option('-u', '--user', dest='user', help='User account to run Django application under')
    op.add_option('-p', '--port', dest='port', default=80, help='Port for webserver to listen on')
    op.add_option('--shared-hosting', dest='shared_hosting', action='store_true', default=False,\
        help='Create a shared hosted Nginx config (allow multiple apps on a single port)')
    op.add_option('-v', '--version', dest='show_version', action='store_true', default=False, help='Show version and exit')
    op.add_option('-t', '--template', dest='template', help='Project template (run --list-templates for available templates)')
    op.add_option('--list-templates', dest='list_templates', action='store_true', default=False, help='List available templates')
    op.add_option('--force', dest='force', action='store_true', default=False, help='Force creation (overwrites existing)')
    op.add_option('--add-static-dir', dest='add_static_dir', help='Add a static directory to nging config (format is '\
        '--add-static-dir <full_path_to_dir>:<alias> - i.e. --add-static-dir /srv/www/app/static:/static')

    opts, args = op.parse_args()

    # check for template list
    if opts.list_templates:
        templates = PROJECT_TEMPLATES
        print('Available templates:')
        print(''.join([' ' + x + '\n' for x in templates]))
        sys.exit(0)

    # show version
    if opts.show_version:
        print(':: Ignition :: version {0}'.format(ignition.__VERSION__))
        sys.exit(0)

    # check for add-static-dir
    if opts.add_static_dir:
        if not opts.root_dir or not opts.project_name:
            logging.error('You must specify a root directory and project name to add a static directory')
            sys.exit(1)
        static_dir, alias = opts.add_static_dir.split(':')
        ignition.common.add_static_dir(opts.root_dir, opts.project_name, static_dir, alias)
        sys.exit(0)

    # check for errors
    if not opts.root_dir or not opts.project_name or not opts.template:
        op.print_help()
        print('\n')
        logging.error('You must specify a root directory, project name, and template')
        sys.exit(1)
    print('\n:: Ignition ::\n')
    main(opts)

