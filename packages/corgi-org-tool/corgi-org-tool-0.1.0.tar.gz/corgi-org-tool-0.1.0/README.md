# corgi - Command line ORG mode General Interface

Corgi is a command line interface for analyzing and manipulating org-mode
files. It implements its own parser of org syntax and doesn't rely on Emacs.
It can interoperate with other tools by creating a simple Abstract Syntax
Tree of org documents and outputting it as human-readable JSON. It can also
recreate org documents from such JSONs, so any third-party tools must only
know how to manipulate them instead of org documents, which is much easier
task.

Corgi is good at manipulating document structure, so its main purpose is to
give users ability to perform tasks such as refiling or displaying simple
agendas from command line. I doesn't implement most of typical org-mode
features, like literate programming, spreadsheets etc. It doesn't follow
recent org-mode. In fact, it doesn't do a lot to interpret org-mode sections
at all (sections are blocks of free text under each headline). Emacs or other
third-party tools should be used for that. However, Corgi can be used as
intermediate step which presents data to other programs in a friendlier way
than org documents.

Due to these constraints, Corgi is reliable. Most org-mode features depend on
"magical" analysis of plain text inside the sections of org documents, but
just passing through their explicit contents will always work.

## Configuration

Corgi is zero-config program, which means that it doesn't need a
configuration file, but it helps if you don't like its default behaviour. It
is configured via a TOML file and is stored in _~/.config/corgi/config.toml_
(Corgi also respects `XDG_CONFIG_HOME` variable).

There are two main sections of configuration file: `[corgi]`, for
corgi-specific options and `[org]` for equivalents of org-mode configuration
options. Options in `[org]` section are named similarily to their org-mode
equivalents: dashes are replaced with underscores and _org-_ prefix is
removed, due to being in `[org]` section. Here are the most important ones:

corgi.default_editor
: text editor which corgi runs for example when running a capture subcommand.
  Corgi creates a temporary org file which is placed in either a `{}`
  placeholder, or at the end of the string.

org.default_notes_file
: default notes file for capture. This file is also counted towards agenda
  files.

org.agenda_files
: list of files which will be scanned to create agenda views. This list might
  contain directories, in which case all org files inside them will be used.
  It can also contain a globbing expressions, which select all the matching
  files. Example: `["~/org", "~/sync/*.org", "~/file.org"]`

org.todo_keywords
: list of keywords recognized as TODO states. It has the same format as
  org-todo-keywords. Example: `["TODO", "WAIT", "|", "DONE"]`. If bar is not
  present on that list, the last keyword will be considered as "done" state.

## Usage

Corgi has built-in help:

```
$ corgi --help
$ corgi <subcommand> --help
```

### Dumping org files to and from JSON

Below commands show how Corgi can be used as a filter to serialize org files
into JSON and then deserialize this JSON back to org files. This is extremely
powerful technique, because it lets using third party programs, which only
have to deal with JSON and don't need to understand the org syntax.

```
$ corgi serialize file.org | corgi deserialize
```

One exampe is to use `jq`, a powerful and popular command-line JSON
processor. We could use it for example to filter only headlines which have a
TODO state:

```
$ corgi serialize file.org | jq 'map(select(.keyword == "TODO"))' | corgi deserialize
```

### Agenda

One of the most recognized org-mode features is its agenda. Corgi implements
basic agenda views (although they are not nearly as powerful as Emacs' ones,
nor they are interactive).

#### Week Agenda

Week agenda is the default view of Corgi and shows a week view of planned
tasks.

```
$ corgi agenda
```

This list can be filtered only to TODO entries under a specific headline, in
specific file:

```
$ corgi agenda --filter-path todo.org/Current
```

We can also use different files than the ones configured by org.agenda_files:

```
$ corgi agenda ~/foo/bar/{file1,file2}.org \
    --filter-path file1.org/Headline \
    --filter-path "file2.org/Other headline"
```

#### List of TODO entries

To produce a list of all TODO entries from org.agenda_files, we can use
`agenda --todo` subcommand:

```
$ corgi agenda --todo
```

TODO agenda can use the same switches (e.g. `--filter-path` as the default
agenda.
