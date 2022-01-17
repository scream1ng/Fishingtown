# Fishingtown

This is an assistance program to help capturing fish. There is no full automation or 24/7 function.

Script has been testted on Google Chrome with bookmarks tab. It works on both 2560x1440 and 1920x1080 res.

# How to use

Play as normal. 

when fishing gauge come up, just leave the script do the work.

# How it works

Using opencv to convert pic to HSV to find contour and matchTemplate to find fish icon.

Then calculate both variable and pass on pydirectinput to control the green bar.
