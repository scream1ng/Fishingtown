import cv2 as cv
import os
import numpy as np
import mss
import sys
import pydirectinput
import time
import threading

def read_sample():
    id = 0
    for list in os.listdir('sample'):
        img = cv.imread('sample/scr' + str(id) + '.jpg')
        cv.imshow('img', img)
        print('read: sample/scr' + str(id) + '.jpg')
        id += 1
        cv.waitKey(10)

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

def click(wait=0):
    pydirectinput.mouseDown()
    time.sleep(wait)
    pydirectinput.mouseUp()

def crop(img):
    # working border for 2560 x 1440
    x, y, w, h = 1288, 493, 50, 575
    frame = img[y:y + h, x:x + w]
    # print(f'image: cropped to {w} x {h}')
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

def AI(frame, top, fish, bottom):
    if bottom > fish and fish > top:
        dist_fish_top = fish - top
        dist_fish_bottom = bottom - fish
        fish_percent = int(fish / 575 * 100)
        bar_percent = int((fish - top) / (bottom - top) * 100)
        #if dist_fish_bottom > dist_fish_top:
        if fish_percent > bar_percent:
            print('click')
            cv.putText(frame, "C", (10, fish), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))

            pydirectinput.mouseDown()

            return frame
        else:
            print('not click')
            cv.putText(frame, "NC", (10, fish), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))

            pydirectinput.mouseUp()

            return frame
    elif top > fish:
        print('click')
        cv.putText(frame, "C", (10, fish), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))

        pydirectinput.mouseDown()

        return frame
    else:
        print('not click')
        cv.putText(frame, "NC", (10, fish), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255))

        pydirectinput.mouseUp()

        return frame

if __name__ == "__main__":
    thr = threading.Thread(target=screen_shot)
    thr.start()

    text = "Looking for Fish..."
    print(text)

    while True:
        img = screen_shot()
        frame = crop(img)
        # detect fish
        fish_dir = "img/fish.jpg"
        frame, fish_pos, fish = fish_detect(frame, fish_dir)

        if fish == 1:
            # print(f'{src}: fish found')
            text = "Fish Found!!!"
            print(text)

            # get y pos at top and bottom of green bar
            top_pos, bottom_pos, frame_green = bar_pos(frame)

            # put dot on fish
            frame = cv.circle(frame, (27, top_pos), 5, (255, 0, 0), -1)
            frame = cv.circle(frame, (27, fish_pos), 5, (255, 0, 0), -1)
            frame = cv.circle(frame, (27, bottom_pos), 5, (255, 0, 0), -1)

            frame = AI(frame, top_pos, fish_pos, bottom_pos)
            print('bottom_pos =', bottom_pos)

            #cv.imshow("main", frame)
            #cv.setWindowProperty("main", cv.WND_PROP_TOPMOST, 1)
        else:
            if text != "Looking for Fish...":
                text = "Looking for Fish..."
                print(text)

        # Press q to quit programas
        if cv.waitKey(1) & 0xFF == ord("q"):
            fisher.keep_fishing = False
            cv.destroyAllWindows()
            cv.waitKey(1)
            flag = False
            sys.exit()
