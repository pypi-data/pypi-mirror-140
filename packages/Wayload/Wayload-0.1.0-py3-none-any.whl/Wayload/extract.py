def apk(hided_apk_file, new_file_name):
    end_hex = b'\x00\x00\x00'
    with open(hided_apk_file, 'rb') as f:
        content = f.read()
        offset = content.index(end_hex)
        f.seek(offset + len(end_hex))

        with open(new_file_name, 'wb') as e:
            e.write(f.read())
            print(f'File Extracted as {new_file_name}')

def gif(hided_gif_file, new_file_name):
    end_hex = b'\x00\x3b'
    with open(hided_gif_file, 'rb') as f:
        content = f.read()
        offset = content.index(end_hex)
        f.seek(offset + len(end_hex))

        with open(new_file_name, 'wb') as e:
            e.write(f.read())
            print(f'File Extracted as {new_file_name}')

def jpeg(hided_jpeg_file, new_file_name):
    end_hex = b'\xff\xd9'
    with open(hided_jpeg_file, 'rb') as f:
        content = f.read()
        offset = content.index(end_hex)
        f.seek(offset + len(end_hex))

        with open(new_file_name, 'wb') as e:
            e.write(f.read())
            print(f'File Extracted as {new_file_name}')

def png(hided_png_file, new_file_name):
    end_hex = b'\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82'
    with open(hided_png_file, 'rb') as f:
        content = f.read()
        offset = content.index(end_hex)
        f.seek(offset + len(end_hex))

        with open(new_file_name, 'wb') as e:
            e.write(f.read())
            print(f'File Extracted as {new_file_name}')


def jpg(hided_jpg_file, new_file_name):
    end_hex = b'\xff\xd9'
    with open(hided_jpg_file, 'rb') as f:
        content = f.read()
        offset = content.index(end_hex)
        f.seek(offset + len(end_hex))

        with open(new_file_name, 'wb') as e:
            e.write(f.read())
            print(f'File Extracted as {new_file_name}')

