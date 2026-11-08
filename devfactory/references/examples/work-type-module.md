# Work Type

A starter team module. `configure-project` copies it into a team's
`.devfactory/modules/` when the team wants its cards to carry a work type;
the team's copy is the team's to change. Drop this note from the copy.

## Holds

Work Type: the one work type that describes the major overall purpose of the
card. A card often contains more than one kind of work; classify it by its main
purpose.

## Rules

- Exactly one value, from the list in "Choosing a value".

## Related data

The card's epic, if it has one, and the epic's Work Type.

## Choosing a value

### The work types

- **Expansion:** business projects that expand beyond our current product or
  customer base. Examples: adding new carriers, expanding service into new
  states, adding new products or services.
- **Improvement:** large business projects that introduce significant
  functionality advancements, with impact at the overall platform level.
  Examples: new functionality for end users, automation of manual processes for
  internal users or teams. Improvement excludes ongoing small to medium changes
  that enhance existing functionality or add minor functionality, whether
  delivered individually or grouped in a smaller project. Those are Maintenance.
- **Internal:** internal projects dealing with infrastructure, internal
  operations and internal improvements, whose results are not directly visible
  to end users. Examples: setting up environments, creating test harnesses or
  development tools, infrastructure upgrades. Infrastructure, Bicep and DevOps
  cards are Internal.
- **Maintenance:** two kinds of work.
  1. Keeping business flowing with current procedures while reacting to
     unexpected changes: plan and rate changes requested by carriers, new report
     requests, changes to document templates, manual processes.
  2. Ongoing small to medium enhancements to existing functionality, or minor
     new functionality, delivered individually or grouped in a smaller project:
     field and validation updates to existing interfaces that add process flow
     efficiencies or address changing needs, and process flow automation
     enhancements.
- **Bugs/Fixes:** unplanned work required to deal with any issue in a
  production environment. Examples: fixing bugs found in production, such as
  unexpected errors being thrown; changes made in production to correct current
  processes; correcting human errors; code spelunking.

### How to choose

1. **The card has an epic with a Work Type:** recommend the epic's Work Type,
   even for a bug fix. Work that is part of a project takes the project's type;
   it is not automatically Maintenance.
2. **Otherwise, decide from the card's main purpose:**

   | If the card is mainly… | Choose |
   |---|---|
   | Adding a carrier, state, product or service | Expansion |
   | A large project that advances platform functionality or automates a manual process | Improvement |
   | Infrastructure, environments, test harnesses or dev tools that end users never see | Internal |
   | Carrier plan or rate changes, new reports, template changes, or small to medium enhancements | Maintenance |
   | An unplanned issue in production | Bugs/Fixes |

3. **Borderline:** if it could be Improvement, check its size first: an ongoing
   small to medium enhancement or minor new functionality is Maintenance, not
   Improvement. If it is still unclear, recommend the closer fit and say to
   confirm with the dev manager.
