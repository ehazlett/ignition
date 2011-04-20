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
import shutil
import commands
from ignition.common import check_command

class ProjectCreator(object):
    '''
    Base creator for all projects
    '''
    def __init__(self, project_name=None, root_dir=os.getcwd(), modules=[], **kwargs):
        if not project_name:
            print_error('You must specify a project name')
            return
        self._project_name = project_name
        self._root_dir = root_dir
        self._ve_dir = os.path.join(self._root_dir, 've')
        self._django_dir = os.path.join(self._root_dir, 'django')
        self._nginx_dir = os.path.join(self._root_dir, 'nginx')
        self._conf_dir = os.path.join(self._root_dir, 'conf')
        self._var_dir = os.path.join(self._root_dir, 'var')
        self._log_dir = os.path.join(self._root_dir, 'log')
        self._script_dir = os.path.join(self._root_dir, 'scripts')
        self._modules = modules
        self._include_mimetypes = False
        if 'user' in kwargs:
            self._user = kwargs['user']
        else:
            self._user = None
        if 'port' in kwargs:
            self._port = kwargs['port']
        else: # default to port 80 if not specified
            self._port = 80
        if 'server_name' in kwargs:
            self._server_name = kwargs['server_name']
        else:
            self._server_name = None
        if 'force' in kwargs:
            self._force = kwargs['force']
        else:
            self._force = False
        # check for extra modules
        if self._modules == None:
            self._modules = []
        elif type(self._modules) == type(''):
            # parse list
            mod_list = self._modules
            self._modules = []
            [self._modules.append(x) for x in mod_list.split(',')]
        # shortcut to python executable in ve
        self._py = self._ve_dir + os.sep + self._project_name + os.sep + \
        'bin' + os.sep + 'python'
        self.log = logging.getLogger('ProjectCreator')
        # check directories
        self.check_directories()

    def check_directories(self):
        '''
        Creates base directories for Django, virtualenv, and nginx
        ''' 
        self.log.debug('Checking directories')
        if not os.path.exists(self._ve_dir):
            os.makedirs(self._ve_dir)
        if not os.path.exists(self._django_dir):
            os.makedirs(self._django_dir)
        if not os.path.exists(self._nginx_dir):
            os.makedirs(self._nginx_dir)
        if not os.path.exists(self._conf_dir):
            os.makedirs(self._conf_dir)
        if not os.path.exists(self._var_dir):
            os.makedirs(self._var_dir)
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir)
        if not os.path.exists(self._script_dir):
            os.makedirs(self._script_dir)

        # copy uswgi_params for nginx
        uwsgi_params = '/etc/nginx/uwsgi_params'
        if os.path.exists(uwsgi_params):
            shutil.copy(uwsgi_params, self._conf_dir)
        else:
            logging.error('Unable to find Nginx uwsgi_params ; you must manually copy this to {0}'.format(self._conf_dir))

        # copy mime.types for nginx
        mime_types = '/etc/nginx/mime.types'
        if os.path.exists(mime_types):
            shutil.copy(mime_types, self._conf_dir)
            self._include_mimetypes = True
        else:
            logging.warn('Unable to find mime.types for Nginx')

    def create_virtualenv(self):
        if check_command('virtualenv'):
            ve_dir = os.path.join(self._ve_dir, self._project_name)
            if os.path.exists(ve_dir):
                if self._force:
                    logging.warn('Removing existing virtualenv')
                    shutil.rmtree(ve_dir)
                else:
                    logging.warn('Found existing virtualenv; not creating (use --force to overwrite)')
                    return
            logging.info('Creating virtualenv')
            p = subprocess.Popen('virtualenv --no-site-packages {0} > /dev/null'.format(ve_dir), shell=True)
            os.waitpid(p.pid, 0)
            # install modules
            for m in self._modules:
                self.log.info('Installing module {0}'.format(m))
                p = subprocess.Popen('{0} install {1} > /dev/null'.format(os.path.join(self._ve_dir, \
                self._project_name) + os.sep + 'bin' + os.sep + 'pip', m), shell=True)
                os.waitpid(p.pid, 0)

    def create_project(self):
        logging.error('Not yet implemented')
    
    def create_uwsgi_script(self):
        logging.error('Not yet implemented')

    def create_nginx_config(self):
        cfg = '# nginx config for {0}\n'.format(self._project_name)
        # user
        if self._user:
            cfg += 'user {0};\n'.format(self._user)
        # misc nginx config
        cfg += 'worker_processes 1;\nerror_log {0}-errors.log;\n\
pid {1}_nginx.pid;\n\n'.format(os.path.join(self._log_dir, \
self._project_name), os.path.join(self._var_dir, self._project_name))
        cfg += 'events {\n\tworker_connections 32;\n}\n\n'
        # http section
        cfg += 'http {\n'
        if self._include_mimetypes:
            cfg += '\tinclude mime.types;\n'
        cfg += '\tdefault_type application/octet-stream;\n'
        cfg += '\tclient_max_body_size 1G;\n'
        cfg += '\tproxy_max_temp_file_size 0;\n'
        cfg += '\tproxy_buffering off;\n'
        cfg += '\taccess_log {0}-access.log;\n'.format(os.path.join \
(self._log_dir, self._project_name))
        cfg += '\tsendfile on;\n'
        cfg += '\tkeepalive_timeout 65;\n'
        # server section
        cfg += '\tserver {\n'
        cfg += '\t\tlisten 0.0.0.0:{0};\n'.format(self._port)
        if self._server_name:
            cfg += '\t\tserver_name {0};\n'.format(self._server_name)
        # location section
        cfg += '\t\tlocation / {\n'
        cfg += '\t\t\tuwsgi_pass unix:///{0}.sock;\n'.format(\
os.path.join(self._var_dir, self._project_name))
        cfg += '\t\t\tinclude uwsgi_params;\n'
        cfg += '\t\t}\n\n'
        # end location
        # error page templates
        cfg += '\t\terror_page 500 502 503 504 /50x.html;\n'
        cfg += '\t\tlocation = /50x.html {\n'
        cfg += '\t\t\troot html;\n'
        # end error page section
        cfg += '\t\t}\n'
        # end server section
        cfg += '\t}\n'
        # end http section
        cfg += '}\n'

        # create conf
        nginx_conf = '{0}_nginx.conf'.format(os.path.join(self._conf_dir, self._project_name))
        f = open(nginx_conf, 'w')
        f.write(cfg)
        f.close()

    def create_manage_scripts(self):
        # create start script
        start = '# start script for {0}\n\n'.format(self._project_name)
        # start uwsgi
        start += 'echo \'Starting uWSGI...\'\n'
        start += 'sh {0}.uwsgi\n'.format(os.path.join(self._conf_dir, self._project_name))
        start += 'sleep 1\n'
        # start nginx
        start += 'echo \'Starting Nginx...\'\n'
        start += 'nginx -c {0}_nginx.conf\n'.format(os.path.join(self._conf_dir, self._project_name))
        start += 'sleep 1\n'
        start += 'echo \'{0} started\'\n\n'.format(self._project_name)

        # stop script
        stop = '# stop script for {0}\n\n'.format(self._project_name)
        # stop nginx
        stop += 'if [ -e {0}_nginx.pid ]; then nginx -c {1}_nginx.conf -s stop ; fi\n'.format(os.path.join(self._var_dir, self._project_name), os.path.join(self._conf_dir, self._project_name))
        # stop uwsgi
        stop += 'if [ -e {0}_uwsgi.pid ]; then kill -HUP `cat {0}_uwsgi.pid` ; rm {0}_uwsgi.pid 2>&1 > /dev/null ; fi\n'.format(os.path.join(self._var_dir, self._project_name))
        stop += 'echo \'{0} stopped\'\n'.format(self._project_name)

        # write scripts
        start_file = '{0}_start.sh'.format(os.path.join(self._script_dir, self._project_name))
        stop_file = '{0}_stop.sh'.format(os.path.join(self._script_dir, self._project_name))
        f = open(start_file, 'w')
        f.write(start)
        f.close()
        f = open(stop_file, 'w')
        f.write(stop)
        f.close()
        # make executable
        os.chmod(start_file, 0754)
        os.chmod(stop_file, 0754)

    def create(self):
        '''
        Creates the full project
        '''
        # create virtualenv
        self.create_virtualenv()
        # create django project
        self.create_project()
        # generate uwsgi script
        self.create_uwsgi_script()
        # generate nginx config
        self.create_nginx_config()
        # generate management scripts
        self.create_manage_scripts()

        logging.info('** Make sure to set proper permissions for the webserver user account on the var and log directories in the project root')

