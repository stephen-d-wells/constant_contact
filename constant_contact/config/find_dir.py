#!/usr/bin/env python

import os

class FindDir():
    _base_dir = os.path.dirname(os.path.realpath(__file__))
    conf_dir = ''
    log_dir  = ''
    report_dir = ''
    found_dir = '' # for special cases

    def __init__(self, dirname=None):
        #current_dir = os.path.join(self._base_dir, 'conf')
        if dirname is None: # maybe these should 'always' be the case
            self.conf_dir = self._find_dir('conf')
            self.log_dir = self._find_dir('log')
            self.report_dir = self._find_dir('reports')
        else:
            self.found_dir = self._find_dir(dirname)

    def _find_dir(self, dirname=None):
        if dirname is None:
            dirname = 'conf'

        current_dir = os.path.join(self._base_dir, dirname)
        while not os.path.isdir(current_dir):

            if os.path.dirname(current_dir) == '/': # end of the line
                return None

            current_dir = os.path.join(
                os.path.dirname(os.path.dirname(current_dir)), dirname)

        return current_dir + '/'


if __name__ == "__main__":
    cd = FindDir()
    print(cd.conf_dir)
    print(cd.log_dir)
    print(cd.report_dir)
