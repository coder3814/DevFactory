# Cards in GitHub Projects

How the card standard maps onto a GitHub Project, how to read a project when
writing its profile, and the behaviours of GitHub that break a card if they are
missed. The standard itself is tracker-neutral; this file is the GitHub Projects
binding, named `github-projects` in the board section of a project profile,
`.devfactory/profile.md`.

A card is a repository issue added to the project. Draft items are not cards:
they have no comments or attachments, so an addition has nowhere to be recorded.
A draft item is brought under the standard by converting it to an issue first.

How an agent reaches GitHub — the `gh` CLI, the GitHub MCP server, or something
else — is the team's choice, not this file's. The profile's board section
records it, and the agent follows it.

## Tracker entries in the profile's board section

| Entry | What it holds |
|---|---|
| Owner | The user or organization that owns the project |
| Project | The project's number, from its URL |
| View | The board view the profile is for |
| Repository | The repository new cards are created as issues in, `owner/name` |
| Issue type | The issue type new cards are created as, if the repository has issue types (or: none) |
| Epics | How an epic is marked, for example issue type Epic or label `epic` |
| Access | How the agent reaches GitHub, in the team's words |

The single-select field the view is grouped by, usually Status, holds the card's column.
The plugin reads and moves no column; a project's event hooks
([`../events.md`](../events.md)) set that field when they move a card.

## Naming a card

An issue number is unique only within its repository, and a project can hold
issues from several. A card is named by its URL or by `owner/name#number`. A
bare number means the issue of that number in the profile's repository; if the
project holds issues from more than one repository, ask which one is meant
rather than assuming.

## Where each part of the card lives

The profile's board section says which field each part of the card is written to. An issue
has one rich-text field, its body, so the defaults are the issue title for the
title and the issue body for every other part. A project's own custom fields
are plain text, number, date, single-select or iteration fields; none can hold
headings or lists, so no part is moved into one.

| Card feature | Issue feature |
|---|---|
| Comments | The issue's comments |
| Attachments | See [Attachments](#attachments) |

Issue titles, bodies and comments are always Markdown, so there is no format to
read or set before writing.

## Reading a project

What `configure-project` reads. With the `gh` CLI, the project commands need a
token with the `project` scope (`gh auth refresh -s project`); without it they
fail with a scope error.

- **The owner's projects:** `gh project list --owner <owner> --format json`.
- **A project's fields:** `gh project field-list <number> --owner <owner>
  --format json`, which gives each field's id, name and type, and the options
  of every single-select field.
- **A project's views:** the GraphQL `projectV2.views` connection, which gives
  each view's name, layout (`BOARD_LAYOUT` for a board) and the field it is
  grouped by (`verticalGroupByFields`). The view's columns are that field's
  options.
- **Issue types:** the GraphQL `repository.issueTypes` connection of the
  profile's repository. Issue types come from the repository's organization,
  not the project's owner. A repository owned by a user has none: its
  `issueTypes` is null, and the profile's issue type entry is none.
- **A project's fields a card can carry:** the project's own custom fields
  (text, number, date, single-select, iteration), plus the issue's labels,
  milestone and assignees. These are what `configure-project` offers as
  additional fields.

GitHub requires only a title on an issue and nothing on a project item, so no
field is one the team must fill unless the team says so.

## A card's column is per project

A card's column is the value of the view's grouping field on the card's item
in this project. An issue can sit in several projects, each with its own value,
and the issue's own open or closed state says nothing about its column. Read the
value from the item in the profile's project, never from another project's
item. For one card, read the issue's GraphQL `projectItems` connection with
`fieldValueByName`. `gh project item-list` suits reading many cards, but it
lists only 30 items unless given a `--limit` above the project's item count, and
a card past that is silently missing. Its JSON keys each field by its name with
the first letter lowered, such as `status` for Status and `releaseNotes` for
ReleaseNotes.

## Creating a card

A card is created in two steps: create the issue in the profile's repository,
with its issue type if the profile names one, then add it to the project
(`gh project item-add`). `gh issue create` and `gh issue edit` cannot set an
issue type; set it in the create itself through the API, with the GraphQL
`createIssue` mutation's `issueTypeId`. Set a project field on the item, such as its column,
with `gh project item-edit`, which takes the project's id, the item's id, the
field's id and, for a single-select field, the option's id — never their names.

## Comments

A comment is added to the issue (`gh issue comment`) and stored as Markdown.

## A card's parent

A card's parent, such as its epic, is the issue it is a sub-issue of: the
issue's GraphQL `parent` field. A card's epic is the nearest ancestor marked
as the profile's Epics entry says: follow parents upward until one is, or there
are no more. GitHub's default issue types have no Epic, so most boards mark
epics another way, such as by label.

The parent's issue fields, such as its labels, are on the parent issue. Its
project fields, such as a Work Type, are on the parent's item in the profile's
project. A parent that is not in the project has no project field values; tell
the user so rather than reading another project's item.

## Attachments

An issue has no attachment objects. A card's attachments are the files linked
from its body and comments that were uploaded to GitHub (links under
`github.com/user-attachments/`) or committed to its repository; their names are
the links' file names.

GitHub has no API for uploading a file to an issue; files dragged into an issue
in the browser are uploaded by the web interface only. Which route a project
uses for attachments, such as committing the file to the repository and linking
it from a comment, is the project's decision, like every other part of how it
reaches GitHub. If the project's stated access method offers no route, say so to
the user and ask them to attach the file in the browser rather than improvising
one.

## Verify every write by reading it back

After any write, read the issue or project item back and confirm the field,
comment or column is what was intended — never trust the write's own response.
An issue has no revision number; compare the content itself.
