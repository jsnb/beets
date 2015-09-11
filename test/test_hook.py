# This file is part of beets.
# Copyright 2015, Thomas Scholtes.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)

import os.path
import tempfile

from test import _common
from test._common import unittest
from test.helper import TestHelper

from beets import config, logging
from beets import plugins


def get_temporary_path():
    temporary_directory = tempfile._get_default_tempdir()
    temporary_name = next(tempfile._get_candidate_names())

    return os.path.join(temporary_directory, temporary_name)


# TODO: Find a good way to test shell option
class HookTest(_common.TestCase, TestHelper):
    TEST_HOOK_COUNT = 5

    def setUp(self):
        self.setup_beets()  # Converter is threaded

    def tearDown(self):
        self.unload_plugins()
        self.teardown_beets()

    def _add_hook(self, event, command, substitute_event=None, shell=None,
                  substitute_args=None):

        hook = {
            'event': event,
            'command': command
        }

        if substitute_event is not None:
            hook['substitute_event'] = substitute_event

        if shell is not None:
            hook['shell'] = shell

        if substitute_args is not None:
            hook['substitute_args'] = substitute_args

        hooks = config['hook']['hooks'].get(list) if 'hook' in config else []
        hooks.append(hook)

        config['hook']['hooks'] = hooks

    def test_hook_no_arguments(self):
        temporary_paths = [
            get_temporary_path() for i in range(self.TEST_HOOK_COUNT)
        ]

        for index, path in enumerate(temporary_paths):
            self._add_hook('test_event_{0}'.format(index),
                           'echo > "{0}"'.format(path))

        self.load_plugins('hook')

        for index in range(len(temporary_paths)):
            plugins.send('test_event_{0}'.format(index))

        for path in temporary_paths:
            self.assertTrue(os.path.isfile(path))
            os.remove(path)

    def test_hook_event_substitution(self):

        temporary_directory = tempfile._get_default_tempdir()
        event_names = ['test_event_{0}'.format(i) for i in
                       range(self.TEST_HOOK_COUNT)]

        for event in event_names:
            self._add_hook(event,
                           'echo > "{0}"'.format(
                               os.path.join(temporary_directory, '%EVENT%')
                           ))

        self.load_plugins('hook')

        for event in event_names:
            plugins.send(event)

        for event in event_names:
            path = os.path.join(temporary_directory, event)

            self.assertTrue(os.path.isfile(path))
            os.remove(path)

    def test_hook_argument_substitution(self):
        temporary_paths = [
            get_temporary_path() for i in range(self.TEST_HOOK_COUNT)
        ]

        for index, path in enumerate(temporary_paths):
            self._add_hook('test_event_{0}'.format(index),
                           'echo > "%PATH%"'.format(path),
                           substitute_args = { 'path': '%PATH%' })

        self.load_plugins('hook')

        for index, path  in enumerate(temporary_paths):
            plugins.send('test_event_{0}'.format(index), path = path)

        for path in temporary_paths:
            self.assertTrue(os.path.isfile(path))
            os.remove(path)


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)

if __name__ == b'__main__':
    unittest.main(defaultTest='suite')
