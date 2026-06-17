import pandas as pd
from PIL import Image

def df_image(fileName):
  data = loadImage(fileName)
  return createImageDataFrame(data, fileName)


loadedHEIF = False
def enableHEIF():
  from pillow_heif import register_heif_opener
  register_heif_opener()


def loadImage(fileName, resize=False, format="RGB"):
  global loadedHEIF
  
  # Detect an enable support for HEIF if needed
  if ".HEIC" in fileName.upper() and not loadedHEIF:
    try:
      enableHEIF()
      loadedHEIF = True
    except:
      raise ImportError("Failed to load support for HEIF/HEIC files.  Install the following library to enable HEIF support:\n  python3 -m pip install pillow-heif")  

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


imageCache = {}


def getTileImage(fileName, size):
  key = f"{fileName}-{size}px"

  if key not in imageCache:
    imageCache[key] = squareAndResizeImage(Image.open(fileName), size)

  return imageCache[key]



def isImageFile(file):
  for ext in [".jpg", ".jpeg", ".png", ".heic"]:
    if file.endswith(ext) or file.endswith(ext.upper()):
      return True

  return False

def listTileImagesInPath(path):
  from os import listdir
  from os.path import isfile, join

  files = []
  for f in listdir(path + "/"):
    file = join(path + "/", f)
    if isfile(file) and isImageFile(file):
      files.append(file)

  return files


tada = "\N{PARTY POPPER}"


def run_test_case_1b(green_pixel):
  if len(green_pixel) != 1:
    print("\N{CROSS MARK} `green_pixel` must contain just one pixel.")
    return
  else:
    print("\u2705 `green_pixel` contains just one pixel!")

  if green_pixel["r"].sum() == 0 and green_pixel["g"].sum() == 255 and green_pixel["b"].sum() == 0:
    print("\u2705 `green_pixel` is a green pixel!")
    print(f"{tada} All tests passed! {tada}")
  else:
    print("\N{CROSS MARK} `green_pixel` looks like a pixel, but it's not green! Check your (x, y) coordinates.")
    return


def run_test_case_2(red, green, blue):
  import numbers  
  if isinstance(red, numbers.Number):
    print("\u2705 `red` is a number!")
  else:
    print(f"\N{CROSS MARK} `red` must be a number -- but yours is a {type(red)}.")
    return

  if red == 255:
    print("\u2705 `red` has the correct value!")
  else:
    print(f"\N{CROSS MARK} `red` is not the correct value.  (Did you use the orange pixel?)")
    return


  if isinstance(green, numbers.Number):
    print("\u2705 `green` is a number!")
  else:
    print(f"\N{CROSS MARK} `green` must be a number -- but yours is a {type(green)}.")
    return

  if green == 85:
    print("\u2705 `green` has the correct value!")
  else:
    print(f"\N{CROSS MARK} `green` is not the correct value.  (Did you use the orange pixel?)")
    return


  if isinstance(blue, numbers.Number):
    print("\u2705 `blue` is a number!")
  else:
    print(f"\N{CROSS MARK} `blue` must be a number -- but yours is a {type(blue)}.")
    return

  if blue == 46:
    print("\u2705 `blue` has the correct value!")
  else:
    print(f"\N{CROSS MARK} `blue` is not the correct value.  (Did you use the orange pixel?)")
    return

  print(f"{tada} All tests passed! {tada}")


def run_test_case_3(f):
  df = f("sample.png")
  
  if not isinstance(df, pd.DataFrame):
    print(f"\N{CROSS MARK} Your function must return a DataFrame.")
    return


  for colName in ['r', 'g', 'b', 'x', 'y']:
    if colName not in df:
      print(f"\N{CROSS MARK} `df` must contain a variable (column) `{colName}`.")
      return

  print("\u2705 `df` looks good!")
  print(f"{tada} All tests passed! {tada}")


def run_test_case_4(findAverageColor):
  pixelData = [
    { "r": 0, "g": 0, "b": 0 },
    { "r": 0, "g": 0, "b": 0 },
    { "r": 3, "g": 6, "b": 9 },
  ]
  result = findAverageColor(pd.DataFrame(pixelData))
  
  for colName in ['r_avg', 'g_avg', 'b_avg']:
    if colName not in result:
      print(f"\N{CROSS MARK} Dictionary must contain the key `{colName}`.")
      return
    else:
      print(f"\u2705 Dictionary contain the key `{colName}`.")

  if result["r_avg"] == 1 and result["g_avg"] == 2 and result["b_avg"] == 3:
    print("\u2705 The values all appear correct!")
    print(f"{tada} All tests passed! {tada}")
  else:
    print(f"\N{CROSS MARK} Dictionary data is incorrect.")


