# -*- coding: utf-8 -*-
"""
See `prereleaser_middle`.

"""


import re
import os
import os.path
import sys
import glob

def _project_name(data):
    # Return the expected project name in the src/ directory
    project_name = data['name']
    if '.' in project_name:
        # Namespace packages
        project_name = project_name.split('.')[0]
    return project_name

def _new_version_bytes(data):
    # Return the version string as bytes.
    new_version = data['new_version']
    if not isinstance(new_version, bytes):
        new_version_bytes = new_version.encode('ascii')
    else:
        new_version_bytes = new_version
    return new_version_bytes

def _find_replacement_directory(data):
    # Return the directory to begin replacing in, or
    # raise an exception
    base_dir = os.path.join(data['reporoot'], 'src', _project_name(data))
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"Unable to find source directory at {base_dir!r}")
    return base_dir

# What we search for
MATCH_DIRECTIVES = re.compile(b'.. (versionchanged|versionadded|deprecated):: NEXT')
# The replacement pattern
REPLACEMENT_PATTERN = br'.. \1:: %s'

def _handle_file(path, replacement, report=print):
    # Examine the file at *path* replacing any matches of MATCH_DIRECTIVES
    # with the *replacement* (from REPLACEMENT_PATTERN). If anything
    # matched, write the updated file in place. Return a true value if
    # this was done, and a false value if nothing changed.
    with open(path, 'rb') as f:
        contents = f.read()
    new_contents, count = MATCH_DIRECTIVES.subn(replacement, contents)
    if count:
        report("Replaced version NEXT in", path, file=sys.stderr)
        with open(path, 'wb') as f:
            f.write(new_contents)
    return count

def prereleaser_middle(data):
    """
    zest.releaser prerelease middle hook.

    The prerelease step:

        * asks you for a version number
        * updates the setup.py or version.txt and the
          CHANGES/HISTORY/CHANGELOG file
        * offers to commit those changes to git

    Within the middle hook:

        * All data dictionary items are available and some questions
          (like new version number) have been asked.
        * No filesystem changes have been made yet.


    This hook:

    - Adds the version number to ``versionadded``, ``versionchanged`` and
      ``deprecated`` directives in Python source.

    Assumptions:

    - The source is found in ``src/{name}`` where ``name`` comes from
      ``data['name']`` which in turn comes from setup.py.

    .. todo: This does not look at .rst files in the ``docs/`` directory.
    """
    base_dir = _find_replacement_directory(data)
    new_version_bytes = _new_version_bytes(data)
    replacement = REPLACEMENT_PATTERN % (new_version_bytes,)

    pattern = os.path.join(base_dir, "**/*.py")
    found_src = False
    for path in glob.iglob(pattern, recursive=True):
        found_src = True
        _handle_file(path, replacement, data.get('icrs.releaser:report', print))

    if not found_src:
        raise FileNotFoundError(
            f"Unable to find any files using the pattern {pattern!r}"
        )
