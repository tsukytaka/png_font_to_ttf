from __future__ import print_function
import sys
import fontforge
from PIL import Image
import json
import time
import gc

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: %s <png_fonts_dir> <index>' % sys.argv[0], file=sys.stderr)
        sys.exit(1)
    png_font_dir = sys.argv[1]
    i = int(sys.argv[2])
    output = "etlcdb_fonts_ttf/etlcdb_" + str(i+1) + ".ttf"
    image = Image.open(png_font_dir + str(i+1) + "_0.png")
    infoFile = png_font_dir + "etlcdb_" + str(i+1) + ".fnt"

    factor = 10 # size factor so that coords are in range [16, 65536]
    private_range = 0xe000 # starting codepoint of private copy
    background = (0, 0, 0, 255) # background RGB color

    font = fontforge.font() 
    font.ascent = 127 * factor
    font.descent = 0 * factor
    font.encoding = 'UnicodeFull' # required encoding to access private range

    #read list char
    charInfos = []
    with open(infoFile) as f:
        lineIdx = 0
        for line in f:
            lineIdx += 1
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

    for i in range(len(charInfos)):
        offset = charInfos[i]["id"]
        x_char = charInfos[i]["x"]
        y_char = charInfos[i]["y"]
        width = charInfos[i]["width"]
        height = charInfos[i]["height"]
        for codepoint in [offset, private_range + offset]:
            char = font.createChar(codepoint)
            char.width = width * factor
            print(f"id: {offset}, char: {char}")
            pen = char.glyphPen()
            for y in range(height):
                for x in range(width):
                    pixel = pixels[x_char + x, y_char + y]
                    if pixel != background:
                        pen.moveTo((x * factor, (height - y) * factor)) # draw a pixel
                        pen.lineTo(((x + 1) * factor, (height - y) * factor))
                        pen.lineTo(((x + 1) * factor, (height - y - 1) * factor))
                        pen.lineTo((x * factor, (height - y - 1) * factor))
                        pen.closePath()
    # export to font 
    font.generate(output, flags=('opentype'))
    del font
    gc.collect()
