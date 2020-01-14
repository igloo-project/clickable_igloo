"""Clickable igloo extensions
"""

__version__ = "0.1"

import logging
import os
import os.path
import subprocess

import click

import clickable.coloredlogs

import clickable_ansible

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


_PHASES = ['firewall', 'httpd', 'tomcat', 'filesystem', 'postgresql', 'glowroot', 'tomcat']
def _igloo_full_decorators():
    # function that handles listed options below
    def configure_extra_vars():
        def wrapper(*args, **kwargs):
            extra_vars = kwargs['extra_vars']
            if not extra_vars:
                extra_vars = []
            new_kwargs = dict(kwargs)

            deploy_war = False

            # deliver a war file
            if 'deliver' in new_kwargs:
                deliver = new_kwargs.pop('deliver')
                extra_vars.append('{}={}'.format('playbook_gitlab_cd_war_location', deliver))
                deploy_war = True

            # build and deliver application
            if new_kwargs.get('build_igloo', None):
                extra_vars.append('{}={}'.format('playbook_build_igloo', 'true'))
            if new_kwargs.get('build_project', None) or new_kwargs.get('build_igloo', None):
                extra_vars.append('{}={}'.format('playbook_build_project', 'true'))
                deploy_war = True
            new_kwargs.pop('build_project')
            new_kwargs.pop('build_igloo')

            # force rebuild
            if new_kwargs.pop('force_rebuild', None):
                extra_vars.append('{}={}'.format('playbook_rebuild_project', 'true'))
                extra_vars.append('{}={}'.format('playbook_rebuild_igloo', 'true'))
            
            phases = new_kwargs.pop('phases', None)
            if phases:
                for phase in phases:
                    extra_args.append('--tags={}'.format(phase))

            skip_handlers = new_kwargs.pop('skip_handlers', None)
            if skip_handlers:
                extra_vars.append('{}={}'.format('handlers_inhibited', 'true'))

            # playbook_deploy_war=true if war or built application must be delivered
            if deploy_war:
                extra_vars.append('{}={}'.format('playbook_deploy_war', 'true'))
            else:
                extra_vars.append('{}={}'.format('playbook_deploy_war', 'false'))
    return [
        click.option('--deliver', default=None, help='War to deliver. If none/empty, delivery is not performed.'),
        click.option('--build-project', default=False, is_flag=True, help='Build project and deliver war.'),
        click.option('--build-igloo', default=False, is_flag=True, help='Build igloo; implies build-project.'),
        click.option('--force-rebuild', default=False, is_flag=True, help='Rebuild already built items.'),
        click.option('--skip-handlers', default=False, is_flag=True, help='Skip handlers; display messages instead. YOU MUST ensure manually that needed restart are performed.'),
        click.option('--phases', default='', help='Choose phases to perform, separate with comma ",": ' + ', '.join(_PHASES))
    ]


def run_igloo_full_task(click_group, name, playbook, static_extra_vars=[],
        decorators=[], help=None, short_help=None,
        common_hosts=False):
    merged_decorators = []
    merged_decorators.extend(decorators)
    merged_decorators.extend(_igloo_full_decorators())
    return clickable_ansible.run_playbook_task(click_group, name, playbook,
            static_extra_vars=static_extra_vars, decorators=merged_decorators,
            help=help, short_help=short_help, common_hosts=common_hosts)
