"""truffleHog3 unittests."""

import git
import os
import sys
import json
import io
import re
from collections import namedtuple
from truffleHog import truffleHog
from mock import patch 
from mock import MagicMock

    def test_local_file(self):
        sys.argv = [PATH, "./tests/test_slack_token.json"]
        self.assertEqual(1, cli.run(no_history=True, whitelist=[]))

    def test_local_directory_no_history(self):
        sys.argv = [PATH, "./tests"]
        self.assertEqual(1, cli.run(no_history=True, json=True))

    def test_remote_with_history(self):
        sys.argv = [PATH, REPO]
        self.assertEqual(1, cli.run(no_history=False, branch=None))

    def test_branch(self):
        sys.argv = [PATH, REPO]
        self.assertEqual(1, cli.run(branch="master"))


class TestCore(unittest.TestCase):

    def test_shannon(self):
        random_stringB64 = ("ZWVTjPQSdhwRgl204Hc51YCsritMIzn8"
                            "B=/p9UyeX7xu6KkAGqfm3FJ+oObLDNEva")
        random_stringHex = "b3A0a1FDfe86dcCE945B72"
        self.assertGreater(
            core._shannon_entropy(
                random_stringB64,
                core.BASE64_CHARS),
            4.5
        )
        self.assertGreater(
            core._shannon_entropy(
                random_stringHex,
                core.HEX_CHARS),
            3
        )

    def test_return_correct_commit_hash(self):
        # Start at commit d15627104d07846ac2914a976e8e347a663bbd9b, which
        # is immediately followed by a secret inserting commit:
        # 9ed54617547cfca783e0f81f8dc5c927e3d1e345
        since_commit = "d15627104d07846ac2914a976e8e347a663bbd9b"
        commit_w_secret = "9ed54617547cfca783e0f81f8dc5c927e3d1e345"
        cross_valdiating_commit_w_secret_comment = "OH no a secret"

        with TemporaryDirectory() as tmp:
            git.Repo.clone_from(REPO, tmp)
            core.config.since_commit = since_commit
            results = core.search_history(tmp)

        filtered_results = list(filter(
            lambda r: r["commitHash"] == commit_w_secret,
            results
        ))
        self.assertEqual(1, len(filtered_results))
        self.assertEqual(commit_w_secret, filtered_results[0]['commitHash'])
        # Additionally, we cross-validate the commit comment matches the expected comment
        self.assertEqual(cross_valdiating_commit_w_secret_comment, filtered_results[0]['commit'].strip())

    @patch('truffleHog.truffleHog.clone_git_repo')
    @patch('truffleHog.truffleHog.Repo')
    @patch('shutil.rmtree')
    def test_branch(self, rmtree_mock, repo_const_mock, clone_git_repo):
        repo = MagicMock()
        repo_const_mock.return_value = repo
        truffleHog.find_strings("test_repo", branch="testbranch")
        repo.remotes.origin.fetch.assert_called_once_with("testbranch")
    def test_path_included(self):
        Blob = namedtuple('Blob', ('a_path', 'b_path'))
        blobs = {
            'file-root-dir': Blob('file', 'file'),
            'file-sub-dir': Blob('sub-dir/file', 'sub-dir/file'),
            'new-file-root-dir': Blob(None, 'new-file'),
            'new-file-sub-dir': Blob(None, 'sub-dir/new-file'),
            'deleted-file-root-dir': Blob('deleted-file', None),
            'deleted-file-sub-dir': Blob('sub-dir/deleted-file', None),
            'renamed-file-root-dir': Blob('file', 'renamed-file'),
            'renamed-file-sub-dir': Blob('sub-dir/file', 'sub-dir/renamed-file'),
            'moved-file-root-dir-to-sub-dir': Blob('moved-file', 'sub-dir/moved-file'),
            'moved-file-sub-dir-to-root-dir': Blob('sub-dir/moved-file', 'moved-file'),
            'moved-file-sub-dir-to-sub-dir': Blob('sub-dir/moved-file', 'moved/moved-file'),
        }
        src_paths = set(blob.a_path for blob in blobs.values() if blob.a_path is not None)
        dest_paths = set(blob.b_path for blob in blobs.values() if blob.b_path is not None)
        all_paths = src_paths.union(dest_paths)
        all_paths_patterns = [re.compile(re.escape(p)) for p in all_paths]
        overlap_patterns = [re.compile(r'sub-dir/.*'), re.compile(r'moved/'), re.compile(r'[^/]*file$')]
        sub_dirs_patterns = [re.compile(r'.+/.+')]
        deleted_paths_patterns = [re.compile(r'(.*/)?deleted-file$')]
        for name, blob in blobs.items():
            self.assertTrue(truffleHog.path_included(blob),
                            '{} should be included by default'.format(blob))
            self.assertTrue(truffleHog.path_included(blob, include_patterns=all_paths_patterns),
                            '{} should be included with include_patterns: {}'.format(blob, all_paths_patterns))
            self.assertFalse(truffleHog.path_included(blob, exclude_patterns=all_paths_patterns),
                             '{} should be excluded with exclude_patterns: {}'.format(blob, all_paths_patterns))
            self.assertFalse(truffleHog.path_included(blob,
                                                      include_patterns=all_paths_patterns,
                                                      exclude_patterns=all_paths_patterns),
                             '{} should be excluded with overlapping patterns: \n\tinclude: {}\n\texclude: {}'.format(
                                 blob, all_paths_patterns, all_paths_patterns))
            self.assertFalse(truffleHog.path_included(blob,
                                                      include_patterns=overlap_patterns,
                                                      exclude_patterns=all_paths_patterns),
                             '{} should be excluded with overlapping patterns: \n\tinclude: {}\n\texclude: {}'.format(
                                 blob, overlap_patterns, all_paths_patterns))
            self.assertFalse(truffleHog.path_included(blob,
                                                      include_patterns=all_paths_patterns,
                                                      exclude_patterns=overlap_patterns),
                             '{} should be excluded with overlapping patterns: \n\tinclude: {}\n\texclude: {}'.format(
                                 blob, all_paths_patterns, overlap_patterns))
            path = blob.b_path if blob.b_path else blob.a_path
            if '/' in path:
                self.assertTrue(truffleHog.path_included(blob, include_patterns=sub_dirs_patterns),
                                '{}: inclusion should include sub directory paths: {}'.format(blob, sub_dirs_patterns))
                self.assertFalse(truffleHog.path_included(blob, exclude_patterns=sub_dirs_patterns),
                                 '{}: exclusion should exclude sub directory paths: {}'.format(blob, sub_dirs_patterns))
            else:
                self.assertFalse(truffleHog.path_included(blob, include_patterns=sub_dirs_patterns),
                                 '{}: inclusion should exclude root directory paths: {}'.format(blob, sub_dirs_patterns))
                self.assertTrue(truffleHog.path_included(blob, exclude_patterns=sub_dirs_patterns),
                                '{}: exclusion should include root directory paths: {}'.format(blob, sub_dirs_patterns))
            if name.startswith('deleted-file-'):
                self.assertTrue(truffleHog.path_included(blob, include_patterns=deleted_paths_patterns),
                                '{}: inclusion should match deleted paths: {}'.format(blob, deleted_paths_patterns))
                self.assertFalse(truffleHog.path_included(blob, exclude_patterns=deleted_paths_patterns),
                                 '{}: exclusion should match deleted paths: {}'.format(blob, deleted_paths_patterns))



    @patch('truffleHog.truffleHog.clone_git_repo')
    @patch('truffleHog.truffleHog.Repo')
    @patch('shutil.rmtree')
    def test_repo_path(self, rmtree_mock, repo_const_mock, clone_git_repo):
        truffleHog.find_strings("test_repo", repo_path="test/path/")
        rmtree_mock.assert_not_called()
        clone_git_repo.assert_not_called()

if __name__ == '__main__':
    unittest.main()
