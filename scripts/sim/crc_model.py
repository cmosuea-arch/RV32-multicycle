"""Modelo independente do contrato CRC CMOS provisório; não certifica Xicrc oficial."""
from binascii import crc_hqx


def crc_model(accumulator, data, op):
    # op escolhe quantos bytes baixos consumir; código inválido deve devolver zero.
    size = {0: 1, 1: 2, 2: 4}.get(op)
    if size is None:
        return 0
    # A biblioteca padrão implementa o polinômio 0x1021 sem repetir o RTL.
    return crc_hqx((data & 0xffffffff).to_bytes(4, 'little')[:size], accumulator & 0xffff)


def check_reference():
    # Confere duas respostas conhecidas antes de usar a biblioteca como referência.
    assert crc_hqx(b'123456789', 0xffff) == 0x29b1
    assert crc_hqx(b'123456789', 0) == 0x31c3
