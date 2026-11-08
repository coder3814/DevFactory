import os
import unittest

from .helpers import run, spec_text, temp_dir, write

DISPOSITIONS_HEAD = '| Concern | Disposition | Demands (criterion or evidence row) |\n|---|---|---|\n'


def codes(r):
    return [l.split(' ')[0] for l in r.lines]


def blank_stamp(status, version='1'):
    return [
        ['Card', '#12'],
        ['Version', version],
        ['Status', status],
        ['Card revision', ''],
        ['Repo commit', ''],
        ['Stamped', ''],
        ['Request type(s)', 'feature'],
    ]


def header(status='Ready', revision='a' * 64, commit='abc1234', stamped='2026-11-07', types='feature'):
    return [
        ['Card', '#12'],
        ['Version', '1'],
        ['Status', status],
        ['Card revision', revision],
        ['Repo commit', commit],
        ['Stamped', stamped],
        ['Request type(s)', types],
    ]


class SpecLintTest(unittest.TestCase):
    def lint(self, spec, criteria='C1\nC2\n', gaps=None):
        d = temp_dir(self)
        write(os.path.join(d, 'spec', 'spec.md'), spec)
        if gaps is not None:
            write(os.path.join(d, 'spec', 'gaps.md'), gaps)
        args = ['spec-lint', os.path.join(d, 'spec')]
        if criteria is not None:
            write(os.path.join(d, 'criteria.txt'), criteria)
            args += ['--criteria', os.path.join(d, 'criteria.txt')]
        return run(args, d)

    def test_a_complete_spec_passes_with_crlf_line_endings_too(self):
        r = self.lint(spec_text().replace('\n', '\r\n'),
                      gaps='## 2026-11-07 — Development\r\n\r\n- **Question or refusal:** Which format?\r\n- **Let through by:** Ready 3.2\r\n- **Resolved by:** 2\r\n')
        self.assertEqual(r.code, 0, r.stdout + r.stderr)
        self.assertEqual(r.lines, [])

    def test_optional_sections_may_be_left_out(self):
        r = self.lint(spec_text(omit=['Owner steps']))
        self.assertEqual(r.code, 0, r.stdout)

    def test_a_missing_header_row_is_reported(self):
        h = [
            ['Card', '#12'],
            ['Version', '1'],
            ['Status', 'Ready'],
            ['Card revision', 'a' * 64],
            ['Repo commit', 'abc1234'],
            ['Request type(s)', 'feature'],
        ]
        r = self.lint(spec_text(header=h))
        self.assertEqual(r.code, 1)
        self.assertEqual(r.lines, ['header-missing Stamped'])

    def test_a_status_outside_drafting_ready_and_approved_is_reported(self):
        r = self.lint(spec_text(status='done'))
        self.assertEqual(r.code, 1)
        self.assertEqual(codes(r), ['status-invalid'])

    def test_a_missing_required_section_is_reported(self):
        r = self.lint(spec_text(omit=['Boundaries']))
        self.assertEqual(r.code, 1)
        self.assertEqual(r.lines, ['section-missing Boundaries'])

    def test_a_section_out_of_order_is_reported(self):
        order = ['Decisions delegated to the developer', 'Dispositions', 'Boundaries', 'Interface surface', 'Evidence plan',
                 'Owner steps', 'Project bindings used', 'Amendments']
        r = self.lint(spec_text(order=order))
        self.assertEqual(r.code, 1)
        self.assertEqual(codes(r), ['section-order'])

    def test_a_blank_disposition_cell_or_one_holding_only_the_italic_prompt_is_reported_by_its_concern(self):
        dispositions = (DISPOSITIONS_HEAD +
                        '| Existing data changed | Not applicable, because nothing is stored | |\n| Security |  | |\n'
                        '| Performance | *say what load it adds* | |\n| Release sequencing | *does the change need anything before or after the deploy* | |\n'
                        '| Owner steps | None, because *nothing* is asked | |')
        r = self.lint(spec_text(dispositions=dispositions))
        self.assertEqual(r.code, 1)
        self.assertEqual(r.lines, ['disposition-blank Security', 'disposition-blank Performance', 'disposition-blank Release sequencing'])

    def test_a_core_concern_with_no_dispositions_row_is_reported(self):
        dispositions = (DISPOSITIONS_HEAD +
                        '| Existing data changed | Not applicable, because nothing is stored | |\n| Performance | Not applicable, because the list is small | |\n'
                        '| Release sequencing | Nothing before or after the deploy | |\n| Owner steps | None | |\n| Accessibility | Not applicable | |')
        r = self.lint(spec_text(dispositions=dispositions))
        self.assertEqual(r.code, 1)
        self.assertEqual(r.lines, ['disposition-missing Security has no row'])

    def test_a_drafting_spec_with_blank_card_revision_repo_commit_and_stamped_passes(self):
        r = self.lint(spec_text(header=blank_stamp('drafting')))
        self.assertEqual(r.code, 0, r.stdout)
        self.assertEqual(r.lines, [])

    def test_an_empty_header_value_is_reported_a_drafting_spec_is_excused_only_the_stamp_rows(self):
        drafting = self.lint(spec_text(header=blank_stamp('drafting', '')))
        self.assertEqual(drafting.code, 1)
        self.assertEqual(drafting.lines, ['header-empty Version'])
        for status in ['Ready', 'approved']:
            r = self.lint(spec_text(header=blank_stamp(status)))
            self.assertEqual(r.code, 1)
            self.assertEqual(r.lines, ['header-empty Card revision', 'header-empty Repo commit', 'header-empty Stamped'])

    def test_request_types_are_each_one_of_the_five(self):
        self.assertEqual(self.lint(spec_text(header=header(types='bug fix, data correction'))).code, 0)
        self.assertEqual(self.lint(spec_text(header=header(types='Refactor / other'))).code, 0)
        r = self.lint(spec_text(header=header(types='feature, chore')))
        self.assertEqual(r.code, 1)
        self.assertEqual(codes(r), ['request-type-invalid'])
        self.assertRegex(r.lines[0], r'"chore"')

    def test_a_ready_or_approved_spec_needs_a_full_card_revision_a_hex_repo_commit_and_a_stamp_date(self):
        for status in ['Ready', 'approved']:
            r = self.lint(spec_text(header=header(status=status, revision='A' * 64, commit='abc12', stamped='today')))
            self.assertEqual(r.code, 1)
            self.assertEqual(codes(r), ['card-revision-invalid', 'repo-commit-invalid', 'stamped-invalid'])
        long = self.lint(spec_text(header=header(commit='f' * 40)))
        self.assertEqual(long.code, 0, long.stdout)
        too_long = self.lint(spec_text(header=header(commit='f' * 41)))
        self.assertEqual(codes(too_long), ['repo-commit-invalid'])
        drafting = self.lint(spec_text(header=header(status='drafting', revision='pending', commit='pending')))
        self.assertEqual(drafting.code, 0, drafting.stdout)

    def test_an_evidence_plan_missing_one_of_the_six_columns_is_reported(self):
        evidence = ('| Criterion | Shown by | What it will show | Generated by | Checkpoint |\n|---|---|---|---|---|\n'
                    '| C1 | test | the list | npm test | Local |\n| C2 | log | the count | npm run job | Local |')
        r = self.lint(spec_text(evidence=evidence))
        self.assertEqual(r.code, 1)
        self.assertEqual(r.lines, ['evidence-column-missing Under what condition'])

    def test_a_criterion_without_an_evidence_row_is_reported(self):
        r = self.lint(spec_text(), criteria='C1\nC2\nC4\n')
        self.assertEqual(r.code, 1)
        self.assertEqual(codes(r), ['evidence-missing'])
        self.assertRegex(r.lines[0], r'C4')

    def test_an_evidence_row_for_an_unknown_criterion_id_is_reported(self):
        r = self.lint(spec_text(), criteria='C1\n')
        self.assertEqual(r.code, 1)
        self.assertEqual(codes(r), ['evidence-unknown'])
        self.assertRegex(r.lines[0], r'C2')

    def test_an_owner_step_without_a_moment_is_reported(self):
        owner = '| Step | Who | Moment in the run |\n|---|---|---|\n| Approve the wording | the requester | |'
        r = self.lint(spec_text(owner=owner))
        self.assertEqual(r.code, 1)
        self.assertEqual(r.lines, ['owner-step-no-moment Approve the wording'])

    def test_an_empty_amendments_table_is_reported(self):
        amendments = '| Version | Date | What changed | Driven by |\n|---|---|---|---|'
        r = self.lint(spec_text(amendments=amendments))
        self.assertEqual(r.code, 1)
        self.assertEqual(codes(r), ['amendments-empty'])

    def test_a_gaps_md_that_does_not_parse_is_reported(self):
        r = self.lint(spec_text(), gaps='## 2026-11-07 — Development\n\n- **Question or refusal:** Which format?\n')
        self.assertEqual(r.code, 1)
        self.assertTrue(all(c == 'gaps-parse' for c in codes(r)), r.stdout)


if __name__ == '__main__':
    unittest.main()
