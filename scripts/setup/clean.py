#!/usr/bin/env python3
"""Arquiva build/logs/ondas de trabalho para recomeçar a prática sem perder saídas."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]


def inventory(path):
    """Não segue links: registra seu destino e calcula SHA-256 de arquivos comuns."""
    if path.is_symlink():
        return {'type': 'symlink', 'target': str(path.readlink())}
    if path.is_file():
        return {'type': 'file', 'bytes': path.stat().st_size,
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    if path.is_dir():
        return {'type': 'directory', 'children': {
            child.name: inventory(child) for child in sorted(path.iterdir())}}
    raise ValueError(f'Tipo de arquivo não suportado: {path}')


def main():
    # Lista apenas diretórios de saídas conhecidos; fontes e evidências não são alvos.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='lista saídas sem mover arquivos')
    args = parser.parse_args()
    paths = []
    build = ROOT / 'build'
    if build.exists() or build.is_symlink():
        paths.append(build)
    for name in ('results/logs', 'results/waveforms'):
        folder = ROOT / name
        if folder.is_symlink():
            raise ValueError(f'Diretório de saídas não pode ser link: {folder}')
        if folder.exists():
            paths.extend(p for p in sorted(folder.iterdir())
                         if p.name not in ('README.md', '.gitkeep'))
    if not paths:
        print('Workspace já limpo: nenhuma saída para arquivar.')
        return
    for path in paths:
        print(f'Arquivar: {path.relative_to(ROOT)}')
    # --dry-run mostra a seleção e termina antes de criar o arquivo de backup.
    if args.dry_run:
        print('Prévia: nenhum arquivo movido.')
        return
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    archive = ROOT / 'results/archive' / stamp
    archive.mkdir(parents=True, exist_ok=False)
    # O manifesto registra o inventário e distingue backup completo de erro parcial.
    manifest = {'status': 'IN_PROGRESS', 'utc': stamp, 'scope': 'workspace cleanup; no tests run',
                'entries': []}
    meta = archive / 'manifest.json'
    meta.write_text(json.dumps(manifest, indent=2) + '\n')
    try:
        for path in paths:
            relative = path.relative_to(ROOT)
            destination = archive / relative
            expected = inventory(path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(destination))
            # A movimentação mantém os bytes; a conferência detecta cópia incompleta.
            if inventory(destination) != expected:
                raise ValueError(f'Backup divergente: {relative}')
            manifest['entries'].append({'path': str(relative), 'inventory': expected})
            meta.write_text(json.dumps(manifest, indent=2) + '\n')
        manifest['status'] = 'ARCHIVED'
    except Exception as error:
        manifest.update(status='ERROR', error=str(error))
        raise
    finally:
        meta.write_text(json.dumps(manifest, indent=2) + '\n')
        print(f'Backup local: {archive.relative_to(ROOT)}')
    print('PASS limpeza: saídas arquivadas; fontes e evidências publicadas preservadas.')


if __name__ == '__main__':
    main()
