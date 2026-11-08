# Cards in Azure DevOps

How the card standard maps onto an Azure DevOps work item, how to read a board
when writing its profile, and the behaviours of Azure DevOps that silently break
a card if they are missed. The standard itself is tracker-neutral; this file is
the Azure DevOps binding, named `azure-devops` in the board section of a project
profile, `.devfactory/profile.md`.

How an agent reaches Azure DevOps — the Azure CLI (`az boards`, `az rest`), the
Azure DevOps MCP server, or something else — is the team's choice, not this
file's. The profile's board section records it, and the agent follows it.

## Tracker entries in the profile's board section

| Entry | What it holds |
|---|---|
| Organization | The Azure DevOps organization |
| Project | The project the cards are in |
| Team | The team whose board the profile is for |
| Board | That team's board, for example Stories |
| Board column field | The board's column field, `WEF_<id>_Kanban.Column` |
| Work item type | The type cards are created as, for example User Story |
| Area path | The area path new cards are created under |
| Access | How the agent reaches Azure DevOps, in the team's words |

## Where each part of the card lives

The profile's board section says which field each part of the card is written to. The
defaults are `System.Title` for the title and `System.Description` for every
other part. The fields a part is commonly moved to are
`Microsoft.VSTS.Common.AcceptanceCriteria` for the acceptance criteria and any
rich-text custom field the team keeps for the summary.

| Card feature | Work item feature |
|---|---|
| Comments | The work item's comments (Discussion) |
| Attachments | Attachments uploaded to the project, linked to the work item with an `AttachedFile` relation |

## Reading a board

What `configure-project` reads, over REST at `https://dev.azure.com/{organization}`
with `api-version=7.1`:

- **Teams:** `GET _apis/projects/{project}/teams`.
- **A team's boards:** `GET {project}/{team}/_apis/work/boards`.
- **A board's columns and column field:** `GET
  {project}/{team}/_apis/work/boards/{board id}`. The response lists the board's
  `columns`, each with the states it maps to, and names its column field in
  `fields.columnField.referenceName`.
- **The work item type's fields:** `GET
  {project}/_apis/wit/workitemtypes/{type}/fields?$expand=all`, which gives each
  field's `alwaysRequired` flag, `defaultValue` and `allowedValues`.
- **A field's data type:** `GET _apis/wit/fields/{reference name}`. Rich text,
  with headings and lists, needs a field of type `html`; a `string` field holds
  plain text of up to 255 characters.

Many system fields are required but set by Azure DevOps itself, such as
`System.AreaId`, `System.IterationId` and `System.State`. Only a required field
with no default is one the team must fill.

## A card's column is per team board

A work item sits in a column of each team board that shows it, and those
columns can differ. Read a card's column from the profile's board column field,
never from `System.State` (several columns can share a state) or from
`System.BoardColumn` (which does not say whose board it describes).

## Rich-text format is per field, per work item

Each multiline field stores either **Markdown** or **HTML**, and the format can
differ between fields on the same work item and between work items on the same
board. It is reported in the `multilineFieldsFormat` object of a work item
response.

- **Read the format before writing a field,** and write content in that format's
  own syntax: `**bold**`, backticks, `##` headings and `[text](url)` links for
  Markdown; `<p>`, `<ul><li>`, `<b>`, `<code>` and entities such as `&amp;` for
  HTML. Markdown written into an HTML field, or tags written into a Markdown
  field, show up as literal punctuation.
- **The format is upgrade-only.** An HTML field can be switched to Markdown; a
  Markdown field cannot be switched back to HTML.
- **Set the format in the same request that sets the content.** Over REST, add a
  sibling patch operation, `{"op": "add", "path":
  "/multilineFieldsFormat/<FieldName>", "value": "Markdown"}`, alongside the
  field's own operation, one per field.
- **A format change only rides on a real content change.** Azure DevOps skips an
  update whose value is unchanged, so re-sending the same text with a new format
  succeeds, leaves the revision where it was, and changes nothing.

## Comments

- **Over REST, the comment format is a query parameter:**
  `POST .../wit/workItems/{id}/comments?api-version=7.1-preview.4&format=markdown`.
  A `format` property in the JSON body is silently ignored and the comment is
  stored as HTML. An existing comment can be repaired by `PATCH`-ing the same
  comment id with the query parameter.
- **Send the request body as UTF-8 bytes** with `Content-Type: application/json;
  charset=utf-8`. In Windows PowerShell 5.1, a JSON string passed directly to
  `Invoke-RestMethod` fails with `TF400898 ... JsonReaderException` as soon as it
  contains a non-ASCII character such as an em dash.
- **Through the MCP server's comment tool,** HTML is stored verbatim: pass real
  tags (`<b>`, `<br>`), never pre-escaped entities (`&lt;b&gt;`), which land on
  the card as literal text.

## A card's parent

A card's parent, such as its epic, is the work item its
`System.LinkTypes.Hierarchy-Reverse` relation points at. Read the card with
`$expand=relations` to find it, then read the parent itself for its fields.
A card's epic is the nearest ancestor of type Epic: follow parents upward until
one is an Epic, or there are no more.

## Attachments

An attachment is added in two steps: upload the file's bytes to
`.../_apis/wit/attachments?fileName=<name>&api-version=7.1`, then `PATCH` the
work item to add a relation `{"rel": "AttachedFile", "url": "<url the upload
returned>"}`.

The upload must carry the file's raw bytes (`Content-Type:
application/octet-stream`). Two routes that look as if they should work do not:

- `az rest --body @file` reads the file as text and re-encodes it, corrupting any
  binary file; base64-encoding it first only stores the base64 text.
- The Azure DevOps MCP server's attachment tool could download attachments but
  not upload them, as of October 2026.

Which client uploads the bytes is the project's decision, like every other part
of how it reaches Azure DevOps. If the project's stated access method offers no
working upload route, say so to the user rather than improvising one.

## Verify every write by reading it back

Azure DevOps reports success for several writes that change nothing. After any
write, read the work item back and confirm the field, format, comment or
attachment is what was intended — never trust the write's own response. For a
field update, the work item's revision also increases.

- **Tags** (`System.Tags`) through the MCP server's `wit_work_item_write` need
  `op: "Replace"`; its default `"Add"` returns success and changes nothing.
- **An attachment** is verified by downloading it and comparing it byte for byte
  with the original.
