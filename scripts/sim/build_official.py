#!/usr/bin/env python3
"""Converte a imagem oficial fixada por SHA-256; não remonta nem modifica as palavras."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.request import urlopen

from isa import CATEGORIES, identify

ROOT = Path(__file__).resolve().parents[2]
ROM_WORDS = 512
LINE = re.compile(r"32'h([0-9a-fA-F]{8}):\s*r_Instruction\s*=\s*32'h([0-9a-fA-F]{8});")


def parse_image(text, base, capacity=ROM_WORDS):
    # Rejeita lacunas, duplicatas, palavras desalinhadas e imagens fora da ROM.
    words = []
    for line in text.splitlines():
        if not line.strip():
            continue
        match = LINE.fullmatch(line.strip())
        if not match:
            raise ValueError(f'Linha de imagem inválida: {line}')
        address, word = (int(value, 16) for value in match.groups())
        if address != base + 4 * len(words) or len(words) >= capacity:
            raise ValueError(f'Endereço inesperado/fora da ROM: {address:08x}')
        words.append(word)
    if not words:
        raise ValueError('Imagem oficial vazia')
    return words


def main():
    # Entrada: cache verificado, cópia local ou download explícito; saída: ROM e metadados.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='baixa a revisão fixada e renova o cache')
    parser.add_argument('--source', type=Path, help='importa uma cópia local do firmware.txt original')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'firmware/official/source.json').read_text())
    source = manifest['files']['firmware.txt']
    cache = ROOT / 'external/championchip-firmware' / manifest['commit'] / 'firmware.txt'
    if args.source:
        data = args.source.read_bytes()
    elif args.fetch:
        url = f'https://raw.githubusercontent.com/championchip-experience-community/CCX_Brasil_Edition_Firmware_Stage_2/{manifest["commit"]}/firmware.txt'
        with urlopen(url, timeout=30) as response:
            data = response.read()
    elif cache.is_file():
        data = cache.read_bytes()
    else:
        raise ValueError('Imagem oficial ausente: execute make official-fetch ou use --source firmware.txt.')
    digest = hashlib.sha256(data).hexdigest()
    # Só atualiza cache/build depois de conferir o conteúdo da revisão fixada.
    if digest != source['sha256']:
        raise ValueError('SHA-256 do firmware oficial diverge da revisão fixada; não gerar ROM.')
    base = int(manifest['imem']['base'], 16)
    words = parse_image(data.decode('utf-8'), base)
    if len(words) != manifest['imem']['words']:
        raise ValueError('Quantidade de palavras diverge do manifesto oficial')
    # Código e constantes são preservados; somente o código recebe tags de cobertura.
    count = manifest['imem']['code_words']
    names = [identify(word) for word in words[:count]]
    enabled = sorted(set(names))
    # A imagem publicada testa 44 tipos; habilitar sistema no RTL não altera a ROM oficial.
    profile = set(json.loads((ROOT / 'docs/isa/enabled.json').read_text()))
    expected = profile - set(CATEGORIES['Sistema/Sincronização'])
    if set(names) != expected or len(enabled) != manifest['static_instruction_inventory']['unique_confirmed_instructions']:
        raise ValueError('Inventário da imagem diverge da revisão oficial fixada')
    success = int(manifest['termination']['success_write_pc'], 16)
    failure = int(manifest['termination']['failure_write_pc'], 16)
    for pc, expected in ((success, 0x00000213), (failure, 0xfff00213),
                         (success + 4, 0x0000006f), (failure + 4, 0x0000006f)):
        if words[(pc - base) // 4] != expected:
            raise ValueError('Protocolo de término não corresponde à imagem fixada')
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(data)
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    image = words + [0x00000013] * (ROM_WORDS - len(words))
    # As palavras já vêm na ordem da IMEM; não aplicar troca de bytes ao texto oficial.
    (build / 'official.hex').write_text(''.join(f'{word:08x}\n' for word in image))
    tags = [enabled.index(name) + 1 for name in names] + [0] * (ROM_WORDS - count)
    # Tag zero identifica constantes/padding, que não contam como instrução exercitada.
    (build / 'official_tags.hex').write_text(''.join(f'{tag:02x}\n' for tag in tags))
    crc_count = sum(name.startswith('CRC') for name in names)
    # Ordem lida por tb_official_firmware: PCs sucesso/loop/falha, código, tipos e CRCs.
    meta = [success, success + 4, failure, count, len(enabled), crc_count]
    (build / 'official_meta.hex').write_text(''.join(f'{word:08x}\n' for word in meta))
    # READY comprova a conversão; só a execução do testbench pode registrar PASS.
    result = {'status': 'READY', 'scope': 'image conversion; not firmware simulation',
              'commit': manifest['commit'], 'source_sha256': digest, 'base': base,
              'words': len(words), 'rom_words': ROM_WORDS, 'instruction_order': enabled,
              'static_counts': dict(Counter(names)),
              'image_sha256': hashlib.sha256((build / 'official.hex').read_bytes()).hexdigest()}
    (build / 'official_image.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'READY official image: {len(words)}/{ROM_WORDS} words, {len(enabled)} instruction types, commit {manifest["commit"][:8]}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
