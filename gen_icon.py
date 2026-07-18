import struct
from pathlib import Path

width = height = 32
bg = (17, 24, 39)
accent = (31, 111, 237)
white = (255, 255, 255)

pixels = []
for y in range(height):
    row = []
    for x in range(width):
        if x in (0, width - 1) or y in (0, height - 1):
            row.append(accent)
        else:
            row.append(bg)
    pixels.append(row)

for y in range(6, 26):
    for x in range(6, 26):
        if y in range(8, 25) and x in range(8, 24):
            pixels[y][x] = white
        if x in range(7, 18) and y in range(13, 24):
            pixels[y][x] = white

xor_bytes = bytearray()
mask_bytes = bytearray()
for y in range(height):
    for x in range(width):
        r, g, b = pixels[y][x]
        xor_bytes.extend((b, g, r, 0))

# AND mask (1 bit per pixel)
for y in range(height):
    row_bits = 0
    for x in range(width):
        bit = 1 if (x < 1 or y < 1 or x >= width - 1 or y >= height - 1) else 0
        if bit:
            row_bits |= 1 << (7 - (x % 8))
        if x % 8 == 7:
            mask_bytes.append(row_bits)
            row_bits = 0
    if width % 8 != 0:
        mask_bytes.append(row_bits)

# pad to 4-byte alignment for BMP row data
row_len = width * 4
pad = (4 - (row_len % 4)) % 4
xor_data = bytearray()
for y in range(height):
    row = xor_bytes[y * row_len:(y + 1) * row_len]
    xor_data.extend(row)
    xor_data.extend(b'\x00' * pad)

# BITMAPINFOHEADER + XOR + AND
bmp_info = bytearray()
bmp_info.extend(struct.pack('<I', 40))
bmp_info.extend(struct.pack('<i', width))
bmp_info.extend(struct.pack('<i', height * 2))
bmp_info.extend(struct.pack('<H', 1))
bmp_info.extend(struct.pack('<H', 32))
bmp_info.extend(struct.pack('<I', 0))
bmp_info.extend(struct.pack('<I', len(xor_data) + len(mask_bytes)))
bmp_info.extend(struct.pack('<i', 2835))
bmp_info.extend(struct.pack('<i', 2835))
bmp_info.extend(struct.pack('<I', 0))
bmp_info.extend(struct.pack('<I', 0))

ico = bytearray()
ico.extend(struct.pack('<BBH', 0, 0, 1))
ico.extend(struct.pack('<B', width))
ico.extend(struct.pack('<B', height))
ico.extend(struct.pack('<B', 0))
ico.extend(struct.pack('<B', 0))
ico.extend(struct.pack('<H', 1))
ico.extend(struct.pack('<H', 32))
ico.extend(struct.pack('<I', len(bmp_info) + len(xor_data) + len(mask_bytes)))
ico.extend(struct.pack('<I', 22))
ico.extend(bmp_info)
ico.extend(xor_data)
ico.extend(mask_bytes)

Path('app_icon.ico').write_bytes(ico)
print('app_icon.ico criado com sucesso')
