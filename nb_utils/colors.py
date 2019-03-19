"""
Heavily inspired by:
https://bsou.io/posts/color-gradients-with-python
Copyright 2017 Ben Southgate MIT License
"""
import numpy as np


def hex_to_RGB(hex):
    """'#FFFFFF' -> [255,255,255]"""
    # Pass 16 to the integer function for change of base
    return [int(hex[i:i+2], 16) for i in range(1,6,2)]


def RGB_to_hex(RGB):
    """[255,255,255] -> '#FFFFFF'"""
    # Components need to be integers for hex to make sense
    RGB = [int(x) for x in RGB]
    return "#"+"".join(["0{0:x}".format(v) if v < 16 else
                        "{0:x}".format(v) for v in RGB])


def rand_hex_color(n=1):
    """Generate n random hex colors

    returns: string if n=1, else list of strings
    """

    colors = [
      RGB_to_hex([x*255 for x in np.random.rand(3)])
      for i in range(n)
    ]
    if n == 1:
      return colors[0]
    else:
      return colors


def linear_gradient(start_hex, finish_hex="#FFFFFF", n=10, return_hex=True):
    '''Generate a gradient list of (n) colors

    start_hex, finish_hex: full six-digit color string ("#FFFFFF")
    '''

    s = hex_to_RGB(start_hex)
    f = hex_to_RGB(finish_hex)

    RGB_list = [s]
    # Calcuate a color at each evenly spaced value of t from 1 to n
    for t in range(1, n):
        # Interpolate RGB vector for color at the current value of t
        curr_vector = []
        for j in range(3):
            rgb_part = int(s[j] + (float(t) / (n-1)) * (f[j] - s[j]))
            curr_vector.append(rgb_part)

        # Add it to our list of output colors
        RGB_list.append(curr_vector)

    if return_hex:
        RGB_list = [RGB_to_hex(color) for color in RGB_list]

    return RGB_list


def polylinear_gradient(hex_colors, n):
    if n < len(hex_colors):
        raise ValueError('n must be greater than the number of colors')

    from math import ceil
    # + 1 because we drop it to avoid duplicates
    n_each = ceil(n / (len(hex_colors) - 1)) + 1

    gradient = []
    for color_1, color_2 in zip(hex_colors, hex_colors[1:]):
        new_grad = linear_gradient(color_1, color_2, n_each)
        gradient.extend(new_grad[:-1])

    if len(gradient) > n:
        print(f'dropped {len(gradient) - n} colors from end of the gradient')

    return gradient[:n]
