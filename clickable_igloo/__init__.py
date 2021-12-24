"""Clickable igloo extensions
"""

__version__ = "1.1"

import logging
import os
import os.path
import subprocess

import clickable.coloredlogs

clickable.coloredlogs.bootstrap()
logger = logging.getLogger('stdout.clickable')

DEFAULT_FOLDERS = [
    "playbooks",
    "inventory"
]


def symlink_folder(from_folder, to_folder, dry_run=False):
    """Populate to_folder with symlinks to files of from_folder. Intermediate
folders are created (not symlinked).

TODO: full implementation of dry_run
    """
    if not os.path.exists(from_folder):
        logger.warn("{} skipped as it does not exist".format(from_folder))
        return
    if not os.path.exists(to_folder):
        logger.debug("{} created as it does not exists".format(to_folder))
        os.makedirs(to_folder)
    if os.path.exists(to_folder) and not os.path.isdir(to_folder):
        raise Exception("{} exists and is not a directory".format(to_folder))
    find_links_command = ["find", "-H", ".", "-type", "l"]
    find_files_command = ["find", "-H", ".", "-type", "f"]
    to_existing_links = subprocess.check_output(find_links_command, text=True, cwd=to_folder).splitlines()
    from_files = subprocess.check_output(find_files_command, text=True, cwd=from_folder).splitlines()
    deleted_links = []
    kept_links = []
    added_links = []
    for link in to_existing_links:
        link_abs = os.path.join(to_folder, link)
        if not os.path.exists(link_abs):
            deleted_links.append(link_abs)
        else:
            kept_links.append(link_abs)
    for from_file in from_files:
        from_file_abs = os.path.join(from_folder, from_file)
        target = os.path.join(to_folder, from_file)
        if not os.path.exists(target):
            added_links.append((from_file_abs, target))
        elif os.path.islink(target):
            assert(os.path.join(to_folder, from_file) in kept_links)
        else:
            raise Exception("{} exists and is not a link".format(target))
    for link in added_links:
        parent = os.path.dirname(link[1])
        if not os.path.exists(parent):
            logger.info("{} directory created".format(parent))
            os.makedirs(parent)
        if not dry_run:
            os.symlink(os.path.relpath(link[0], parent), link[1])
        else:
            logger.warn("{} > {} creation skipped (dry-run)".format(link[1], link[0]))
    for link in deleted_links:
        if os.path.islink(link):
            os.remove(link)
        else:
            logger.warn("{} orphan deletion skipped (dry-run)".format(link))


def symlink_folders(from_root, to_root, folders=DEFAULT_FOLDERS, dry_run=False):
    for folder in folders:
        symlink_folder(os.path.join(from_root, folder), os.path.join(to_root, folder), dry_run)
