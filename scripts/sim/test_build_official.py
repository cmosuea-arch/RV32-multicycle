#!/usr/bin/env python3
"""Testa integridade/endereço da imagem sem rede, compilador ou síntese."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build_official as build


class OfficialImage(unittest.TestCase):
    def test_words_are_not_byte_swapped(self):
        text="32'h00400000: r_Instruction = 32'h12345678;\n32'h00400004: r_Instruction = 32'h90ABCDEF;\n"
        self.assertEqual(build.parse_image(text, 0x400000), [0x12345678, 0x90abcdef])

    def test_rejects_gaps_duplicates_alignment_and_overflow(self):
        first="32'h00400000: r_Instruction = 32'h00000013;\n"
        for address, capacity in ((0x400000, 512), (0x400008, 512),
                                  (0x400006, 512), (0x400004, 1)):
            with self.subTest(address=hex(address), capacity=capacity):
                text=first+f"32'h{address:08x}: r_Instruction = 32'h00000013;\n"
                with self.assertRaises(ValueError):
                    build.parse_image(text, 0x400000, capacity)

    def test_rejects_empty_or_malformed_image(self):
        for text in ('', 'not an image', "32'h00400000: r_Instruction = 32'h123;"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                build.parse_image(text, 0x400000)

    def test_crc_and_exact_system_inventory(self):
        for word, name in ((0x80000033, 'CRCB'), (0x80001033, 'CRCH'), (0x80002033, 'CRCW'),
                           (0x00000073, 'ECALL'), (0x00100073, 'EBREAK'), (0x0ff0000f, 'FENCE')):
            self.assertEqual(build.identify(word), name)
        for word in (0x00200073, 0x00108073, 0x000000f3, 0x0000100f):
            with self.subTest(word=hex(word)), self.assertRaises(ValueError):
                build.identify(word)

    def test_untrusted_source_does_not_create_rom_or_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            folder=root/'firmware/official'
            folder.mkdir(parents=True)
            (folder/'source.json').write_text(json.dumps({
                'commit':'pinned', 'files':{'firmware.txt':{
                    'sha256':hashlib.sha256(b'original').hexdigest()}}}))
            source=root/'tampered.txt'
            source.write_text('modified')
            with patch.object(build,'ROOT',root), patch('sys.argv',['build_official.py','--source',str(source)]):
                with self.assertRaisesRegex(ValueError,'SHA-256'):
                    build.main()
            self.assertFalse((root/'build/official.hex').exists())
            self.assertFalse((root/'external').exists())


if __name__=='__main__':
    unittest.main()
