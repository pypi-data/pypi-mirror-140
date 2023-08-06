from constants import RESPONSE_CODES as RC

from camera import Camera


if __name__ == '__main__':
    import time
    count = 0
    c = Camera()
    c.set_shutter_speed('1/8000')
    c.set_iso(200)
    c.set_aperture(5)
    for i in range(150):
        c.snap()
        r = c.read()
        if RC[r.code[0]] == 'OK':
            count += 1
            print("Next")
            time.sleep(0.33)
        else:
            code = RC[r.code[0]]
            while code != "OK":
                print(f"Retrying: {RC[r.code[0]]}")
                c.snap()
                r = c.read()
                code = RC[r.code[0]]
                time.sleep(1)
            print("Retry success, next")
            count += 1

    print(f"Total photos: {count}")
