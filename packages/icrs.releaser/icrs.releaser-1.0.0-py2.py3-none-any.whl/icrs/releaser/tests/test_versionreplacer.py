# -*- coding: utf-8 -*-

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import os
import os.path
import tempfile
import unittest

from .. import versionreplacer

class TestFuncs(unittest.TestCase):

    def test_project_name_plain(self):
        self.assertEqual('foo',
                         versionreplacer._project_name({'name': 'foo'}))

    def test_project_name_dotted(self):
        self.assertEqual('foo',
                         versionreplacer._project_name({'name': 'foo.bar'}))

    def test_new_version_bytes_bytes(self):
        self.assertEqual(
            b'1.0',
            versionreplacer._new_version_bytes({'new_version': b'1.0'})
        )

    def test_new_version_bytes_str(self):
        self.assertEqual(
            b'1.0',
            versionreplacer._new_version_bytes({'new_version': '1.0'})
        )

    def test_find_replacement_directory_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_name = 'foo'
            path = os.path.join(tmp, 'src', project_name)
            os.makedirs(path)

            data = {
                'reporoot': tmp,
                'name': project_name
            }
            self.assertEqual(
                path,
                versionreplacer._find_replacement_directory(data)
            )

    def test_find_replacement_directory_dne(self):
        with tempfile.TemporaryDirectory() as tmp:
            project_name = 'foo'
            data = {
                'reporoot': tmp,
                'name': project_name
            }
            with self.assertRaises(FileNotFoundError):
                versionreplacer._find_replacement_directory(data)

    def _setup_one_file(self, tmp_dir):
        import textwrap
        src = os.path.join(tmp_dir, 'src', 'project')
        os.makedirs(src)
        path = os.path.join(src, 'foo.py')
        with open(path, 'w', encoding='utf-8') as f:
            # defeat the replacement in this file!
            next = "NEXT"
            f.write(textwrap.dedent(f"""\
            .. versionchanged:: {next}
            .. deprecated:: {next}
            .. versionadded:: {next}
            .. versionnotmatched:: {next}
            ..versionchanged:: {next}
            """))

        reports = []
        def report(msg, path, file):
            reports.append((msg, path, file))

        def validate():
            import sys
            self.assertEqual(reports, [
                ("Replaced version NEXT in", path, sys.stderr)
            ])
            with open(path, 'r', encoding='utf-8') as f:
                contents = f.read()
            self.assertEqual(contents.splitlines(), [
                '.. versionchanged:: 1.0',
                '.. deprecated:: 1.0',
                '.. versionadded:: 1.0',
                '.. versionnotmatched:: NEXT',
                '..versionchanged:: NEXT'
            ])
        return path, b"1.0", validate, report

    def test_handle_file_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, new_version, content_validator, report = self._setup_one_file(tmp)
            replacement = br".. \1:: %s" % (new_version,)
            result = versionreplacer._handle_file(path, replacement, report)
            self.assertTrue(result)

            content_validator()

    def test_handle_file_no_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'foo.py')
            with open(path, 'w', encoding='utf-8') as f:
                f.write('Hello nurse!\n')
            before = os.stat(path)

            replacement = br".. \1:: 1.0"
            result = versionreplacer._handle_file(path, replacement)
            self.assertFalse(result)
            self.assertEqual(os.stat(path), before)

            with open(path, 'r', encoding='utf-8') as f:
                contents = f.read()
            self.assertEqual(contents, "Hello nurse!\n")

    def test_prereleaser_middle_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            _path, new_version, content_validator, report = self._setup_one_file(tmp)
            data = {
                'name': 'project',
                'reporoot': tmp,
                'new_version': new_version,
                'icrs.releaser:report': report
            }
            versionreplacer.prereleaser_middle(data)
            content_validator()

    def test_prereleaser_middle_no_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, new_version, _content_validator, report = self._setup_one_file(tmp)
            data = {
                'name': 'project',
                'reporoot': tmp,
                'new_version': new_version,
                'icrs.releaser:report': report
            }
            os.remove(path)

            with self.assertRaisesRegex(FileNotFoundError, "find any files using the pattern"):
                versionreplacer.prereleaser_middle(data)

if __name__ == '__main__':
    unittest.main()
