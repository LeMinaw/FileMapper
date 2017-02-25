#!/usr/bin/env python3

"""A module used for generating images from binary data."""

from PIL       import Image, ImageDraw, ImageColor
from bitstring import BitArray
from math      import ceil, sqrt
from os        import close


def linear(x, xMin, xMax, yMin, yMax):
    """Simple linear range conversion"""
    return (x - xMin) * (yMax - yMin) / (xMax - xMin) + yMin


def gcd(x, y):
    """Simple greatest common divisor"""
    if y == 0:
        return x
    else:
        return gcd(y, x%y)


def lcm(x, y):
    """Simple low common multiple"""
    if x == 0 or y == 0:
        return 0
    else:
        return (x * y) // gcd(x, y)


def bitsFromFile(path):
    """Returns the binary data of a given file as a string of Os and 1s.\n
    path: String, the path to the file"""

    sourceFile = open(path, mode='rb')
    sourceData = bytes=sourceFile.read()
    sourceFile.close()

    return BitArray(sourceData).bin


def map(data, scale=1, ratio=1, multiple=1, cellX=1, cellY=1, mode='offset', name='generated'):
    """Returns a PNG image from a string of binay data.\n
    data: String, the input data (as 0s and 1s)
    scale: Int, the size of a data square (in px)
    ratio: Float, the image ratio (eg. 2, 4/3, 16/9...)
    multiple: Int, the output image dimensions will be a multiple of it
    name: String, the output file  name (without extension)"""

    cellRatio = cellX/cellY
    if mode == 'offset':
        sizeCorrectorX = cellX
        sizeCorrectorY = cellY
    else:
        sizeCorrectorX = 1
        sizeCorrectorY = 1

    sizeX = nceil((sqrt(len(data))*   sqrt(ratio*cellRatio) )/sizeCorrectorX, lcm(multiple, cellX))
    sizeY = nceil((sqrt(len(data))*(1/sqrt(ratio*cellRatio)))/sizeCorrectorY, 1)

    # sizeX = nceil(sqrt(len(data))/sizeCorrectorX, multiple*cellX)
    # sizeY = nceil(sqrt(len(data))/sizeCorrectorY, multiple*cellY)

    image = Image.new(mode='RGBA', size=(sizeX, sizeY), color='white')

    print("Processing...")
    oor = 0

    if mode == 'offset':
        for line in range(0, sizeY):
            for pixel in range(0, sizeX):
                colorData = []
                for y in range(0, cellY):
                    chanData = 0
                    for x in range(0, cellX):
                        try:
                            chanData += int(data[(line*cellY+y) * sizeX*cellX + (pixel*cellX+x)])
                        except IndexError:
                            oor += 1
                            chanData = 0
                    chanData = int(linear(chanData, 0, cellX, 0, 255))
                    colorData.append(chanData)
                image.putpixel((pixel, line), tuple(colorData))
            print("Processed line", line, "/", sizeY)

    elif mode == 'sliding':
        for line in range(0, sizeY):
            for pixel in range(0, sizeX):
                try:
                    colorData = []
                    for y in range(int((1-cellY)/2), int((1+cellY)/2)):
                        chanData = 0
                        for x in range(int((1-cellX)/2), int((1+cellX)/2)):
                            chanData += int(data[(line+y) * sizeX + pixel+x])
                            chanData = int(linear(chanData, 0, cellX, 0, 255))
                        colorData.append(chanData)
                    image.putpixel((pixel, line), tuple(colorData))
                except IndexError:
                    oor += 1
            print("Processed line", line, "/", sizeY)

    else:
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

    print(str(x) + ":" + str(y))
    return y


if __name__=='__main__':
    while True:
        f = input("Path: ")
        data = bitsFromFile(f)
        #print(data)
        #print(percentOfChar(data, '1'))
        #map(data, scale=4, ratio=16/9, multiple=1, cellX=64, cellY=3, mode='offset', name=f)

        map(data, scale=4, ratio=16/9, multiple=16, cellX=1, cellY=1, mode='bin', name=f+'-bin')

        map(data, scale=4, ratio=16/9, multiple=16, cellX=3, cellY=3, mode='sliding', name=f+'-sliding')

        for integ in (64, 32, 24, 16, 12, 8, 6, 4, 2, 1):
            map(data, scale=4, ratio=16/9, multiple=16, cellX=integ, cellY=3, mode='offset', name=f+'-'+str(integ))
