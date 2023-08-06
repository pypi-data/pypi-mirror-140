"""
Converter for `git diff` paths
"""
import os
from posixpath import isabs
import sys

from dcov.command_runner import execute


class GitPathTool:
    """
    Converts `git diff` paths to absolute paths or relative paths to cwd.
    This class should be used throughout the project to change paths from
    the paths yielded by `git diff` to correct project paths
    """

    _cwd = None
    _root = None

    @classmethod
    def set_cwd(cls, cwd):
        """
        Set the cwd that is used to manipulate paths.
        """
        if not cwd:
            try:
                cwd = os.getcwdu()
            except AttributeError:
                cwd = os.getcwd()
        if isinstance(cwd, bytes):
            cwd = cwd.decode(sys.getdefaultencoding())
        cls._cwd = cwd
        cls._root = cls._git_root()

    @classmethod
    def relative_path(cls, git_diff_path):
        """
        Returns git_diff_path relative to cwd.
        """
        # Remove git_root from src_path for searching the correct filename
        # If cwd is `/home/user/work/diff-cover/diff_cover`
        # and git_diff_path is `diff_cover/violations_reporter.py`
        # search for `violations_reporter.py`
        if os.path.isabs(git_diff_path):
            # print("cwd: {}\ndiff path: {}\n".format(cls._cwd, git_diff_path))  
            return os.path.relpath(git_diff_path, cls._cwd)
        root_rel_path = os.path.relpath(cls._cwd, cls._root)
        return os.path.relpath(git_diff_path, root_rel_path)

    @classmethod
    def absolute_path(cls, src_path):
        """
        Returns absolute git_diff_path
        """
        # If cwd is `/home/user/work/diff-cover/diff_cover`
        # and src_path is `other_package/some_file.py`
        # search for `/home/user/work/diff-cover/other_package/some_file.py`

        return os.path.join(cls._root, src_path)

    @classmethod
    def compare_path(cls, path1, path2):
        pass

    @classmethod
    def _git_root(cls):
        """
        Returns the output of `git rev-parse --show-toplevel`, which
        is the absolute path for the git project root.
        """
        command = ["git", "rev-parse", "--show-toplevel", "--encoding=utf-8"]
        git_root = execute(command)[0]
        return git_root.split("\n", maxsplit=1)[0] if git_root else ""
        
