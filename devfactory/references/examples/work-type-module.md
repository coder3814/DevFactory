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

- **Expansion:** work that takes the product beyond what it covers today.
  Examples: serving a new kind of customer, adding a new product or service,
  supporting a new market or partner.
- **Improvement:** large pieces of work that add significant functionality
  across the product. Examples: a new capability for end users, automating a
  process people now do by hand. Improvement excludes ongoing small to medium
  changes that enhance existing functionality or add minor functionality,
  whether delivered individually or grouped in a smaller project. Those are
  Maintenance.
- **Internal:** work on infrastructure, internal operations and internal
  improvements, whose results end users do not see directly. Examples: setting
  up environments, building test harnesses or development tools, upgrading
  infrastructure.
- **Maintenance:** two kinds of work.
  1. Keeping current operations running while reacting to changes from
     outside: a changed rule or price that must be reflected, a new report, a
     changed document template.
  2. Ongoing small to medium enhancements to existing functionality, or minor
     new functionality, delivered individually or grouped in a smaller project:
     field and validation changes to existing screens, small automations of an
     existing flow.
- **Fixes:** unplanned work to deal with an issue in the live system.
  Examples: fixing a defect users have hit, such as an unexpected error;
  correcting data a mistake left wrong; investigating unexplained behaviour.

### How to choose

1. **The card has an epic with a Work Type:** recommend the epic's Work Type,
   even for a bug fix. Work that is part of a project takes the project's type;
   it is not automatically Maintenance.
2. **Otherwise, decide from the card's main purpose:**

   | If the card is mainly… | Choose |
   |---|---|
   | A new kind of customer, product, service, market or partner | Expansion |
   | A large piece of work that adds significant functionality or automates a manual process | Improvement |
   | Infrastructure, environments, test harnesses or development tools that end users never see | Internal |
   | A changed rule or price, a new report, a template change, or a small to medium enhancement | Maintenance |
   | An unplanned issue in the live system | Fixes |

3. **Borderline:** if it could be Improvement, check its size first: an ongoing
   small to medium enhancement or minor new functionality is Maintenance, not
   Improvement. If it is still unclear, recommend the closer fit and say that
   the requester should confirm it.
