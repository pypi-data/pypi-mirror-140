# Installation
Depending on if you want only this tool, the full set of PNU tools, or PNU plus a selection of additional third-parties tools, use one of these commands:

pip install [pnu-dcmp](https://pypi.org/project/pnu-dcmp/)
<br>
pip install [PNU](https://pypi.org/project/PNU/)
<br>
pip install [pytnix](https://pypi.org/project/pytnix/)

# DCMP(1)

## NAME
dcmp - compare two directories, deduplicating if needed

## SYNOPSIS
**dcmp**
\[--dedup\]
\[-h|--nosymlinks\]
\[-s|--silent|--quiet\]
\[-v|--verbose\]
\[--debug\]
\[--help|-?\]
\[--version\]
\[--\]
directory1 directory2

## DESCRIPTION
The **dcmp** utility compares two directories contents and writes the results to the standard output.
By default, **dcmp** is silent if the directories are the same;
if they differ, the differences are reported with a leading:
* '!' if files contents are different
* '+' if the file or directory appears in directory1 but not in directory2
* '-' if the file or directory appears in directory2 but not in directory1
* '=' if the files contents are identical and you used the *-v|--verbose* option

If you use the *-s|--silent|--quiet* option, differences won't be reported and the overall result will be returned though the exit status
(thus stopping the comparison at the first difference).

By default, **dcmp** follows symbolic links to directories, unless you tell it not to do so with the *-h|--nosymlinks* option,
or you use the *--dedup* option for deduplicating the first directory, removing identical files
(ie. those having the same [SHA-256 message digest](https://en.wikipedia.org/wiki/SHA-2)) and symbolic links, as well as empty directories sitting there.

### OPTIONS
The following options are available:

Options | Use
------- | ---
--dedup|In dir1, remove empty dirs and files which are identical to those in dir2
-h\|--nosymlinks|Do not follow symbolic links
-s\|--silent\|--quiet|Print nothing for differing dirs; return exit status only
-v\|--verbose|Print identical dirs and files names
--debug|Enable debug mode
--help\|-?|Print usage and a short help message and exit
--version|Print version and exit
--|Options processing terminator

## ENVIRONMENT
The *DCMP_DEBUG* environment variable can also be set to any value to enable debug mode.

## EXIT STATUS
The **dcmp** utility exits with one of the following values:
* 0: The directories are identical
* 1: The directories are different
* \>1: An error occurred

## SEE ALSO
[cmp(1)](https://www.freebsd.org/cgi/man.cgi?query=cmp),
[sha256(1)](https://www.freebsd.org/cgi/man.cgi?query=sha256)

## STANDARDS
The **dcmp** utility is not a standard UNIX command.

This implementation tries to follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for [Python](https://www.python.org/) code.

## PORTABILITY
To be tested under Windows.

## HISTORY
This implementation was made for the [PNU project](https://github.com/HubTou/PNU).

The **dcmp** utility was made to help spot potential differences between restored backups and current files and directories.

## LICENSE
It is available under the [3-clause BSD license](https://opensource.org/licenses/BSD-3-Clause).

## AUTHORS
[Hubert Tournier](https://github.com/HubTou)

