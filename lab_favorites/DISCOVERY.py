import pandas as pd
from PIL import Image

def df_image(fileName):
  data = loadImage(fileName)
  return createImageDataFrame(data)

def loadImage(fileName, resize=False, format="RGB"):
  # Open the image using the PIL library
  image = Image.open(fileName)

  # Convert it to an (x, y) array:
  return imageToArray(image, format, resize)


# Resize the image to an `outputSize` x `outputSize` square, where `outputSize` is defined (globally) above.
def squareAndResizeImage(image, resize):
  import PIL

  w, h = image.size
  d = min(w, h)
  image = image.crop( (0, 0, d, d) ).resize( (resize, resize), resample=PIL.Image.LANCZOS )
  
  return image


def rgb2lab(inputColor):
  # Convert RGB [0,255] to [0,1]
  r, g, b = [x / 255.0 for x in inputColor]

  # Apply sRGB companding
  def compand(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

  r, g, b = compand(r), compand(g), compand(b)

  # Convert to XYZ
  X = r * 0.4124 + g * 0.3576 + b * 0.1805
  Y = r * 0.2126 + g * 0.7152 + b * 0.0722
  Z = r * 0.0193 + g * 0.1192 + b * 0.9505

  # Normalize for D65 white point
  X /= 0.95047
  Y /= 1.00000
  Z /= 1.08883

  # LAB conversion helper
  def f(t):
    return t ** (1/3) if t > 0.008856 else (7.787 * t) + (16 / 116)

  fx, fy, fz = f(X), f(Y), f(Z)

  L = (116 * fy) - 16
  a = 500 * (fx - fy)
  b = 200 * (fy - fz)

  return [L, a, b]



# Convert (and resize) an Image to an Lab array
def imageToArray(image, format, resize):
  import numpy as np

  w, h = image.size
  if resize:
    image = squareAndResizeImage(image, resize)

  image = image.convert('RGB')
  rgb = np.array(image)
  if format == "RGB":
    rgb = rgb.astype(int)
    return rgb.transpose([1,0,2])
  elif format == "Lab":
    lab = rgb.astype(float)
    for i in range(len(rgb)):
      for j in range(len(rgb[i])):
        lab[i][j] = rgb2lab(lab[i][j])
    return lab.transpose([1,0,2])
  else:
    raise Exception(f"Unknown format {format}")



def createImageDataFrame(img):
  data = []
  width = len(img)
  height = len(img[0])

  for x in range(width):
    for y in range(height):
      pixel = img[x][y]
      r = pixel[0]
      g = pixel[1]
      b = pixel[2]

      d = {"x": x, "y": y, "r": r, "g": g, "b": b}
      data.append(d)  

  return pd.DataFrame(data)