def run_test_case_5(findImageSubset):
  rawPixelData = [
    # [0]           [1]           [2]           [3]
    [ [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0] ],  # [0]
    [ [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0], [30, 60, 90] ],  # [1]
    [ [ 0,  0,  0], [ 0,  0,  0], [30, 60, 90], [30, 60, 90] ],  # [2]
    [ [ 0,  0,  0], [30, 60, 90], [30, 60, 90], [30, 60, 90] ],  # [3]
    [ [30, 60, 90], [30, 60, 90], [30, 60, 90], [30, 60, 90] ],  # [4]
    [ [30, 60, 90], [30, 60, 90], [30, 60, 90], [ 0,  0,  0] ],  # [5]
    [ [30, 60, 90], [30, 60, 90], [ 0,  0,  0], [ 0,  0,  0] ],  # [6]
    [ [30, 60, 90], [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0] ],  # [7]
    [ [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0] ],  # [8]
  ]

  d = []
  for x in range(len(rawPixelData)):
    for y in range(len(rawPixelData[0])):
      p = rawPixelData[x][y]
      d.append({"x": x, "y": y, "r": p[0], "g": p[1], "b": p[2]})
  pixelData = pd.DataFrame(d)

  def TEST_findImageSubset(f, x, y, w, h, expected):
    result = f(pixelData, x, y, w, h)
    if len(result) != w * h:
      print(f"\N{CROSS MARK} findImageSubset(image, x0={x}, y0={y}, width={w}, height={h}) must have {w * h} pixels.")
      print("== Your DataFrame ==")
      print(result)
      return False

    if len(result[ result.x < x ]) != 0:
      print(f"\N{CROSS MARK} findImageSubset(image, x0={x}, y0={y}, width={w}, height={h}) must have no pixels less than x={x}.")
      print("== Your DataFrame ==")
      print(result)
      return False

    if len(result[ result.x >= x + w ]) != 0:
      print(f"\N{CROSS MARK} findImageSubset(image, x0={x}, y0={y}, width={w}, height={h}) must have no pixels greater than or equal to x={x + w}.")
      print("== Your DataFrame ==")
      print(result)
      return False

    if len(result[ result.y < y ]) != 0:
      print(f"\N{CROSS MARK} findImageSubset(image, x0={x}, y0={y}, width={w}, height={h}) must have no pixels less than y={y}.")
      print("== Your DataFrame ==")
      print(result)
      return False

    if len(result[ result.y >= y + h ]) != 0:
      print(f"\N{CROSS MARK} findImageSubset(image, x0={x}, y0={y}, width={w}, height={h}) must have no pixels greater than or equal to y={y + h}.")
      print("== Your DataFrame ==")
      print(result)
      return False
    

    print(f"\u2705 Test case for findImageSubset(image, x0={x}, y0={y}, width={w}, height={h}) appears correct.")
    return True

  r = TEST_findImageSubset(findImageSubset, 0, 0, 2, 2, [0, 0, 0])
  if not r: return

  r = TEST_findImageSubset(findImageSubset, 2, 0, 2, 2, [7.5, 15, 22.5])
  if not r: return

  r = TEST_findImageSubset(findImageSubset, 2, 2, 2, 2, [30, 60, 90])
  if not r: return

  r = TEST_findImageSubset(findImageSubset, 5, 1, 2, 2, [90/4, 180/4, 270/4])
  if not r: return

  r = TEST_findImageSubset(findImageSubset, 5, 1, 3, 2, [90/8, 180/8, 270/8])
  if not r: return

  r = TEST_findImageSubset(findImageSubset, 5, 1, 4, 3, [90/12, 180/12, 270/12])
  if not r: return

  r = TEST_findImageSubset(findImageSubset, 1, 1, 1, 3, [90/12, 180/12, 270/12])
  if not r: return

  print(f"{tada} All tests passed! {tada}")


def run_test_case_6(findAverageImageSubsetColor):
  rawPixelData = [
    # [0]           [1]           [2]           [3]
    [ [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0] ],  # [0]
    [ [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0], [30, 60, 90] ],  # [1]
    [ [ 0,  0,  0], [ 0,  0,  0], [30, 60, 90], [30, 60, 90] ],  # [2]
    [ [ 0,  0,  0], [30, 60, 90], [30, 60, 90], [30, 60, 90] ],  # [3]
    [ [30, 60, 90], [30, 60, 90], [30, 60, 90], [30, 60, 90] ],  # [4]
    [ [30, 60, 90], [30, 60, 90], [30, 60, 90], [ 0,  0,  0] ],  # [5]
    [ [30, 60, 90], [30, 60, 90], [ 0,  0,  0], [ 0,  0,  0] ],  # [6]
    [ [30, 60, 90], [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0] ],  # [7]
    [ [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0], [ 0,  0,  0] ],  # [8]
  ]

  d = []
  for x in range(len(rawPixelData)):
    for y in range(len(rawPixelData[0])):
      p = rawPixelData[x][y]
      d.append({"x": x, "y": y, "r": p[0], "g": p[1], "b": p[2]})
  pixelData = pd.DataFrame(d)

  def TEST_findAverageImageSubsetColor(f, x, y, w, h, expected):
    result = f(pixelData, x, y, w, h)

    if result["r_avg"] != expected[0] or result["g_avg"] != expected[1] or result["b_avg"] != expected[2]:
      print(f"\N{CROSS MARK} Test case for findAverageImageSubsetColor(image, x0={x}, y0={y}, width={w}, height={h}) did not have the expected value.")
      
      r = result["r_avg"]
      g = result["g_avg"]
      b = result["b_avg"]
      print(f"  Your Result: r_avg={r}, g_avg={g}, b_avg={b}")

      r = expected[0]
      g = expected[1]
      b = expected[2]
      print(f"  Expected Result: r_avg={r}, g_avg={g}, b_avg={b}")
      return False
    else:
      print(f"\u2705 Test case for findAverageImageSubsetColor(image, x={x}, y={y}, width={w}, height={h}) appears correct.")
      return True
    
  r = TEST_findAverageImageSubsetColor(findAverageImageSubsetColor, 0, 0, 2, 2, [0, 0, 0])
  if not r: return

  r = TEST_findAverageImageSubsetColor(findAverageImageSubsetColor, 2, 0, 2, 2, [7.5, 15, 22.5])
  if not r: return

  r = TEST_findAverageImageSubsetColor(findAverageImageSubsetColor, 2, 2, 2, 2, [30, 60, 90])
  if not r: return

  r = TEST_findAverageImageSubsetColor(findAverageImageSubsetColor, 5, 1, 2, 2, [90/4, 180/4, 270/4])
  if not r: return

  r = TEST_findAverageImageSubsetColor(findAverageImageSubsetColor, 5, 1, 3, 2, [15, 30, 45])
  if not r: return

  r = TEST_findAverageImageSubsetColor(findAverageImageSubsetColor, 5, 1, 4, 3, [90/12, 180/12, 270/12])
  if not r: return

  r = TEST_findAverageImageSubsetColor(findAverageImageSubsetColor, 1, 1, 1, 3, [10, 20, 30])
  if not r: return

  print(f"{tada} All tests passed! {tada}")



