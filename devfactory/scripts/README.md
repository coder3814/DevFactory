# DevFactory scripts

Run as `node <plugin>/devfactory/scripts/devfactory.js <command> ...` (Node standard library only). Exit 0 is success, 1 a failed check with findings on stdout as `<code> <message>`, 2 a usage or environment error on stderr. Tests: `node --test devfactory/scripts/test`.

- `stamp --card <n> [--repo owner/name]` or `stamp --text <file>`: prints the card revision (SHA-256 of title, LF, body without spec lines, LF line endings, no trailing LFs); `--text` takes the first line as title. Exit 0, 2 when `gh` or the file fails.
- `stamp-check --card <n> [--repo owner/name] --spec <dir>` (or `--text <file>` for the card): prints `match` or `changed <old> <new>`, then `ancestor` or `not-ancestor` for the stamped Repo commit against HEAD in cwd. Exit 0 on match and ancestor, 1 otherwise, 2 when the stamp rows, `gh` or `git` fail.
- `spec-lint <dir> [--criteria <file>]`: checks `spec.md`'s header rows, Status, section order, Disposition cells, evidence rows against the criterion IDs (one per line), owner-step Moments, the Amendments table and `gaps.md`. Exit 0 clean, 1 findings, 2 no `spec.md`.
- `criteria-ids --card <n> [--repo owner/name]` or `--text <file>`: prints each criterion ID opening a list item (under "Acceptance criteria" when the card has that heading), then `duplicate <ID>` for any repeated one. Exit 0, 1 on a duplicate.
- `gaps add <dir> --stage <Approval|Development|Done|Acceptance> --question <q> --condition <c> [--resolved <v>]`: appends a dated entry to `<dir>/gaps.md`; Resolved by defaults to `open`. Exit 0, 2 on a bad stage or folder.
- `gaps check <dir>`: reports `gap-open` for each entry resolved by `open` and `gaps-parse` for a malformed file. Exit 0 / 1.
- `gaps ledger <dir> --card <n> --types <t> --ledger <file>`: appends every entry to the ledger under `## <card> (<types>) — <date> — <stage>` and prints `appended <count>`. Exit 0, 1 when `gaps.md` does not parse.
- `evidence-check <dir> --criteria <file>`: checks each `evidence/<ID>/` exists, is non-empty, and every artifact has a one-line `<name>.txt` sidecar with `revision:`, `checkpoint:` and `produced by:`. Exit 0 / 1.
- `begin <skill>` / `end <skill>`: writes or removes `<cwd>/.devfactory/.active/<skill>` holding an ISO timestamp; `begin` prints `active <other> since <time> (<age> ago)` for each other marker. Exit 0.
- `profile [--field <name>] [--section <heading>]`: prints `<cwd>/.devfactory/profile.md`, or the value of the first `- Name: value` line, within the named section when given. Exit 0, 2 when the profile or field is missing.
