[![Sourcecode on GitHub](https://img.shields.io/badge/pyTooling-pyTooling.CLIAbstraction-323131.svg?logo=github&longCache=true)](https://github.com/pyTooling/pyTooling.CLIAbstraction)
[![Sourcecode License](https://img.shields.io/pypi/l/pyTooling.CLIAbstraction?logo=GitHub&label=code%20license)](LICENSE.md)
[![GitHub tag (latest SemVer incl. pre-release)](https://img.shields.io/github/v/tag/pyTooling/pyTooling.CLIAbstraction?logo=GitHub&include_prereleases)](https://github.com/pyTooling/pyTooling.CLIAbstraction/tags)
[![GitHub release (latest SemVer incl. including pre-releases)](https://img.shields.io/github/v/release/pyTooling/pyTooling.CLIAbstraction?logo=GitHub&include_prereleases)](https://github.com/pyTooling/pyTooling.CLIAbstraction/releases/latest)
[![GitHub release date](https://img.shields.io/github/release-date/pyTooling/pyTooling.CLIAbstraction?logo=GitHub)](https://github.com/pyTooling/pyTooling.CLIAbstraction/releases)
[![Dependents (via libraries.io)](https://img.shields.io/librariesio/dependents/pypi/pyTooling.CLIAbstraction?logo=librariesdotio)](https://github.com/pyTooling/pyTooling.CLIAbstraction/network/dependents)  
[![GitHub Workflow - Build and Test Status](https://img.shields.io/github/workflow/status/pyTooling/pyTooling.CLIAbstraction/Unit%20Testing,%20Coverage%20Collection,%20Package,%20Release,%20Documentation%20and%20Publish?label=Pipeline&logo=GitHub%20Actions&logoColor=FFFFFF)](https://github.com/pyTooling/pyTooling.CLIAbstraction/actions/workflows/Pipeline.yml)
[![Codacy - Quality](https://img.shields.io/codacy/grade/3806b49bc754407d900232503a8f7d31?logo=Codacy)](https://www.codacy.com/gh/pyTooling/pyTooling.CLIAbstraction)
[![Codacy - Coverage](https://img.shields.io/codacy/coverage/3806b49bc754407d900232503a8f7d31?logo=Codacy)](https://www.codacy.com/gh/pyTooling/pyTooling.CLIAbstraction)
[![Codecov - Branch Coverage](https://img.shields.io/codecov/c/github/pyTooling/pyTooling.CLIAbstraction?logo=Codecov)](https://codecov.io/gh/pyTooling/pyTooling.CLIAbstraction)
[![Libraries.io SourceRank](https://img.shields.io/librariesio/sourcerank/pypi/pyTooling.CLIAbstraction?logo=librariesdotio)](https://libraries.io/github/pyTooling/pyTooling.CLIAbstraction/sourcerank)  
[![PyPI](https://img.shields.io/pypi/v/pyTooling.CLIAbstraction?logo=PyPI&logoColor=FBE072)](https://pypi.org/project/pyTooling.CLIAbstraction/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyTooling.CLIAbstraction?logo=PyPI&logoColor=FBE072)
![PyPI - Status](https://img.shields.io/pypi/status/pyTooling.CLIAbstraction?logo=PyPI&logoColor=FBE072)
[![Libraries.io status for latest release](https://img.shields.io/librariesio/release/pypi/pyTooling.CLIAbstraction?logo=librariesdotio)](https://libraries.io/github/pyTooling/pyTooling.CLIAbstraction)
[![Requires.io](https://img.shields.io/requires/github/pyTooling/pyTooling.CLIAbstraction)](https://requires.io/github/pyTooling/pyTooling.CLIAbstraction/requirements/?branch=main)  
[![Read the Docs](https://img.shields.io/readthedocs/pyTooling.CLIAbstraction?label=ReadTheDocs&logo=readthedocs)](https://pyTooling.CLIAbstraction.readthedocs.io/)
[![Documentation License](https://img.shields.io/badge/doc%20license-CC--BY%204.0-green?logo=readthedocs)](LICENSE.md)
[![Documentation - Read Now!](https://img.shields.io/badge/doc-read%20now%20%E2%9E%94-blueviolet?logo=readthedocs)](https://pyTooling.CLIAbstraction.readthedocs.io/)

# pyTooling.CLIAbstraction

pyTooling.CLIAbstraction is an abstraction layer and wrapper for command line programs, so they can be used easily in
Python. All parameters like ``--value=42`` are described as parameters of the executable.


## Main Goals

* Offer access to CLI programs as Python classes.
* Abstract CLI arguments (a.k.a. parameter, option, flag, ...) as members on such a Python class.
* Derive program variants from existing programs.
* Assemble parameters in list format for handover to `subprocess.Popen` with proper escaping and quoting.
* Launch a program with `subprocess.Popen` and hide the complexity of Popen.
* Get a generator object for line-by-line output reading to enable postprocessing of outputs.

## Use Cases

* Wrap command line interfaces of EDA tools (Electronic Design Automation) in Python classes.


## Example

The following example implements a portion of the ``git`` program and its ``commit`` sub-command.

**Git program defining `commit` argument:**

```Python
from pyTooling.CLIAbstraction import CLIArgument, Executable
from pyTooling.CLIAbstraction.Command import CommandArgument
from pyTooling.CLIAbstraction.Flag import LongFlag
from pyTooling.CLIAbstraction.ValuedTupleFlag import ShortTupleFlag

class Git(Executable):
	_executableNames = {
		"Windows": "git.exe",
		"Linux": "git",
		"Darwin": "git"
	}
	
	@CLIArgument()
	class FlagVerbose(LongFlag, name="verbose"):
		"""Print verbose messages."""
	
	@CLIArgument()
	class CommandCommit(CommandArgument, name="commit"):
		"""Command to commit staged files."""
	
	@CLIArgument()
	class ValueCommitMessage(ShortTupleFlag, name="m"):
		"""Specify the commit message."""
	
	def GetCommitTool(self):
		"""Derive a new program from a configured program."""
		tool = self.__class__(executablePath=self._executablePath)
		tool[tool.CommandCommit] = True
		self._CopyParameters(tool)
		
		return tool
```

**Usage:**
```Python
# Create a program instance and set common parameters.
git = Git()
git[git.FlagVerbose] = True

# Derive a variant of that pre-configured program.
commit = git.getCommitTool()
commit[commit.ValueCommitMessage] = "Bumped dependencies."

# Launch the program and parse outputs line-by-line.
commit.StartProcess()
for line in commit.GetLineReader():
	print(line)
```


# Consumers

This layer is used by:

* ✅ [pyEDAA.CLITool](https://github.com/edaa-org/pyEDAA.CLITool)


## Contributors
* [Patrick Lehmann](https://github.com/Paebbels) (Maintainer)
* [Unai Martinez-Corral](https://github.com/umarcor)
* [and more...](https://github.com/pyTooling/pyTooling.CLIAbstraction/graphs/contributors)


## License

This Python package (source code) licensed under [Apache License 2.0](LICENSE.md).  
The accompanying documentation is licensed under [Creative Commons - Attribution 4.0 (CC-BY 4.0)](doc/Doc-License.rst).

-------------------------
SPDX-License-Identifier: Apache-2.0
