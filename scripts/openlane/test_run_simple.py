#!/usr/bin/env python3
"""Verifica as barreiras de entrada do fluxo, sem iniciar Docker ou ferramentas EDA."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import run_simple as flow


class FlowInputs(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.object(flow, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        for name, text in {'rtl/simple_system.sv': 'module simple_system; endmodule\n',
                           'build/simple.hex': '00000013\n',
                           'openlane/simple_system/constraints.sdc': '# constraints\n'}.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        (self.root / flow.CONFIG).write_text(json.dumps({
            'VERILOG_FILES': ['dir::rtl/simple_system.sv'],
            'PNR_SDC_FILE': 'dir::openlane/simple_system/constraints.sdc',
            'SIGNOFF_SDC_FILE': 'dir::openlane/simple_system/constraints.sdc'}))
        self.proof = self.root / 'results/logs/simple_synth.json'
        self.proof.parent.mkdir(parents=True)
        self.proof.write_text(json.dumps({
            'status': 'PASS', 'netlist_simulation': 'PASS',
            'sha256': {name: flow.sha256(self.root / name) for name in
                       ('rtl/simple_system.sv', 'build/simple.hex')}}))

    def test_missing_proof_is_rejected(self):
        self.proof.unlink()
        with self.assertRaisesRegex(RuntimeError, 'make simple-synth'):
            flow.prepare()

    def test_changed_rom_or_rtl_is_rejected(self):
        for name in ('build/simple.hex', 'rtl/simple_system.sv'):
            with self.subTest(name=name):
                path = self.root / name
                old = path.read_bytes()
                path.write_bytes(old + b'\n')
                with self.assertRaisesRegex(RuntimeError, 'desatualizada'):
                    flow.prepare()
                path.write_bytes(old)

    def test_incomplete_proof_is_rejected(self):
        proof = json.loads(self.proof.read_text())
        proof['sha256'].pop('build/simple.hex')
        self.proof.write_text(json.dumps(proof))
        with self.assertRaisesRegex(RuntimeError, 'incompleto'):
            flow.prepare()

    def test_snapshot_does_not_follow_later_edits(self):
        work, container, hashes = flow.prepare()
        source = self.root / 'build/simple.hex'
        original = source.read_bytes()
        source.write_text('ffffffff\n')
        self.assertEqual((work / 'design/build/simple.hex').read_bytes(), original)
        self.assertEqual(flow.sha256(work / 'design/build/simple.hex'), hashes['build/simple.hex'])
        config = json.loads((work / 'design' / flow.CONFIG).read_text())
        self.assertEqual(config['SYNTH_PARAMETERS'], [f'ROM_FILE="{container / "build/simple.hex"}"'])

    def test_failed_preflight_invalidates_old_pass(self):
        self.proof.unlink()
        report = self.root / 'results/logs/simple_openlane.json'
        report.write_text('{"status": "PASS"}\n')
        with patch('sys.argv', ['run_simple.py', '--stage', 'synth']):
            with self.assertRaises(RuntimeError):
                flow.main()
        self.assertEqual(json.loads(report.read_text())['status'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
