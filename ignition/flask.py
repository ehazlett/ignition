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

import os
import logging
import subprocess
import commands
import shutil
from ignition.common import check_command
from ignition import ProjectCreator

class FlaskCreator(ProjectCreator):
    def __init__(self, project_name=None, root_dir=os.getcwd(), modules=[], **kwargs):
        """
        Handles creating Flask projects

        :keyword project_name: Name of project to create or edit
        :keyword root_dir: Base directory where projects are stored
        :keyword modules: List of Python modules to install into virtualenv (uses PIP)

        """
        ProjectCreator.__init__(self, project_name, root_dir, modules, **kwargs)
        self.log = logging.getLogger('FlaskCreator')
        # add Flask
        flask_found = False
        for m in self._modules:
            if m.find('flask') > -1:
                flask_found = True
        if not flask_found:
            self._modules.append('flask')

    def create_project(self):
        """
        Creates a base Flask project

        """
        if os.path.exists(self._py):
            prj_dir = os.path.join(self._app_dir, self._project_name)
            if os.path.exists(prj_dir):
                if self._force:
                    logging.warn('Removing existing project')
                    shutil.rmtree(prj_dir)
                else:
                    logging.warn('Found existing project; not creating (use --force to overwrite)')
                    return
            logging.info('Creating project')
            os.makedirs(prj_dir)
            # create the flask project stub
            app = """#!/usr/bin/env python\n"""\
            """from flask import Flask\n"""\
            """app = Flask(__name__)\n\n"""\
            """@app.route(\"/\")\n"""\
            """def hello():\n"""\
            """    return \"Hello from Flask...\"\n\n"""\
            """if __name__==\"__main__\":\n"""\
            """    app.run()\n\n"""
            with open(os.path.join(prj_dir, 'app.py'), 'w') as f:
                f.write(app)
        else:
            logging.error('Unable to find Python interpreter in virtualenv')
            return
    
    def create_uwsgi_script(self):
        scr = 'uwsgi '
        # set user
        if self._user:
            scr += '--uid {0} '.format(self._user)
        # set VE dir
        scr += '-H {0} '.format(self._ve_dir + os.sep + \
            self._project_name)
        # set process limit
        scr += '-p 1 '
        # set socket
        scr += '-s {0}.sock '.format(os.path.join(self._var_dir, self._project_name))
        # chdir for app
        scr += '--chdir {0} '.format(os.path.join(self._app_dir, self._project_name))
        scr += '--pp {0} '.format(os.path.join(self._app_dir))
        # app settings
        scr += '-w app:app '
        # uwsgi settings
        scr += '--pidfile {0}/{1}_uwsgi.pid -d {2}/{1}_uwsgi.log '.format(\
            self._var_dir, self._project_name, self._log_dir)
        # misc
        scr += '--no-orphans --vacuum -M --chmod-socket 664 \
--harakiri 300 --max-requests 5000 --limit-as 160 \
--post-buffering 16777216 '
        # write config
        uwsgi_file = os.path.join(self._conf_dir, '{0}.uwsgi'.format(self._project_name))
        f = open(uwsgi_file, 'w')
        f.write(scr)
        f.close()
        # make executable
        os.chmod(uwsgi_file, 0754)

