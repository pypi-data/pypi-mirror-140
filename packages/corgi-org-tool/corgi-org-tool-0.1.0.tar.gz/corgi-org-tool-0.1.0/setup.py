# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['corgi', 'corgi.lick']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.4,<0.5.0', 'tomli>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['corgi = corgi.app:main']}

setup_kwargs = {
    'name': 'corgi-org-tool',
    'version': '0.1.0',
    'description': 'Command Line parser, agenda and manipulator for org-mode files.',
    'long_description': '# corgi - Command line ORG mode General Interface\n\nCorgi is a command line interface for analyzing and manipulating org-mode\nfiles. It implements its own parser of org syntax and doesn\'t rely on Emacs.\nIt can interoperate with other tools by creating a simple Abstract Syntax\nTree of org documents and outputting it as human-readable JSON. It can also\nrecreate org documents from such JSONs, so any third-party tools must only\nknow how to manipulate them instead of org documents, which is much easier\ntask.\n\nCorgi is good at manipulating document structure, so its main purpose is to\ngive users ability to perform tasks such as refiling or displaying simple\nagendas from command line. I doesn\'t implement most of typical org-mode\nfeatures, like literate programming, spreadsheets etc. It doesn\'t follow\nrecent org-mode. In fact, it doesn\'t do a lot to interpret org-mode sections\nat all (sections are blocks of free text under each headline). Emacs or other\nthird-party tools should be used for that. However, Corgi can be used as\nintermediate step which presents data to other programs in a friendlier way\nthan org documents.\n\nDue to these constraints, Corgi is reliable. Most org-mode features depend on\n"magical" analysis of plain text inside the sections of org documents, but\njust passing through their explicit contents will always work.\n\n## Configuration\n\nCorgi is zero-config program, which means that it doesn\'t need a\nconfiguration file, but it helps if you don\'t like its default behaviour. It\nis configured via a TOML file and is stored in _~/.config/corgi/config.toml_\n(Corgi also respects `XDG_CONFIG_HOME` variable).\n\nThere are two main sections of configuration file: `[corgi]`, for\ncorgi-specific options and `[org]` for equivalents of org-mode configuration\noptions. Options in `[org]` section are named similarily to their org-mode\nequivalents: dashes are replaced with underscores and _org-_ prefix is\nremoved, due to being in `[org]` section. Here are the most important ones:\n\ncorgi.default_editor\n: text editor which corgi runs for example when running a capture subcommand.\n  Corgi creates a temporary org file which is placed in either a `{}`\n  placeholder, or at the end of the string.\n\norg.default_notes_file\n: default notes file for capture. This file is also counted towards agenda\n  files.\n\norg.agenda_files\n: list of files which will be scanned to create agenda views. This list might\n  contain directories, in which case all org files inside them will be used.\n  It can also contain a globbing expressions, which select all the matching\n  files. Example: `["~/org", "~/sync/*.org", "~/file.org"]`\n\norg.todo_keywords\n: list of keywords recognized as TODO states. It has the same format as\n  org-todo-keywords. Example: `["TODO", "WAIT", "|", "DONE"]`. If bar is not\n  present on that list, the last keyword will be considered as "done" state.\n\n## Usage\n\nCorgi has built-in help:\n\n```\n$ corgi --help\n$ corgi <subcommand> --help\n```\n\n### Dumping org files to and from JSON\n\nBelow commands show how Corgi can be used as a filter to serialize org files\ninto JSON and then deserialize this JSON back to org files. This is extremely\npowerful technique, because it lets using third party programs, which only\nhave to deal with JSON and don\'t need to understand the org syntax.\n\n```\n$ corgi serialize file.org | corgi deserialize\n```\n\nOne exampe is to use `jq`, a powerful and popular command-line JSON\nprocessor. We could use it for example to filter only headlines which have a\nTODO state:\n\n```\n$ corgi serialize file.org | jq \'map(select(.keyword == "TODO"))\' | corgi deserialize\n```\n\n### Agenda\n\nOne of the most recognized org-mode features is its agenda. Corgi implements\nbasic agenda views (although they are not nearly as powerful as Emacs\' ones,\nnor they are interactive).\n\n#### Week Agenda\n\nWeek agenda is the default view of Corgi and shows a week view of planned\ntasks.\n\n```\n$ corgi agenda\n```\n\nThis list can be filtered only to TODO entries under a specific headline, in\nspecific file:\n\n```\n$ corgi agenda --filter-path todo.org/Current\n```\n\nWe can also use different files than the ones configured by org.agenda_files:\n\n```\n$ corgi agenda ~/foo/bar/{file1,file2}.org \\\n    --filter-path file1.org/Headline \\\n    --filter-path "file2.org/Other headline"\n```\n\n#### List of TODO entries\n\nTo produce a list of all TODO entries from org.agenda_files, we can use\n`agenda --todo` subcommand:\n\n```\n$ corgi agenda --todo\n```\n\nTODO agenda can use the same switches (e.g. `--filter-path` as the default\nagenda.\n',
    'author': 'Michal Goral',
    'author_email': 'dev@goral.net.pl',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://git.goral.net.pl/mgoral/corgi',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
