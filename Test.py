from Crypto import *

file_size = 0
crumbs = []
with open("risk.bmp", "rb") as dat_file:
    dat_file.seek(0, 2)
    file_size = dat_file.tell()
    dat_file.seek(0)
    for x in range(file_size):
        for crumb in decompose_byte(dat_file.read(1)[0]):
            crumbs.append(crumb)

print(f"{file_size}")
for crumb in crumbs:
    print(f"{bin(crumb)}")
