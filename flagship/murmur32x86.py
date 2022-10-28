from __future__ import unicode_literals
import sys

def murmurHash(key):
    c1 = -0x3361d2af
    c2 = 0x1b873593
    # if sys.version_info[0] < 3:
    #     key = key.decode('utf-8')
    h1 = 0
    pos = 0
    end = len(key)
    k1 = 0
    # k2 = 0
    shift = 0
    # bits = 0
    nBytes = 0

    while pos < end:
        char = key[pos]
        code = ord(key[pos])
        pos += 1
        if code < 0x80:
            k2 = code
            bits = 8
        elif code < 0x800:
            # k2 = (0xC0  | (code >> 6) | (0x80 | (code & 0x3F) << 8))
            k2 = (0xC0 | (code >> 6) | ((0x80 | (code & 0x3F)) << 8))
            bits = 16
        elif code < 0xD800 or code > 0xDFFF or pos >= end:
            k2 = (0xE0 | (code >> 12) | ((0x80 | (code >> 6 & 0x3F)) << 8) | ((0x80 | (code & 0x3F)) << 16))
            bits = 24
        else:
            utf32 = ord(key[pos])
            pos += 1
            utf32 = (code - 0xD7C0 << 10) + (utf32 & 0x3FF)
            k2 = (0xff & (0xF0 | (utf32 >> 18)) | ((0x80 | (utf32 >> 12 & 0x3F)) << 8) | (
                    (0x80 | (utf32 >> 6 & 0x3F)) << 16) | ((0x80 | (utf32 & 0x3F)) << 24))
            bits = 32
        k1 = k1 | (k2 << shift)
        shift += bits
        if shift >= 32:

            k1 = ((k1 * c1) & 0xFFFFFFFF) - 2 ** 32
            k1 = ((k1 << 15) & 0xFFFFFFFF) | ((k1 & 0xFFFFFFFF) >> 17)
            k1 = ((k1 * c2) & 0xFFFFFFFF) - 2 ** 32
            h1 = h1 ^ k1

            h1 = (((h1 << 13) & 0xFFFFFFFF) - 2 ** 32) | ((h1 & 0xFFFFFFFF) >> 19)
            h1 = (((h1 * 5) & 0xFFFFFFFF) - 2 ** 32) + (-0x19ab949c)
            shift -= 32
            if shift != 0:
                k1 = k2 >> (bits - shift)  # Todo check this condition
            else:
                k1 = 0
            nBytes += 4

    if shift > 0:
        nBytes += (shift >> 3)

        k1 = ((k1 * c1) & 0xFFFFFFFF)
        k1 = (((k1 << 15) & 0xFFFFFFFF) - 2 ** 32) | ((k1 & 0xFFFFFFFF) >> 17)
        k1 = ((k1 * c2) & 0xFFFFFFFF)
        h1 = h1 ^ k1

    h1 = h1 ^ nBytes

    h1 = h1 ^ ((h1 & 0xFFFFFFFF) >> 16)

    h1 = ((h1 * -0x7a143595) & 0xFFFFFFFF) - 2 ** 32
    h1 = (h1 ^ ((h1 & 0xFFFFFFFF) >> 13))
    h1 = ((h1 * -0x3d4d51cb) & 0xFFFFFFFF) - 2 ** 32
    h1 = (h1 ^ ((h1 & 0xFFFFFFFF) >> 16))

    return h1 & 0xFFFFFFFF
