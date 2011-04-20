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
from ignition.common import check_command
from ignition import ProjectCreator

class DjangoCreator(ProjectCreator):
    '''
    Handles creating Django projects
    '''
    def __init__(self, project_name=None, root_dir=os.getcwd(), modules=[], **kwargs):
        ProjectCreator.__init__(self, project_name, root_dir, modules, **kwargs)
        self.log = logging.getLogger('DjangoCreator')
        # add Django
        django_found = False
        for m in self._modules:
            if m.find('django') > -1:
                django_found = True
        if not django_found:
            self._modules.append('django')

    def create_project(self):
        '''
        Creates a base Django project
        '''
        if os.path.exists(self._py):
            django_dir = os.path.join(self._django_dir, self._project_name)
            if os.path.exists(django_dir):
                if self._force:
                    logging.warn('Removing existing django project')
                    shutil.rmtree(django_dir)
                else:
                    logging.warn('Found existing django project; not creating (use --force to overwrite)')
                    return
            logging.info('Creating Django project')
            p = subprocess.Popen('cd {0} ; {1} startproject {2} > /dev/null'.format(self._django_dir, self._ve_dir + os.sep + self._project_name + \
            os.sep + 'bin' + os.sep + 'django-admin.py', self._project_name), \
            shell=True)
            os.waitpid(p.pid, 0)
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
        scr += '--chdir {0} '.format(os.path.join(self._django_dir, self._project_name))
        scr += '--pp {0} '.format(os.path.join(self._django_dir))
        # app settings
        scr += '--env DJANGO_SETTINGS_MODULE=settings -w \
\"django.core.handlers.wsgi:WSGIHandler()\" '
        # uwsgi settings
        scr += '--pidfile {0}/{1}_uwsgi.pid -d {2}/{1}_uwsgi.log '\
            .format(self._var_dir, self._project_name, self._log_dir)
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

