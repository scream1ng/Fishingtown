import cv2 as cv
import numpy as np
import mss
import sys
import pydirectinput
import tkinter as tk
import yaml

f = open('config.yaml', 'r')
conf = yaml.safe_load(f)
f.close()

pydirectinput.PAUSE = conf['delay']

def screen_shot(left=0, top=0, width=2560, height=1440):
    stc = mss.mss()
    scr = stc.grab({
        'left': left,
        'top': top,
        'width': width,
        'height': height
    })

    img = np.array(scr)
    img = cv.cvtColor(img, cv.IMREAD_COLOR)
    return img

def crop(img, width, height):
    # working border for 2560 x 1440
    if width == 2560 and height == 1440:
        x, y, w, h = 1288, 493, 50, 575
        frame = img[y:y + h, x:x + w]
    elif width == 1920 and height == 1080:
        x, y, w, h = 966, 382, 37, 422
        frame = img[y:y + h, x:x + w]
    return frame

def fish_detect(img, templ_dir):
    templ = cv.imread(templ_dir)
    img_gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
    templ_gray = cv.cvtColor(templ, cv.COLOR_RGB2GRAY)
    templ_w, templ_h = templ_gray.shape[::-1]

    result = cv.matchTemplate(img_gray, templ_gray, cv.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv.minMaxLoc(result)

    top_left = max_loc

    centre = int(top_left[1] + templ_h / 2)

    if max_val >= 0.9:
        fish = 1
        return img, centre, fish
    else:
        centre = None
        fish = 0
        return img, centre, fish

def bar_pos(img):
    # convert to HSV
    hsvframe = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    # create green BGR range and delate
    green_mask = cv.inRange(hsvframe, (55, 0, 0), (70, 255, 255))
    green_mask = cv.dilate(green_mask, (5, 5), 5)

    # merge image and mask
    res_green = cv.bitwise_and(frame, frame, mask=green_mask)

    # find contour
    contours = cv.findContours(green_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)[0]

    top = 1000
    bottom = 1

    for contour in contours:
        area = cv.contourArea(contour)

        if area > 200:
            x2, y2, w2, h2 = cv.boundingRect(contour)
            frame_green = cv.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (0, 0, 255), 2)

            if y2 < top:
                top = y2

            if y2 + h2 > bottom:
                bottom = y2 + h2

    return top, bottom, frame_green

def AI(frame=None, top=0, fish=0, bottom=0):
    try:
        if bottom > fish and fish > top:
            fish_percent = int(fish / frame.shape[0] * 100)
            bar_percent = int((fish - top) / (bottom - top) * 100)
            if fish_percent > bar_percent:
                cv.putText(frame, "C", (10, fish), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))
                pydirectinput.mouseDown()
                return frame
            else:
                cv.putText(frame, "NC", (10, fish), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))
                pydirectinput.mouseUp()
                return frame
        elif top > fish:
            cv.putText(frame, "C", (10, fish), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))
            pydirectinput.mouseDown()
            return frame
        else:
            cv.putText(frame, "NC", (10, fish), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))
            pydirectinput.mouseUp()
            return frame
    except:
        print('Found error, re-running...')

if __name__ == "__main__":
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    print('=====> This program only support 2560x1440 and 1920x1080 resolution')
    print('=====> Tested on Google Chrome with bookmarks bar')
    print(f'=====> Your resolution is {screen_width} x {screen_height}\n')

    text = "Looking for Fish..."
    print(text)

    while True:
        try:
            #start_time = time.time()
            img = screen_shot(0, 0, screen_width, screen_height)
            frame = crop(img, screen_width, screen_height)

            # detect fish
            if screen_width == 2560 and screen_height == 1440:
                fish_dir = "img/fish2K.jpg"
            elif screen_width == 1920 and screen_height == 1080:
                fish_dir = "img/fishFHD.jpg"

            frame, fish_pos, fish = fish_detect(frame, fish_dir)

            if fish == 1:
                if text != "Fish Found: Running AI":
                    text = "Fish Found: Running AI"
                    print(text)

                # get y pos at top and bottom of green bar
                top_pos, bottom_pos, frame_green = bar_pos(frame)

                # put dot on fish
                frame = cv.circle(frame, (27, top_pos), 5, (255, 0, 0), -1)
                frame = cv.circle(frame, (27, fish_pos), 5, (255, 0, 0), -1)
                frame = cv.circle(frame, (27, bottom_pos), 5, (255, 0, 0), -1)

                frame = AI(frame, top_pos, fish_pos, bottom_pos)

                #cv.imshow("main", frame)
                #cv.setWindowProperty("main", cv.WND_PROP_TOPMOST, 1)
            else:
                if text != "Looking for Fish...":
                    text = "Looking for Fish..."
                    print(text)
        except:
            print('Found error, re-running...')

        # Press q to quit programas
        if cv.waitKey(1) & 0xFF == ord("q"):
            cv.destroyAllWindows()
            cv.waitKey(1)
            flag = False
            sys.exit()

        #print("FPS: ", 1.0 / (time.time() - start_time))
