from PIL import Image, ImageDraw
import binascii
import math
import string 
import random
import cv2

class T2i:
  def __init__(self):
    self.image_height = 240
    self.image_width = 240
    self.image_block = 40

  # RGB -> Hex Color
  def createRgbtoHex(self, rgb):
    return ('%02x%02x%02x' % (rgb[2], rgb[1], rgb[0]))

  # Image -> Color(HEX)
  def getHexFromImage(self, image):
    w = self.image_height
    h = self.image_width
    block = self.image_block
    line_number = 0
    image = cv2.imread(image+".png")
    color = []
    image_range = (w/block)*(h/block)
    for i in range(round(image_range)):
      if (i != 0 and i%(w/block) == 0):
        line_number += 1
      check_size_height = int((block/2)+block*(i%(h/block)))
      check_size_width = int((block/2)+block*line_number)
      print('check_size > '+str(check_size_height)+' '+str(check_size_width))

      color_temp = image[check_size_width, check_size_height]
      print(color_temp)

      if (color_temp[0] != 0 and color_temp[1] != 0 and color_temp[2] != 0):
        color.append(('%02x%02x%02x' % (int(color_temp[2]), int(color_temp[1]), int(color_temp[0]))))
      else:
        break
      


    return color

  # 랜덤 ID 생성
  def generatePrimaryId(self):
    length = 28
    stringPool = string.ascii_lowercase+'1234567890'
    result = ""
    for i in range(length) :
        result += random.choice(stringPool)
    return result

  # 텍스트를 hex로 변환
  def createHex(self, text):
    textEncode = text.encode("utf-8").hex()
    tempText = []
    for i in range(len(textEncode)+6):
      if i % 6 == 0:
        tempText.append(textEncode[int(i)-6:int(i)])
    
    return tempText



  def createEncryptionImage(self, hexlist):
    w = self.image_height # 60w 60h 10c
    h = self.image_width
    c = self.image_block # 블록 크기
    k = 0 # 라인 넘버 (첫번째 라인은 0번)
    img = Image.new('RGB', (w, h), color = 'black')
    img1 = ImageDraw.Draw(img)
    # shape1 = [(10, 10), (w - 60, h - 60)]
    # shape2 = [(20, 10), (w - 50, h - 60)]

    for i in range(len(hexlist)):
      if (hexlist[i] == ""):
        print('N1')
      elif (len(hexlist[i]) != 6):
        print('N2')
      elif (i % (h/c) == 0):
        print(hexlist[i], k, [((w), c*(k+1)), (w+(i%(w/c)-1)*c), (k*c)])
        img1.rectangle([((w), c*(k+1)), (w+(i%(w/c)-1)*c), (k*c)], fill ="#"+hexlist[i])
        k += 1
      elif (hexlist[i] != ""):
        print(hexlist[i], k, [(c*(i%(h/c)), c*(k+1)), ((i%(w/c)-1)*c), (k*c)])
        img1.rectangle([(c*(i%(h/c)), c*(k+1)), ((i%(w/c)-1)*c), (k*c)], fill ="#"+hexlist[i])

    img.show()
    img.save('result.png')