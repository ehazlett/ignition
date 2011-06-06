#!/usr/bin/env python
#   Copyright 2011 Evan Hazlett <ejhazlett@gmail.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
import commands
import os

def check_command(command):
    cmd = commands.getoutput('which {0}'.format(command))
    if cmd == '':
        logging.error('{0} not found on path'.format(command))
        return False
    else:
        return True

def add_static_dir(root_dir=None, project_name=None, static_dir_path=None, alias=None):
    log = logging.getLogger('common')
    conf_file = os.path.join(root_dir, 'conf' + os.sep + '{0}_nginx.conf'.format(project_name))
    if not os.path.exists(conf_file):
        log.error('Unable to find config file: {0}.  Please check root directory and project name'.format(conf_file))
        return
    log.info('Creating static directory alias')
    f = open(conf_file, 'r')
    cfg = f.readlines()
    f.close()
    new_cfg = ''
    location_found = False
    alias_added = False
    for l in cfg:
        if l.find('location') > -1:
            location_found = True
            new_cfg += l
        elif location_found and l.find('}') > -1 and not alias_added:
            # end of location found ; add alias
            new_cfg += l
            alias = '\t\tlocation {0} {{\n'.format(alias)
            alias += '\t\t\talias {0};\n'.format(static_dir_path)
            alias += '\t\t}\n'
            new_cfg += alias
            location_found = False
            alias_added = True
        else:
            new_cfg += l
    f = open(conf_file, 'w')
    f.write(new_cfg)
    f.close()

