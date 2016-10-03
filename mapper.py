#!/usr/bin/env python3

"""A module used for generating images from binary data."""

from PIL       import Image, ImageDraw, ImageColor
from bitstring import BitArray
from math      import ceil, sqrt
from os        import close

def bitsFromFile(path):
    """Returns the binary data of a given file as a string of Os and 1s.\n
    path: String, the path to the file"""

    sourceFile = open(path, mode='rb')
    sourceData = bytes=sourceFile.read()
    sourceFile.close()

    return BitArray(sourceData).bin

def map(data, scale=1, ratio=1, multiple=1, name='generated'):
    """Returns a PNG image from a string of binay data.\n
    data: String, the input data (as 0s and 1s)
    scale: Int, the size of a data square (in px)
    ratio: Float, the image ratio (eg. 2, 4/3, 16/9...)
    multiple: Int, the output image dimensions will be a multiple of it
    name: String, the output file  name (without extension)"""

    sizeX = nceil(sqrt(len(data))*sqrt(ratio), multiple)
    sizeY = nceil(sqrt(len(data))*(1/sqrt(ratio)), multiple)

    image = Image.new(mode='RGBA', size=(sizeX, sizeY), color='white')

    print("Processing...")
    oor = 0
    for line in range(0, sizeY):
        for pixel in range(0, sizeX):
            try:
                if data[line * sizeX + pixel] == '1':
                    image.putpixel((pixel, line), (0, 0, 0))
            except IndexError:
                oor += 1
        print("Processed line", line, "/", sizeY)

    print("OOR:", oor)
    print("Saving...")
    image = image.resize((sizeX * scale, sizeY * scale))
    image.save(name + '.png')
    print("Done !")

def percentOfChar(data, char):
    """Returns the percent of a given char in a string.\n
    data: String, the input
    char: String, the char to count"""

    return data.count(char)/len(data)*100

def nceil(x, n=1):
    """Returns the next n-multiple of a number.\n
    x: Float, the input number
    n: Float, will be the next multiple of this number"""

    y = ceil(x) - ceil(x) % n
    if y < x:
        y += n
    return y


if __name__=='__main__':
    while True:
        f = input("Path: ")
        data = bitsFromFile(f)
        #print(data)
        #print(percentOfChar(data, '1'))
        map(data, scale=1, ratio=16/9, multiple=8, name=f)
