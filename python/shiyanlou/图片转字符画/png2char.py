from PIL import Image
import argparse


ascii_char = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")

# 将256灰度映射到70个字符上
def get_char(r,g,b,alpha = 256):
    if alpha == 0:
        return ' '
    length = len(ascii_char)
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)

    unit = (256.0 + 1)/length
    return ascii_char[int(gray/unit)]

if __name__=="__main__":
    #input arguements process
    parser=argparse.ArgumentParser(description="convert a png to char picture")
    parser.add_argument('file',help='input file')
    parser.add_argument('-o','--output',default='output.txt',help='output file')
    parser.add_argument('--width',type=int,default=80,help='width of char picture')
    parser.add_argument('--height',type=int,default=80,help='height of char picture')
    args=parser.parse_args()

    im=Image.open(args.file)
    # assert isinstance(im,Image)
    # im.convert('L').show()
    im=im.resize((args.width,args.height),Image.NEAREST)

    txt = ""
    for i in range(args.height):
        for j in range(args.width):
            txt += get_char(*im.getpixel((j,i)))
        txt += '\n'

    #字符画输出到文件
    with open(args.output,'w') as f:
        f.write(txt)