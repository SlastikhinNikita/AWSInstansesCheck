# -*- coding: utf-8 -*-
from time import sleep
import sys


class TextColor:
    HEADER      = '\033[95m'
    BLUE        = '\033[94m'
    GREEN       = '\033[92m'
    WARNING     = '\033[93m'
    FAIL        = '\033[91m'
    ENDC        = '\033[0m'
    BOLD        = '\033[1m'
    UNDERLINE   = '\033[4m'
    WHITE       = '\033[0m'
    RED         = '\033[31m'
    PURPLE      = '\033[35m'
    CYAN        = '\033[36m'



Mask = TextColor.WARNING + TextColor.BOLD + str('''
   _____  __      __  _________
  /  _  \/  \    /  \/   _____/
 /  /_\  \   \/\/   /\_____  \ 
/    |    \        / /        \\
\____|__  /\__/\  / /_______  /
        \/      \/          \/''') \
+ TextColor.BLUE \
+ str(''' 
 _           _                                               _ _             
(_)_ __  ___| |_ __ _ _ __   ___ ___   _ __ ___   ___  _ __ (_) |_ ___  _ __ 
| | '_ \/ __| __/ _` | '_ \ / __/ _ \ | '_ ` _ \ / _ \| '_ \| | __/ _ \| '__|
| | | | \__ \ || (_| | | | | (_|  __/ | | | | | | (_) | | | | | || (_) | |   
|_|_| |_|___/\__\__,_|_| |_|\___\___| |_| |_| |_|\___/|_| |_|_|\__\___/|_|   
                                                                                                                                  
''') + TextColor.GREEN + \
str('''/ Created by Slastikhin Nikita /

''') + TextColor.WHITE

class MaskTerminal:
    def __init__(self):
        self.Text = Mask

    def ShowMask(self):
        animation = self.Text
        print
        for i in range(len(self.Text)):
            sleep(0.001)
            sys.stdout.write(animation[i % len(animation)])
            sys.stdout.flush()
        print

    def ShowLoading(self):
        animation = "|/-\\"
        for i in range(len(animation)):
            sleep(0.1)
            sys.stdout.write(animation[i % len(animation)])
            sys.stdout.flush()
        print