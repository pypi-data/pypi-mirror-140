#_#_#_#_#_#_#
from gettext import install
import webbrowser
import os
import time
from pip import *

class pip:
    def install(module='Module'):
        print(F'Installing {module}')
        os.system(f'pip install {module}')

class colors:
    pink = '\033[95m'
    blue = '\033[94m'
    cyan = '\033[96m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    end = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'    

class loremipsum:
    loremipsum = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Iaculis at erat pellentesque adipiscing commodo elit at imperdiet dui. At lectus urna duis convallis. Bibendum est ultricies integer quis auctor elit sed vulputate mi. Quam elementum pulvinar etiam non quam lacus. Neque egestas congue quisque egestas diam in. Rutrum quisque non tellus orci. Lobortis mattis aliquam faucibus purus in massa tempor nec. Habitant morbi tristique senectus et netus. Mauris ultrices eros in cursus turpis. Cursus mattis molestie a iaculis at. Natoque penatibus et magnis dis parturient montes. Lobortis scelerisque fermentum dui faucibus in. Tortor dignissim convallis aenean et tortor at risus viverra adipiscing.

Pulvinar neque laoreet suspendisse interdum consectetur libero. Netus et malesuada fames ac turpis egestas integer eget aliquet. Vulputate odio ut enim blandit volutpat maecenas volutpat blandit aliquam. Montes nascetur ridiculus mus mauris vitae ultricies. Amet consectetur adipiscing elit ut aliquam purus sit amet luctus. Egestas diam in arcu cursus euismod quis viverra nibh. Dignissim convallis aenean et tortor at risus. In cursus turpis massa tincidunt dui ut. Id volutpat lacus laoreet non curabitur gravida. Maecenas accumsan lacus vel facilisis volutpat est velit. Convallis posuere morbi leo urna molestie. Diam donec adipiscing tristique risus nec. Quis risus sed vulputate odio ut enim blandit volutpat. At varius vel pharetra vel turpis nunc. Nunc mi ipsum faucibus vitae aliquet nec ullamcorper sit.

Aliquet nibh praesent tristique magna sit amet purus gravida. Enim ut tellus elementum sagittis vitae et leo. Velit ut tortor pretium viverra suspendisse potenti nullam ac tortor. Felis eget nunc lobortis mattis. Urna id volutpat lacus laoreet non curabitur. Sed viverra tellus in hac habitasse platea dictumst vestibulum rhoncus. Dolor magna eget est lorem ipsum dolor. Neque aliquam vestibulum morbi blandit cursus. Pellentesque massa placerat duis ultricies lacus sed. Venenatis a condimentum vitae sapien pellentesque habitant morbi tristique. Sit amet mauris commodo quis imperdiet massa tincidunt nunc pulvinar. Tellus elementum sagittis vitae et leo.

Aliquam faucibus purus in massa. Accumsan in nisl nisi scelerisque eu. Felis bibendum ut tristique et egestas quis ipsum. Morbi tristique senectus et netus et malesuada. Scelerisque in dictum non consectetur a erat nam. Rhoncus mattis rhoncus urna neque. Amet nulla facilisi morbi tempus. Habitant morbi tristique senectus et netus et malesuada. Vitae congue eu consequat ac felis donec et odio. Vitae elementum curabitur vitae nunc sed. Nunc sed blandit libero volutpat sed cras ornare arcu dui. Id nibh tortor id aliquet lectus. Venenatis lectus magna fringilla urna porttitor rhoncus dolor purus non. At quis risus sed vulputate odio. Ullamcorper malesuada proin libero nunc consequat interdum. Est pellentesque elit ullamcorper dignissim cras tincidunt lobortis feugiat vivamus. In hac habitasse platea dictumst quisque sagittis purus sit.

Porttitor rhoncus dolor purus non enim praesent. Phasellus vestibulum lorem sed risus ultricies tristique nulla. Odio ut enim blandit volutpat maecenas volutpat blandit aliquam. Pretium viverra suspendisse potenti nullam ac. Diam maecenas ultricies mi eget mauris pharetra et ultrices. Consequat nisl vel pretium lectus quam. Morbi quis commodo odio aenean sed adipiscing diam donec. Enim sit amet venenatis urna cursus eget nunc scelerisque. Posuere lorem ipsum dolor sit amet consectetur adipiscing elit. Imperdiet sed euismod nisi porta lorem mollis aliquam.    
"""

class license:
    mit = """Copyright <YEAR> <COPYRIGHT HOLDER>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

def mitLicense(year, owner):
    return ( f"""Copyright {year} {owner}

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.""")

def loremIpsum(paragraphs = 5):
    return (loremipsum.loremipsum)

#-#

def webOpen(website="http://google.com"):
    webbrowser.open(website)

def fileOpen(file='cmd.exe'):
    webbrowser.open(file)

def AppOpen(title='Title', app='Cmd.exe', arguments=''):
    os.system(f'START "{app}" "{title} {arguments}"')

#-#

def wait(secs=2):
    time.sleep(secs)

def shell(command='echo Hello World'):
    os.system(command)

#0-#
def end():
    quit()

def exit():
    quit()

def leave():
    quit()

def stop():
    quit()

#-#