def run_test_case_8(findBestTile):
  real_df = pd.DataFrame([
      {'file': 'notebook-images/test.png', 'r': 47.19722525581813, 'g': 49.03421116311881, 'b': 38.60877549417687},
      {'file': 'notebook-images/test2.png', 'r': 54.24409328969397, 'g': 59.3141053878179, 'b': 52.97987993308968},
      {'file': 'notebook-images/test3.png', 'r': 46.41423991872082, 'g': 47.89200069370779, 'b': 37.011986112075455}
  ])

  try:
    bestMatch = findBestTile(real_df, 0, 0, 0)
    assert(type(bestMatch) == type(pd.DataFrame())), "findBestMatch must return a DataFrame"
    assert(len(bestMatch) == 1), "findBestMatch must return exactly one best match"
    assert(bestMatch['file'].values[0] == 'notebook-images/test3.png'), "findBestMatch did not return the best match for test (r=0, g=0, b=0)"
    print(f"\u2705 Test case #1 (r=0, g=0, b=0) passed!")

    bestMatch = findBestTile(real_df, 47, 49, 38)
    assert(bestMatch['file'].values[0] == 'notebook-images/test.png'), "findBestMatch did not return the best match for test (r=47, g=49, b=38)"
    print(f"\u2705 Test case #1 (r=47, g=49, b=38) passed!")

    bestMatch = findBestTile(real_df, 54, 49, 38)
    assert(bestMatch['file'].values[0] == 'notebook-images/test.png'), "findBestMatch did not return the best match for test (r=54, g=49, b=38)"
    print(f"\u2705 Test case #1 (r=54, g=49, b=38) passed!")

    bestMatch = findBestTile(real_df, 54, 49, 52)
    assert(bestMatch['file'].values[0] == 'notebook-images/test2.png'), "findBestMatch did not return the best match for test (r=54, g=49, b=52)"
    print(f"\u2705 Test case #1 (r=54, g=49, b=52) passed!")

    bestMatch = findBestTile(real_df, -100, -100, -100)
    assert(bestMatch['file'].values[0] == 'notebook-images/test3.png'), "findBestMatch did not return the best match for test (r=-100, g=-100, b=-100)"
    print(f"\u2705 Test case #1 (r=-100, g=-100, b=-100) passed!")

    print(f"{tada} All tests passed! {tada}")

  except AssertionError as e:
    print(f"\N{CROSS MARK} {e}.")

  


# def createImageDataFrame(width, height):
#   import random

#   data = []
#   for x in range(width):
#     for y in range(height):
#       data.append( {"x": x, "y": y, "r": random.randint(0, 255), "g": random.randint(0, 255), "b": random.randint(0, 255)} )
  
#   return pd.DataFrame(data)


def createImageDataFrame(img, fileName = None):
  data = []
  width = len(img)
  height = len(img[0])

  if (width > 400 or height > 400) and (fileName != "base.jpg"):
    print(f"⚠️ Your file {fileName} is large! ⚠️")
    print("- If this is being used as a tile image, your mosaic may run for a LONG time due to the size of your photo.")
    print("- View the notebook `shrink-images.ipynb` to pre-shrink the images into a new `tiles-small` folder if you need to speed up your program.")

  for x in range(width):
    for y in range(height):
      pixel = img[x][y]
      r = pixel[0]
      g = pixel[1]
      b = pixel[2]

      d = {"x": x, "y": y, "r": r, "g": g, "b": b}
      data.append(d)  

  return pd.DataFrame(data)