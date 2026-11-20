import unittest
from copy import deepcopy
from r54_original_batch_clock import audit_rows, audit_zip, minimal_order_cost_bounds


def fixture():
    entries=[]
    groups={1:([1,1,1,1,1,0],[0,1,1,1,1,1],[0,1,1,1,1,1]),
            2:([1,1,1,1,0,0],[1,1,1,1,0,0],[1,1,1,1,0,0])}
    for group, periods in groups.items():
        for t,mask in enumerate(periods,1):
            gross=0 if t==1 else sum(x!=y for x,y in zip(periods[t-2],mask))
            for i,route in enumerate(mask,1):
                entries.append({'session':'3','section':'2','trt':'1','Period':str(t),
                                'Group':str(group),'ID':str(100*group+i),
                                'RouteA':str(route),'RouteB':str(1-route),
                                'NumSwitch':str(gross)})
    return entries


class R54BatchClockTests(unittest.TestCase):
    def test_exact_unknown_order_witness(self):
        self.assertEqual(minimal_order_cost_bounds(5,1,1),(3,15))
        self.assertEqual(minimal_order_cost_bounds(4,1,1),(3,3))
        self.assertEqual(minimal_order_cost_bounds(3,0,0),(0,0))
        with self.assertRaises(ValueError):minimal_order_cost_bounds(5,2,0)

    def test_sample_audit_detects_unobserved_microstep_order(self):
        result=audit_rows(fixture())
        self.assertEqual((result['six_actor_group_sections'],result['group_period_transitions']), (2,4))
        self.assertEqual(result['gross_switch_histogram'],{0:3,2:1})
        self.assertEqual(result['unknown_order_changes_hypothetical_microcost'],1)
        self.assertEqual(result['five_to_five_one_each_direction'],1)
        self.assertEqual(result['constant_occupancy_with_churn'],1)
        self.assertEqual(result['hypothetical_microstep_excess_sum_range'],[3,15])
        self.assertEqual(result['recorded_gross_switches'],2)

    def test_source_declared_switch_must_match_actor_difference(self):
        corrupted=fixture()
        target=next(x for x in corrupted if x['Period']=='2' and x['Group']=='1')
        target['NumSwitch']='1'
        with self.assertRaisesRegex(ValueError,'NumSwitch mismatch'):audit_rows(corrupted)

    def test_missing_or_duplicate_actor_fails_closed(self):
        entries=fixture()
        with self.assertRaisesRegex(ValueError,'duplicate actor'):audit_rows(entries+[entries[0]])
        missing=[x for x in entries if not (x['Period']=='2' and x['Group']=='1' and x['ID']=='101')]
        with self.assertRaisesRegex(ValueError,'actor changed identity'):audit_rows(missing)

    def test_raw_blob_seal_and_tiny_fixture_opt_out(self):
        from zipfile import ZipFile
        from tempfile import TemporaryDirectory
        from pathlib import Path
        import csv
        with TemporaryDirectory() as folder:
            path = Path(folder)/"synthetic_source.zip"
            rows = fixture()
            import io
            out = io.StringIO()
            writer = csv.DictWriter(out, fieldnames=rows[0].keys())
            writer.writeheader();writer.writerows(rows)
            with ZipFile(path,'w') as z:
                z.writestr('data_task_all_switch_230705.csv', out.getvalue())
            result = audit_zip(path, require_original=False)
            self.assertEqual(result['group_period_transitions'],4)
            with self.assertRaisesRegex(ValueError,'SHA256 mismatch'):
                audit_zip(path, require_original=True)

    def test_original_population_not_assumed_from_tiny_fixture(self):
        with self.assertRaisesRegex(ValueError,'sealed 24-session'):audit_rows(fixture(),require_original=True)
        sample=fixture()
        excluded=deepcopy(sample[0]);excluded['session']='2'
        self.assertEqual(audit_rows(sample+[excluded])['individual_choices'],len(sample))
        impossible=deepcopy(sample[0]);impossible['RouteA']='1';impossible['RouteB']='1'
        with self.assertRaisesRegex(ValueError,'binary route'):audit_rows([impossible])


if __name__ == '__main__':unittest.main()
