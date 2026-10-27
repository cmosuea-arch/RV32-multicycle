"""Referência independente Xicrc, conforme firmware oficial edc7d599."""
from binascii import crc_hqx


def crc_model(data, accumulator, op):
    # Mesma ordem do RTL: data=rs1; accumulator=rs2. Ex.: (0x31323334, 0xffff, 2).
    # op escolhe quantos bytes baixos consumir; código inválido deve devolver zero.
    size = {0: 1, 1: 2, 2: 4}.get(op)
    if size is None:
        return 0
    # A biblioteca padrão implementa o polinômio 0x1021 sem repetir o RTL.
    selected = data & ((1 << (size * 8)) - 1)
    return crc_hqx(selected.to_bytes(size, 'big'), accumulator & 0xffff)


def check_reference():
    # Confere duas respostas conhecidas antes de usar a biblioteca como referência.
    assert crc_hqx(b'123456789', 0xffff) == 0x29b1
    assert crc_hqx(b'123456789', 0) == 0x31c3
    # Mensagem e resposta publicadas no firmware da competição.
    assert crc_hqx(bytes.fromhex('1234567890ABCDEF'), 0xffff) == 0x1e82
