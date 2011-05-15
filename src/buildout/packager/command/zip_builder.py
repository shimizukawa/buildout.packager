# -*- coding: utf-8 -*-
import os
import sys
from distutils import log
from utils import to_filename


def builder(name, installer_name, install_dir, src_dir, dist_dir,
           version='0.0.1', author_name=None, author_url=None,
           postfix_name=None, verbose=1):

    data_files = []
    for dirpath, dirnames, filenames in os.walk(src_dir):
        data_files.extend(os.path.join(dirpath, x) for x in filenames)

    zipfile_name = to_filename(installer_name, version, postfix_name)
    zipfile_name += '.zip'
    log.info("Creating zip file: %s", zipfile_name)

    raise NotImplementedError('zip_builder.builder')
