[![Package Version](https://img.shields.io/pypi/v/truffleHog3.svg)](https://pypi.org/project/truffleHog3)
![Python Version](https://img.shields.io/badge/python-3.6%2B-informational.svg)
[![Build Status](https://travis-ci.com/feeltheajf/truffleHog3.svg?branch=master)](https://travis-ci.com/feeltheajf/truffleHog3)
[![Code Coverage](https://codecov.io/gh/feeltheajf/truffleHog3/branch/master/graph/badge.svg)](https://codecov.io/gh/feeltheajf/truffleHog3)
[![Downloads](https://pepy.tech/badge/trufflehog3)](https://pepy.tech/project/trufflehog3)


# truffleHog3
This is an enhanced version of [truffleHog](https://github.com/dxa4481/truffleHog) scanner


## New

- Python 3.6
- flake8 compliant code
- output to file option
- option to disable Git history checks - scan simple files/folders
- option to exclude files/directories
- config file support with automatic detection of [trufflehog.json](https://github.com/feeltheajf/truffleHog3/blob/master/trufflehog.json.example) config in source code directory


With the `--include_paths` and `--exclude_paths` options, it is also possible to limit scanning to a subset of objects in the Git history by defining regular expressions (one per line) in a file to match the targeted object paths. To illustrate, see the example include and exclude files below:

_include-patterns.txt:_
```ini
src/
# lines beginning with "#" are treated as comments and are ignored
gradle/
# regexes must match the entire path, but can use python's regex syntax for
# case-insensitive matching and other advanced options
(?i).*\.(properties|conf|ini|txt|y(a)?ml)$
(.*/)?id_[rd]sa$
```

_exclude-patterns.txt:_
```ini
(.*/)?\.classpath$
.*\.jmx$
(.*/)?test/(.*/)?resources/
```

These filter files could then be applied by:
```bash
trufflehog --include_paths include-patterns.txt --exclude_paths exclude-patterns.txt file://path/to/my/repo.git
```
With these filters, issues found in files in the root-level `src` directory would be reported, unless they had the `.classpath` or `.jmx` extension, or if they were found in the `src/test/dev/resources/` directory, for example. Additional usage information is provided when calling `trufflehog` with the `-h` or `--help` options.

These features help cut down on noise, and makes the tool easier to shove into a devops pipeline.

![Example](https://i.imgur.com/YAXndLD.png)
## Installation

Package is available on [PyPI](https://pypi.org/project/truffleHog3)

```
pip install truffleHog3
```


## Customizing

List of regexes was moved into repository, see [regexes.json](https://github.com/feeltheajf/truffleHog3/blob/master/truffleHog3/regexes.json)


## Help

```
usage: trufflehog3 [options] source

Find secrets in your codebase.

positional arguments:
  source              URL or local path for secret searching

optional arguments:
  -h, --help          show this help message and exit
  -c, --config        path to config file
  -r, --rules         ignore default regexes and source from json
  -o, --output        write report to file
  -b, --branch        name of the branch to be scanned
  -m, --max-depth     max commit depth for searching
  -s, --since-commit  scan starting from a given commit hash
  --json              output in JSON
  --exclude           exclude paths from scan
  --whitelist         skip matching strings
  --no-regex          disable high signal regex checks
  --no-entropy        disable entropy checks
  --no-history        disable commit history check
```


## Thanks

Special thanks to Dylan Ayrey ([@dxa4481](https://github.com/dxa4481)), developer of the original [truffleHog](https://github.com/dxa4481/truffleHog) scanner
