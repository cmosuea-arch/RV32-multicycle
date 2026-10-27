#!/usr/bin/env python3
"""Rejeita cobertura falsa: firmware parcial, hashes antigos e traps aposentados."""
import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import coverage


class CoverageEvidence(unittest.TestCase):
    def setUp(self):
        # Monta evidências mínimas num diretório temporário; não executa CPU ou síntese.
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for folder in ('docs/isa','build','results/logs','rtl'):
            (self.root/folder).mkdir(parents=True)
        self.names={name for group in coverage.CATEGORIES.values() for name in group}
        self.write('docs/isa/enabled.json',sorted(self.names))
        self.counts={name:1 for name in self.names-set(coverage.SYSTEM)}
        self.write('build/isa_counts.json',self.counts)
        (self.root/'rtl/evidence.sv').write_text('verified revision')
        hashes={'rtl/evidence.sv':hashlib.sha256(b'verified revision').hexdigest()}
        self.official={'status':'PASS','instructions':sorted(self.names-{'FENCE','ECALL','EBREAK'}),'sha256':hashes}
        self.system={'status':'PASS','checks':{'FENCE':512,'ECALL':256,'EBREAK':256},
                     'trap_instructions_retired':0,'sha256':hashes}
        self.tests={'tb_decoder','tb_control_unit','tb_core_system','tb_isa','tb_official_firmware'}
        self.root_patch=patch.object(coverage,'ROOT',self.root)
        self.root_patch.start(); self.addCleanup(self.root_patch.stop)

    def write(self,path,value):
        (self.root/path).write_text(json.dumps(value))

    def publish(self):
        # Usa o validador real; omite só a exportação visual para concentrar nas evidências.
        self.write('results/logs/official_firmware.json',self.official)
        self.write('results/logs/system.json',self.system)
        with patch.object(coverage,'render_coverage'):
            coverage.write_coverage(self.tests)

    def test_47_implemented_does_not_claim_47_in_official_firmware(self):
        # 47 PASS funcionais devem coexistir com apenas 44 PASS na coluna de firmware.
        self.publish()
        with (self.root/'docs/isa/coverage.csv').open() as source:
            rows=list(csv.DictReader(source))
        self.assertEqual(len(rows),47)
        self.assertTrue(all(row['Regressão']=='PASS' for row in rows))
        self.assertEqual(sum(row['Firmware oficial']=='PASS' for row in rows),44)
        for row in rows:
            if row['Instrução'] in coverage.SYSTEM:
                self.assertIn('traps precisos',row['Observação'])
                self.assertNotIn('aposentadorias',row['Observação'])
                self.assertEqual(row['Firmware oficial'],'NÃO EXERCITADA')

    def test_missing_current_test_is_not_coverage(self):
        self.tests.remove('tb_core_system')
        with self.assertRaisesRegex(RuntimeError,'missing current'):
            self.publish()

    def test_official_missing_instruction_is_not_masked_by_system(self):
        self.official['instructions'].remove('ADD')
        with self.assertRaisesRegex(RuntimeError,'44-type inventory'):
            self.publish()

    def test_trap_must_be_precise_and_observed(self):
        self.system['checks']['ECALL']=0
        with self.assertRaisesRegex(RuntimeError,'precise system'):
            self.publish()
        self.system['checks']['ECALL']=256
        self.system['trap_instructions_retired']=1
        with self.assertRaisesRegex(RuntimeError,'precise system'):
            self.publish()

    def test_changed_rtl_invalidates_recorded_evidence(self):
        (self.root/'rtl/evidence.sv').write_text('modified revision')
        with self.assertRaisesRegex(RuntimeError,'stale coverage'):
            self.publish()

    def test_trap_cannot_appear_as_retirement(self):
        self.counts['ECALL']=1
        self.write('build/isa_counts.json',self.counts)
        with self.assertRaisesRegex(RuntimeError,'must not be counted'):
            self.publish()

    def test_fence_requires_retirement_trace(self):
        self.counts.pop('FENCE')
        self.write('build/isa_counts.json',self.counts)
        with self.assertRaisesRegex(RuntimeError,'absent from trace'):
            self.publish()


if __name__=='__main__':
    unittest.main()
