import struct, sys, os
src, out, pattern = sys.argv[1], sys.argv[2], sys.argv[3].lower()
with open(src, 'rb') as f:
    data = f.read()
assert data[:4] in (b'BIGF', b'BIG4')
count, = struct.unpack('>I', data[8:12])
pos = 16
for _ in range(count):
    off, size = struct.unpack('>II', data[pos:pos+8]); pos += 8
    end = data.index(b'\0', pos); name = data[pos:end].decode('latin-1'); pos = end + 1
    if pattern in name.lower():
        dst = os.path.join(out, name.replace(chr(92), os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'wb') as o: o.write(data[off:off+size])
        print(name, size)
