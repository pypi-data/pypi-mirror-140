# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Poser Handler
"""

from __future__ import unicode_literals, absolute_import

import os
import sys
import subprocess

from rattail.app import GenericHandler


class PoserHandler(GenericHandler):
    """
    Base class and default implementation for Poser (custom code)
    handler.
    """

    def get_default_poser_dir(self):
        appdir = self.config.appdir(require=False)
        if not appdir:
            appdir = os.path.join(sys.prefix, 'app')
        return os.path.join(appdir, 'poser')

    def make_poser_dir(self, path=None, **kwargs):
        """
        Create the directory structure for Poser.
        """
        # assume default path if none specified
        if not path:
            path = self.get_default_poser_dir()

        # path must not yet exist
        path = os.path.abspath(path)
        if os.path.exists(path):
            raise RuntimeError("folder already exists: {}".format(path))

        # make top-level dir
        os.makedirs(path)

        # normal refresh takes care of most of it
        self.refresh_poser_dir(path)

        # make git repo
        subprocess.check_call(['git', 'init', path])
        subprocess.check_call([
            'bash', '-c',
            "cd {} && git add poser .gitignore".format(path),
        ])

        return path

    def refresh_poser_dir(self, path=None, **kwargs):
        """
        Refresh the basic structure for Poser.
        """
        # assume default path if none specified
        if not path:
            path = self.get_default_poser_dir()

        # path must already exist
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise RuntimeError("folder does not exist: {}".format(path))

        # make poser pkg dir
        poser = os.path.join(path, 'poser')
        if not os.path.exists(poser):
            os.makedirs(poser)

        # add `__init__` stub
        init = os.path.join(poser, '__init__.py')
        if not os.path.exists(init):
            with open(init, 'wt') as f:
                pass

        # make 'db' subpackage
        db = os.path.join(poser, 'db')
        if not os.path.exists(db):
            os.makedirs(db)

        # add `__init__` stub
        init = os.path.join(db, '__init__.py')
        if not os.path.exists(init):
            with open(init, 'wt') as f:
                pass

        # make 'db.model' subpackage
        model = os.path.join(db, 'model')
        if not os.path.exists(model):
            os.makedirs(model)

        # add `__init__` stub
        init = os.path.join(model, '__init__.py')
        if not os.path.exists(init):
            with open(init, 'wt') as f:
                pass

        # make 'db:alembic' folder
        alembic = os.path.join(db, 'alembic')
        if not os.path.exists(alembic):
            os.makedirs(alembic)

        # make .gitignore
        gitignore = os.path.join(path, '.gitignore')
        # TODO: this should always overwrite a "managed" section of the file
        if not os.path.exists(gitignore):
            with open(gitignore, 'wt') as f:
                f.write('**/__pycache__/\n')
