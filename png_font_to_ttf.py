from __future__ import print_function
import sys
import fontforge
from PIL import Image
import json

if len(sys.argv) != 6:
    print('usage: %s <output.otf> <input.png> <char-width> <char-height> <input.fnt>' % sys.argv[0], file=sys.stderr)
    sys.exit(1)

output = sys.argv[1]
image = Image.open(sys.argv[2])
width = int(sys.argv[3])
height = int(sys.argv[4])
infoFile = sys.argv[5]

factor = 10 # size factor so that coords are in range [16, 65536]
private_range = 0xe000 # starting codepoint of private copy
background = (0, 0, 0, 255) # background RGB color

font = fontforge.font() 
font.ascent = height * factor
font.descent = 0 * factor
font.encoding = 'UnicodeFull' # required encoding to access private range

#read list char
charInfos = []
with open(infoFile) as f:
    lineIdx = 0
    for line in f:
        lineIdx += 1
    # content = f.readline()
    # print(content)
        if lineIdx > 4 and line.startswith("char "):
            info = line.strip()
            info = info.replace("char ", "")
            info = info.replace('=', '":')
            info = info.replace(' ', ', "')
            info = '{"' + info + '}'
            print(info)
            char_params = json.loads(info)
            print(char_params)
            charInfos.append(char_params)

pixels = image.load()
for j in range(image.height // height):
    for i in range(image.width // width):
        offset = i + j * (image.width // width)

        # generate two copies of char, in 0-256 and in private range
        for codepoint in [offset, private_range + offset]:
            char = font.createChar(codepoint)
            char.width = width * factor
            pen = char.glyphPen()
            print("char: ", char)
            # draw each non-background pixel as a square
            for y in range(height):
                for x in range(width):
                    pixel = pixels[i * width + x, j * height + y]
                    if pixel != background:
                        pen.moveTo((x * factor, (height - y) * factor)) # draw a pixel
                        pen.lineTo(((x + 1) * factor, (height - y) * factor))
                        pen.lineTo(((x + 1) * factor, (height - y - 1) * factor))
                        pen.lineTo((x * factor, (height - y - 1) * factor))
                        pen.closePath()
sys.exit(1)

chars = [48,49,50,51,52,53,54,55,56,57,68]
for j in range(image.height // height):
    for i in range(image.width // width):
        index = i + j * (image.width // width)
        if index > 10: break
        offset = chars[index]
        # generate two copies of char, in 0-256 and in private range
        for codepoint in [offset, private_range + offset]:
            char = font.createChar(codepoint)
            char.width = width * factor
            pen = char.glyphPen()
            
            # draw each non-background pixel as a square
            for y in range(height):
                for x in range(width):
                    pixel = pixels[i * width + x, j * height + y]
                    print("pixel %d,%d value : ", y, x, pixel) 
                    if pixel != background:
                        pen.moveTo((x * factor, (height - y) * factor)) # draw a pixel
                        pen.lineTo(((x + 1) * factor, (height - y) * factor))
                        pen.lineTo(((x + 1) * factor, (height - y - 1) * factor))
                        pen.lineTo((x * factor, (height - y - 1) * factor))
                        pen.closePath()

# export to font 
font.generate(output, flags=('opentype'))
