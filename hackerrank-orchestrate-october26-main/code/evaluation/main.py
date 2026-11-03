#!/usr/bin/env python3
"""Structural and public-sample evaluation for the local deletion-audit engine."""
from __future__ import annotations
import csv, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'code'))
import main as engine

class AuditTests(unittest.TestCase):
    def test_01_multilingual_deletion_intents(self):
        self.assertTrue(engine.is_deletion_request('Solicito a exclusão permanente da conta associada a este e-mail.'))
        self.assertTrue(engine.is_deletion_request('이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다.'))
        self.assertTrue(engine.is_deletion_request('Je demande la suppression définitive du compte associé à cette adresse e-mail.'))
    def test_02_non_deletion_intent(self):
        self.assertFalse(engine.is_deletion_request('Please correct the email address on my profile.'))
        self.assertFalse(engine.is_deletion_request('Please unsubscribe me from marketing newsletters.'))
    def test_03_output_contract(self):
        req=engine.read_csv(ROOT/'dataset/deletion_requests.csv')
        errs=engine.validate_output(ROOT/'output.csv',req)
        self.assertEqual(errs,[],'; '.join(errs[:10]))
    def test_04_step_order_and_enums(self):
        rows=engine.read_csv(ROOT/'output.csv')
        for row in rows:
            steps=json.loads(row['steps_json'])
            self.assertEqual([s['step_no'] for s in steps],list(range(1,len(steps)+1)))
            keys=[(engine.PHASE_ORDER[s['phase']],engine.OP_ORDER[s['operation']],s['system_id'],s['resource_id']) for s in steps]
            self.assertEqual(keys,sorted(keys))
    def test_05_not_applicable_empty(self):
        row={'case_id':'custom_non_delete','email':'x@example.com','requested_at':'2026-01-01T00:00:00Z','reported_status':'NOT_STARTED','reported_at':'2026-01-01T00:00:00Z','audit_at':'2026-01-02T00:00:00Z','request_text':'Please correct my email address; do not delete my account.'}
        self.assertFalse(engine.is_deletion_request(row['request_text']))
    def test_06_policy_special_treatments(self):
        self.assertEqual(engine.policy_action('ACCOUNT_TOMBSTONE',{}),'REDACT')
        self.assertEqual(engine.policy_action('ANALYTICS_PROFILE',{}),'ANONYMIZE')
        self.assertEqual(engine.policy_action('BACKUP_ARCHIVE',{}),'RETAIN')

def main_eval():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(AuditTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    requests=engine.read_csv(ROOT/'dataset/sample_deletion_requests.csv')
    identities=engine.read_csv(ROOT/'dataset/user_identities.csv')
    audits=engine.read_csv(ROOT/'dataset/user_audit_log.csv')
    activities=engine.read_csv(ROOT/'dataset/system_activity.csv')
    rules=engine.read_csv(ROOT/'dataset/deletion_rules.csv')
    observations,_=engine.build_observations(ROOT/'dataset')
    preds=[engine.case_output(r,observations,identities,audits,activities,rules) for r in requests]
    with (ROOT/'dataset/sample_output.csv').open(encoding='utf-8-sig',newline='') as f: gold={r['case_id']:r for r in csv.DictReader(f)}
    status=sum(p['deletion_status']==gold[p['case_id']]['deletion_status'] for p in preds)
    exact=sum(json.loads(p['steps_json'])==json.loads(gold[p['case_id']]['steps_json']) for p in preds)
    pred_step_keys=[]; gold_step_keys=[]; field_matches=0; field_total=0
    for p in preds:
        ps=json.loads(p['steps_json']); gs=json.loads(gold[p['case_id']]['steps_json'])
        pk={(s['phase'],s['system_id'],s['resource_id'],s['operation'],s['state']) for s in ps}
        gk={(s['phase'],s['system_id'],s['resource_id'],s['operation'],s['state']) for s in gs}
        pred_step_keys.extend(pk); gold_step_keys.extend(gk)
        # Field accuracy on matching (phase, system, resource) anchors.
        pmap={(s['phase'],s['system_id'],s['resource_id']):s for s in ps}
        gmap={(s['phase'],s['system_id'],s['resource_id']):s for s in gs}
        for key in set(pmap)|set(gmap):
            if key in pmap and key in gmap:
                for field in ('operation','state','evidence_id'):
                    field_total+=1; field_matches+=pmap[key].get(field)==gmap[key].get(field)
            else:
                field_total+=3
    matched=len(set(pred_step_keys)&set(gold_step_keys))
    precision=matched/max(1,len(set(pred_step_keys))); recall=matched/max(1,len(set(gold_step_keys)))
    print(f'PUBLIC_SAMPLE_STATUS_ACCURACY={status}/{len(preds)} ({status/len(preds):.1%})')
    print(f'PUBLIC_SAMPLE_EXACT_STEP_ARRAY={exact}/{len(preds)} ({exact/len(preds):.1%})')
    print(f'PUBLIC_SAMPLE_STEP_SET_PRECISION={precision:.1%} ({matched}/{len(set(pred_step_keys))})')
    print(f'PUBLIC_SAMPLE_STEP_SET_RECALL={recall:.1%} ({matched}/{len(set(gold_step_keys))})')
    print(f'PUBLIC_SAMPLE_FIELD_ACCURACY={field_matches}/{field_total} ({field_matches/max(1,field_total):.1%})')
    print('Note: sample metrics are diagnostic; sample requests are not the 518-case evaluation set.')
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__': sys.exit(main_eval())
