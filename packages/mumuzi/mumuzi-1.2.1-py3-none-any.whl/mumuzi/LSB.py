#author 8神 Cheyenne
#感谢8神提供脚本，救了命了
from PIL import Image
import math

# 把字节对应转换成二进制字符串
def Byte2Bin(byte, order):
    s = ''
    for i in range(len(byte)):
        if order == 'lsb':
            tmp = str(bin(byte[i]))[2:].zfill(8)
        elif order == 'msb':
            tmp = str(bin(byte[i]))[2:].zfill(8)[::-1]
        else:
            raise(NameError)
        s += tmp
    return(s)

# 把8位二进制数的第n位（从低往高数）替换成0或1
def NumReplace(number, n, x01):
    if number > 255 or number < 0 or n > 7 or n < 0 or x01 not in [0, 1]:
        raise(NameError)
    tmp = str(bin(number))[2:].zfill(8)
    n = 7 - n
    s = tmp[:n] + str(x01) + tmp[n+1:]
    return(int(s, 2))


def LSB(path, ori, out, payload, bit = '0', plane = 'RGB', axis = 'x', order = 'lsb'):
    img = Image.open(path + ori)
    w, h, m = img.size[0], img.size[1], img.mode
    binstr = Byte2Bin(payload, order)

    # 把plane参数转换成对应通道的顺序的列表
    plist = []
    for i in plane:
        if m.find(i) == -1:
            raise(IndexError)
        else:
            plist += [m.find(i)]

    # 把bit参数转换成对应字节位的列表
    blist = []
    for i in bit:
        blist += [int(i)]

    # 计算需要的像素数量（不判断图片像素够不够用）
    pixelnum = math.ceil(len(binstr) / (len(plist) * len(bit)))

    # 开始隐写
    for a in range(pixelnum):
        if axis == 'x':
            px, py = a % w, a // w
        elif axis == 'y':
            py, px = a % h, a // h
        else:
            raise(NameError)
        pixel = list(img.getpixel((px, py)))
        for b in range(len(plist)):
            for c in range(len(bit)):
                binstrnum = a * len(plist) * len(bit) + b * len(bit) + c
                if binstrnum < len(binstr):
                    pixel[plist[b]] = NumReplace(pixel[plist[b]], blist[c], int(binstr[binstrnum]))
        img.putpixel((px, py), tuple(pixel))

    img.save(path + out)