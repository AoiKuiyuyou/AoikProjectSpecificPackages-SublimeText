# coding: utf-8
#
import codecs
import json
import os
import os.path
import sys
import traceback

from datetime import datetime

import sublime
import sublime_plugin

# If Sublime Text version is 2
if sublime.version().startswith('2'):
    #
    from shutil import copy2
    from shutil import copystat
# If Sublime Text version is higher than 2
else:
    #
    from distutils.dir_util import copy_tree as copy_tree_py3


#
_PACKAGE_NAME = 'AoikProjectSpecificPackages'


#
class AoikProjectSpecificPackagesEventListener(sublime_plugin.EventListener):
    """
    Project Settings (in ".sublime-project" JSON file's "settings" key):
    - project_specific_packages_directory: a path, either relative or absolute.
      Default is "sublime_packages". Files under this directory will be copied
      into Sublime Text's "Packages" directory.
    """

    def __init__(self):
        # Current project file path (i.e. ".sublime-project" file)
        self._proj_file_path = None

    def on_activated(self, view):
        """
        Called when a view gains input focus.
        """
        # Get view window
        window = view.window()

        # If window is unavailable
        if window is None:
            # Exit
            return

        # Get project file path (i.e. ".sublime-project" file)

        # If Sublime Text version is 2
        if sublime.version().startswith('2'):
            # Sublime Text 2 has no API "project_file_name".
            # Instead, check if any view in the active group is a project file
            # i.e. ending with ".sublime-project". Use the first one found.
            # So to make this plugin work in Sublime Text 2, users should keep
            # their project file open in a view and ensure it is the first one
            # to be found.

            # The project file path
            proj_file_path = None

            # Get the active view
            active_view = window.active_view()

            # If has an active view
            if active_view is not None:
                # Get the active group index
                active_group_index, _ = \
                    window.get_view_index(active_view)

                # Get all views in the active group
                view_s = window.views_in_group(active_group_index)

                # Start to find project file path
                for view in view_s:
                    # Get view file path
                    view_file_path = view.file_name()

                    # If the view file path ends with ".sublime-project"
                    if view_file_path \
                            and view_file_path.endswith('.sublime-project'):

                        # If the view file is a regular file
                        if os.path.isfile(view_file_path):

                            # Use it as project file path
                            proj_file_path = view_file_path

                            # Skip others
                            break

        # If Sublime Text version is higher than 2
        else:
            # Get project file path using API.
            proj_file_path = window.project_file_name()

        # If project file path is empty
        if not proj_file_path:
            # Exit
            return

        # If project file path is equal to current value
        if proj_file_path == self._proj_file_path:
            # Exit
            return

        # If project file path is not existing
        if not os.path.isfile(proj_file_path):
            # Exit
            return

        # Message
        print('# {0}'.format(_PACKAGE_NAME))

        # Get project settings
        try:
            with codecs.open(
                    proj_file_path, encoding='utf-8') as proj_file_obj:

                # Read file text, which should be JSON data
                proj_file_text = proj_file_obj.read()

                # Parse JSON data into dict
                proj_file_dict = json.loads(proj_file_text)

                # Get "settings" dict
                proj_settings = proj_file_dict.get('settings', {})

        except Exception:
            # Get traceback
            exc_tb_s = traceback.format_exception(*sys.exc_info())

            exc_tb_text = ''.join(exc_tb_s)

            # Message
            print('Error: Failed parsing project file: {0}\n{1}'.format(
                proj_file_path, exc_tb_text))

            # Exit
            return

        # Get setting
        psps_dir = proj_settings.get(
            'project_specific_packages_directory',
            'sublime_packages',
        )

        # Save as current value
        self._proj_file_path = proj_file_path

        # Message
        print('Project: {0}'.format(proj_file_path))

        # If the directory path is not absolute
        if not os.path.isabs(psps_dir):
            # Get project file's directory path
            proj_file_dir = os.path.dirname(proj_file_path)

            # Create an absolute path
            psps_dir = os.path.join(proj_file_dir, psps_dir)

        # If the directory path is not existing
        if not os.path.isdir(psps_dir):
            # Message
            print(
                "Error: Missing project's packages dir: {0}".format(psps_dir)
            )

            # Exit
            return

        # Get Sublime Text's "Packages" directory path
        sublime_packages_dir = sublime.packages_path()

        # If the directory path is not existing
        if not os.path.isdir(sublime_packages_dir):
            # Message
            print(
                "Error: Missing Sublime Text's packages dir: {0}".format(
                    sublime_packages_dir)
            )

            # Exit
            return

        # Message
        print('From: {0}\nTo: {1}'.format(
            psps_dir, sublime_packages_dir)
        )

        # Copy "project-specific packages" directory to Sublime Text's
        # "Packages" directory
        try:
            # If Sublime Text version is 2
            if sublime.version().startswith('2'):
                # Set copy function
                copy_tree_func = self.copy_tree_py2

                # Set kwargs
                copy_tree_kwargs = dict(
                    symlinks=True
                )

            # If Sublime Text version is higher than 2
            else:
                # Set copy function
                copy_tree_func = copy_tree_py3

                # Set kwargs
                copy_tree_kwargs = dict(
                    preserve_mode=1,
                    preserve_times=1,
                    preserve_symlinks=1,
                )

            # Copy
            dst_file_path_s = copy_tree_func(
                src=psps_dir,
                dst=sublime_packages_dir,
                **copy_tree_kwargs
            )

        except Exception:
            # Get traceback
            exc_tb_s = traceback.format_exception(*sys.exc_info())

            exc_tb_text = ''.join(exc_tb_s)

            # Message
            print(
                'Error: Coping failed:\n{0}'.format(exc_tb_text)
            )

            # Exit
            return

        # Get path prefix length.
        # "+ 1" means to remove a slash.
        path_prefix_length = len(sublime_packages_dir) + 1

        # List of copied file relative paths
        copied_file_rel_path_s = []

        # Start to collect copied file relative paths
        for dst_file_path in dst_file_path_s:
            # If the path starts with the prefix
            if dst_file_path.startswith(sublime_packages_dir):
                # Get relative path
                copied_file_rel_path = dst_file_path[path_prefix_length:]
            # If the path not starts with the prefix (should not happen)
            else:
                # Use the path as is.
                copied_file_rel_path = dst_file_path

            # Add to the list
            copied_file_rel_path_s.append(copied_file_rel_path)

        # Get the listing text
        copied_file_listing_text = '\n'.join(copied_file_rel_path_s)

        # Message
        print('Copied:\n{0}'.format(copied_file_listing_text))

        # Message
        print('Time: {0}'.format(datetime.now().strftime('%H:%M:%S')))

    # "copy_tree" function for Sublime Text 2.
    #
    # Sublime Text 2's "shutil.copytree" uses "os.makedirs", which will raise
    # an error when the directory to create is existing. So it is not usable in
    # this case. Create one instead.
    #
    # Modified from:
    # https://docs.python.org/release/2.6.5/library/shutil.html?highlight=shutil#example
    def copy_tree_py2(self, src, dst, symlinks=False):
        """
        @param src: source directory.
        @param dst: destination directory.
        @param symlinks: copy symlinks as-is.
        """

        # Get list of files in the source directory
        name_s = os.listdir(src)

        # Create destination directory if not exists
        try:
            os.makedirs(dst)
            # ^ Raise error if directory "dst" exists.
        except Exception:
            # Ignore the error
            pass

        # A list of copied file paths
        copied_list = []

        # Start to copy
        for name in name_s:
            # Get source file path
            srcname = os.path.join(src, name)

            # Get destination file path
            dstname = os.path.join(dst, name)

            try:
                # If copy symlinks as-is and the source file is a symlinks
                if symlinks and os.path.islink(srcname):
                    # Get target file path
                    linkto = os.readlink(srcname)

                    # Create destination symlink
                    os.symlink(linkto, dstname)

                    # Add to copied list
                    copied_list.append(dstname)

                # If the source file is a directory
                elif os.path.isdir(srcname):
                    # Copy the directory recursively
                    copied_list_sub = self.copy_tree_py2(
                        srcname, dstname, symlinks)

                    # Add to copied list
                    copied_list.extend(copied_list_sub)

                # If conditions above are not met
                else:
                    # Copy the source file as a regular file
                    copy2(srcname, dstname)

                    # Add to copied list
                    copied_list.append(dstname)

            except Exception:
                # Get traceback
                exc_tb_s = traceback.format_exception(*sys.exc_info())

                exc_tb_text = ''.join(exc_tb_s)

                # Message
                print(
                    'Error: Coping failed:\n{0}'.format(exc_tb_text)
                )

        # Copy file status
        try:
            # Copy file status
            copystat(src, dst)

        except WindowsError:
            # Can't copy file access times on Windows
            pass

        except Exception:
            # Get traceback
            exc_tb_s = traceback.format_exception(*sys.exc_info())

            exc_tb_text = ''.join(exc_tb_s)

            # Message
            print(
                'Error: Coping file status failed:\n{0}'.format(exc_tb_text)
            )

        # Return the copied list
        return copied_list
