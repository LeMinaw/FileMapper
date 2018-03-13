#!/usr/bin/env python3

"""A module used for generating images from binary data."""

from PIL             import Image, ImageDraw, ImageColor
from bitstring       import BitArray
from math            import ceil, sqrt
from multiprocessing import Pool
from os              import close


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


def linear(x, xMin, xMax, yMin=0, yMax=1):
    """Simple linear range conversion"""
    return (x - xMin) * (yMax - yMin) / (xMax - xMin) + yMin


def gcd(x, y):
    """Simple greatest common divisor"""
    if y == 0:
        return x
    else:
        return gcd(y, x % y)


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


def truncate(data, start, end):
    """Relative file truncation.
    start: In %, where to start
    end: In %, where to stop"""

    start = int(len(data) * start / 100)
    end   = int(len(data) * end   / 100)

    if start == end:
        return None
    elif start > end:
        end, start = start, end
        data.reverse()
    return data[start:end]


def computePixel(mode, data, line, pixel, sizeY, sizeX, cellY, cellX, zoneSize):
    """Pixel computation logic. Not really to be called manually...\n
    Modes :\n
    - bin
    - offset
    - y-offset
    - split
    - sliding (REMOVED)"""

    if mode == 'bin':
        try:
            if data[line * sizeX + pixel] == '1':
                return (0, 0, 0)
        except IndexError:
            pass
        return (255, 255, 255)
    else:
        colorData = []
        if mode =='y-offset':
            for x in range(0, cellX):
                chanData = 0
                for y in range(0, cellY):
                    try:
                        chanData += int(data[(line*cellY+y) * sizeX*cellX + pixel*cellX+x])
                    except IndexError:
                        chanData = 0
                chanData = int(linear(chanData, 0, cellY, 0, 255))
                colorData.append(chanData)
        else:
            for y in range(0, cellY):
                chanData = 0
                for x in range(0, cellX):
                    try:
                        if mode == 'offset':
                            chanData += int(data[(line*cellY+y) * sizeX*cellX + (pixel*cellX+x)])
                        elif mode == 'split':
                            chanData += int(data[line*sizeX*cellX + zoneSize*y + pixel*cellX+x])
                    except IndexError:
                        chanData = 0
                chanData = int(linear(chanData, 0, cellX, 0, 255))
                colorData.append(chanData)
        return tuple(colorData)

    # Old snippet from an old mode :
    # for y in range(int((1-cellY)/2), int((1+cellY)/2)):
    #     chanData = 0
    #     for x in range(int((1-cellX)/2), int((1+cellX)/2)):
    #         try:
    #             chanData += int(data[(line+y) * sizeX + pixel+x])
    #         except IndexError:
    #             pass
    #         chanData = int(linear(chanData, 0, cellX, 0, 255))
    #     colorData.append(chanData)


def map(data, scale=1, ratio=1, multiple=1, cellX=1, cellY=1, mode='offset', name='generated', processes=2):
    """Returns a PNG image from a string of binay data.\n
    data: String, the input data (as 0s and 1s)
    scale: Int, the size of a data square (in px)
    ratio: Float, the image ratio (eg. 2, 4/3, 16/9...)
    multiple: Int, the output image dimensions will be a multiple of it
    name: String, the output file  name (without extension)"""

    cellRatio = cellX/cellY
    if mode == 'normal':
        sizeCorrectorX = 1
        sizeCorrectorY = 1
    else:
        sizeCorrectorX = cellX
        sizeCorrectorY = cellY

    sizeX = nceil((sqrt(len(data))*   sqrt(ratio*cellRatio) )/sizeCorrectorX, lcm(multiple, cellX))
    sizeY = nceil((sqrt(len(data))*(1/sqrt(ratio*cellRatio)))/sizeCorrectorY, 1)
    zoneSize = len(data) // cellY

    image = Image.new(mode='RGBA', size=(sizeX, sizeY), color='white')

    print("=== Starting processing on %s child processe(s) ===" % str(processes))
    pool = Pool(processes)
    args = []
    for line in range(0, sizeY):
        for pixel in range(0, sizeX):
            args.append((mode, data, line, pixel, sizeY, sizeX, cellY, cellX, zoneSize))

    imageData = pool.starmap(computePixel, args)

    print("Saving %s ..." % name)
    image.putdata(imageData)
    image = image.resize((sizeX * scale, sizeY * scale))
    image.save(name + '.png')
    print("Done !")


if __name__=='__main__':
    while True:
        f = input("Path: ")
        if f == '':
            exit()
        data = bitsFromFile(f)
        #data = truncate(data, 50, 51)
        #print(data)
        #print(percentOfChar(data, '1'))

        map(data, scale=4, ratio=16/9, multiple=16, cellX=1, cellY=1, mode='bin', name=f+'-bin', processes=8)
        for integ in (64, 32, 24, 16, 12, 8, 6, 4, 2, 1):
            # map(data, scale=4, ratio=16/9, multiple=16, cellX=3, cellY=integ, mode='y-offset', name=f+'-'+str(integ), processes=8)
            map(data, scale=4, ratio=16/9, multiple=16, cellX=integ, cellY=3, mode='offset', name=f+'-'+str(integ), processes=8)

        # for i in range(0, 200):
        #     trump = truncate(data, i/4, 50+i/4)
        #     map(trump, scale=4, ratio=16/9, multiple=16, cellX=4, cellY=3, mode='offset', name=f+'-'+str(i), processes=8)
