#!/usr/bin/env python
import os
import tempfile
import shutil
import unittest
import commands
from ignition import ProjectCreator
from ignition import common
from ignition.django import DjangoCreator
from random import Random
import string

class ProjectCreatorTestCase(unittest.TestCase):
    def setUp(self):
        self.root_dir = tempfile.mkdtemp()
        self.project_name = 'testproject'
        self.modules = []
        self.prj = ProjectCreator(root_dir=self.root_dir, project_name=self.project_name, modules=self.modules)

    def tearDown(self):
        if os.path.exists(self.root_dir):
            shutil.rmtree(self.root_dir)
    
    def testCheckDirectories(self):
        self.prj.check_directories()
        self.assertTrue(os.path.exists(self.prj._ve_dir))

    def testCreateVirtualenv(self):
        self.prj.create_virtualenv()
        self.assertTrue(os.path.exists(os.path.join(self.prj._ve_dir, self.project_name)))
        py = self.prj._ve_dir + os.sep + self.project_name + os.sep + \
        'bin' + os.sep + 'python'
        # run a simple import check to make sure we have working 
        # python environment
        self.assertEqual(commands.getoutput('{0} -c \'import {1}\''.format(py, 'os')), '')

    def testCreateNginxConfig(self):
        self.prj.create_nginx_config()
        nginx_conf = os.path.join(self.prj._conf_dir, '{0}_nginx.conf'.format(self.prj._project_name))
        self.assertTrue(os.path.exists(nginx_conf))
        f = open(nginx_conf, 'r')
        cfg = f.read()
        f.close()
        # search config for project_name -- not the best validation, but some
        self.assertTrue(cfg.find(self.prj._project_name) > -1)
        # search for 'http' section (standalone hosting
        self.assertTrue(cfg.find('http {') > -1)
        os.remove(nginx_conf)
        # create project with shared hosting
        self.prj = ProjectCreator(root_dir=self.root_dir, project_name=self.project_name, modules=self.modules, shared_hosting=True)
        self.prj.create_nginx_config()
        nginx_conf = os.path.join(self.prj._conf_dir, '{0}_nginx.conf'.format(self.prj._project_name))
        self.assertTrue(os.path.exists(nginx_conf))
        f = open(nginx_conf, 'r')
        cfg = f.read()
        f.close()
        # search config for project_name -- not the best validation, but some
        self.assertTrue(cfg.find(self.prj._project_name) > -1)
        # search for 'http' section (standalone hosting
        self.assertTrue(cfg.find('http {') == -1)

    def testAddStaticNginxDir(self):
        self.prj.create_nginx_config()
        nginx_config = self.prj.get_nginx_config()
        self.assertIsNotNone(nginx_config)
        # generate a random static dir to add to config
        vdir = ''.join(Random().sample(string.letters, 5))
        common.add_static_dir(root_dir=self.prj.get_root_dir(), project_name=self.prj.get_project_name(),\
            static_dir_path='/tmp', alias=vdir)
        nginx_config = self.prj.get_nginx_config()
        self.assertTrue(nginx_config.find(vdir) > -1)
        

    def testCreateManageScripts(self):
        self.prj.create_manage_scripts()
        self.assertTrue(os.path.exists('{0}_start.sh'.format(os.path.join(self.prj._script_dir, self.prj._project_name))))
        self.assertTrue(os.path.exists('{0}_stop.sh'.format(os.path.join(self.prj._script_dir, self.prj._project_name))))

class DjangoCreatorTestCase(unittest.TestCase):
    def setUp(self):
        self.root_dir = tempfile.mkdtemp()
        self.project_name = 'testproject'
        self.modules = []
        self.prj = DjangoCreator(root_dir=self.root_dir, project_name=self.project_name, modules=self.modules)

    def tearDown(self):
        if os.path.exists(self.root_dir):
            shutil.rmtree(self.root_dir)
    
    def testCreateProject(self):
        self.prj.create_virtualenv()
        self.assertTrue(os.path.exists(os.path.join(self.prj._django_dir)))
        self.prj.create_project()
        self.assertTrue(os.path.exists(os.path.join(self.prj._django_dir, \
        self.project_name) + os.sep + 'manage.py'))

if __name__=='__main__':
    unittest.main()
