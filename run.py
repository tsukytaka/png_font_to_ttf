import subprocess
import os
import time
folder = "etlcdb_fonts_png/"
for i in range(160):
    subprocess.run(["python3", "etlcdb_png_font_to_ttf.py", folder, str(i)])