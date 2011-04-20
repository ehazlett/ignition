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

def check_command(command):
    cmd = commands.getoutput('which {0}'.format(command))
    if cmd == '':
        logging.error('{0} not found on path'.format(command))
        return False
    else:
        return True

