def hd(bind_file, payload_file):
    with open(bind_file, 'ab') as f, open(payload_file, 'rb') as e:
        f.write(e.read())
        print(f"{payload_file} is been hided in {bind_file}")

