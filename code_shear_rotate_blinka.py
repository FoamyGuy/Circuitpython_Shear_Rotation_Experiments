import math
import time

import bitmaptools
import board
from displayio import Group, TileGrid, Palette, Bitmap
import adafruit_imageload
from battler_helper import Character


def print_bmp(bmp):
    for y in range(bmp.height):
        for x in range(bmp.width):
            print(f"{bmp[y, x]},", end="")
        print()


def shear_rotate(bmp, angle, palette):
    clockwise = angle > 0

    if clockwise:
        h_multiplier = math.tan(angle / 2)
        v_multiplier = -math.sin(angle)
    else:
        h_multiplier = -math.tan(angle / 2)
        v_multiplier = math.sin(angle)

    print(f"h_multiplier: {h_multiplier}, v_multiplier: {v_multiplier}")
    h_midway = bmp.width // 2
    v_midway = bmp.height // 2

    first_row_centered_index = h_midway - 0
    first_row_shear_amount = round(first_row_centered_index * h_multiplier)

    first_col_centered_index = v_midway - 0
    first_col_shear_amount = abs(round(first_col_centered_index * v_multiplier))
    print(f"first_col_shear_amount: {first_col_shear_amount}")

    output_bmp = Bitmap(bmp.width + (first_row_shear_amount * 4), bmp.height + (first_col_shear_amount * 2),
                        len(palette))
    print(f"new_bmp size: {output_bmp.width}, {output_bmp.height}")

    # first horizontal shear
    for row_index in range(bmp.height):
        centered_row_index = h_midway - row_index
        shear_amount = round(centered_row_index * h_multiplier)

        x = (first_row_shear_amount * 2) + shear_amount
        y = row_index + first_col_shear_amount
        x1 = 0
        y1 = row_index
        x2 = bmp.width
        y2 = row_index + 1

        print(f"blit vals: x={x}, y={y}, x1={x1}, y1={y1}, x2={x2}, y2={y2}")
        bitmaptools.blit(output_bmp, bmp,
                         x, y,
                         x1=x1, y1=y1,
                         x2=x2, y2=y2)
        print(f"row_index: {row_index} | {centered_row_index} | {shear_amount}")

    vertical_slice_buffer_bmp = Bitmap(1, output_bmp.height, len(palette))
    print("\nSTARTING VERTICAL SHEAR\n")
    # vertical shear
    for col_index in range(bmp.width):
        centered_col_index = v_midway - col_index
        shear_amount = round(centered_col_index * v_multiplier)
        print(f"col_index: {col_index} | {centered_col_index} | {shear_amount}")

        x = col_index + first_row_shear_amount
        y = first_col_shear_amount + shear_amount
        x1 = col_index + first_row_shear_amount
        y1 = first_col_shear_amount
        x2 = col_index + first_row_shear_amount + 1
        y2 = first_col_shear_amount + bmp.height
        print(f"blit vals: x={x}, y={y}, x1={x1}, y1={y1}, x2={x2}, y2={y2}")

        # bitmaptools.fill_region(output_bmp, x1, y1, x2, y2, 4)
        # bitmaptools.fill_region(output_bmp, x, y, x + 1, y + 1, 17)
        bitmaptools.blit(vertical_slice_buffer_bmp, output_bmp,
                         0, 0,
                         x1=x1, y1=y1,
                         x2=x2, y2=y2)

        # erase column in full bmp
        bitmaptools.fill_region(output_bmp, x1, y1, x2, y2, 0)

        bitmaptools.blit(output_bmp, vertical_slice_buffer_bmp,
                         x, y)

    horizontal_slice_buffer_bmp = Bitmap(output_bmp.width, 1, len(palette))

    print("\nSTARTING 2nd HORZONTAL SHEAR\n")

    # second horizontal shear
    for row_index in range(output_bmp.height):
        centered_row_index = (output_bmp.width // 2) - row_index
        shear_amount = round(centered_row_index * h_multiplier)

        x = shear_amount
        y = row_index
        x1 = 0
        y1 = row_index
        x2 = output_bmp.width
        y2 = row_index + 1
        print(f"row_index: {row_index} | {centered_row_index} | {shear_amount}")
        print(f"blit vals: x={x}, y={y}, x1={x1}, y1={y1}, x2={x2}, y2={y2}")

        if x < 0:
            x1 += abs(x)
            x = 0
        if True:  # row_index < (output_bmp.width // 2):
            # bitmaptools.fill_region(output_bmp, x1, y1, x2, y2, 4)
            # bitmaptools.fill_region(output_bmp, x, y, x + 1, y + 1, 17)

            bitmaptools.blit(horizontal_slice_buffer_bmp, output_bmp,
                             0, 0,
                             x1=x1, y1=y1,
                             x2=x2, y2=y2)

            # erase row in full bmp
            bitmaptools.fill_region(output_bmp, x1, y1, x2, y2, 0)

            bitmaptools.blit(output_bmp, horizontal_slice_buffer_bmp, x, y)

    return output_bmp


# Load the sprite sheet (bitmap)
sprite_sheet, palette = adafruit_imageload.load("/castle_sprite_sheet.bmp",
                                                bitmap=Bitmap,
                                                palette=Palette)

palette.make_transparent(0)

# Create the sprite TileGrid
sprite = TileGrid(sprite_sheet, pixel_shader=palette,
                  width=1,
                  height=1,
                  tile_width=16,
                  tile_height=16,
                  default_tile=0)

# rotated_bmp = Bitmap(32, 32, len(palette))
rotated_bmp = Bitmap(16, 16, len(palette))

# bitmaptools.rotozoom(dest_bitmap=rotated_bmp, source_bitmap=sprite_sheet,
#                      source_clip0=(0,0), source_clip1=(16,16), px=7, py=7, angle=1.5708)

bitmaptools.rotozoom(dest_bitmap=rotated_bmp, source_bitmap=sprite_sheet,
                     source_clip0=(0, 0), source_clip1=(16, 16), px=8, py=8)

main_group = Group(scale=5)

rotated_tg = TileGrid(rotated_bmp, pixel_shader=palette, width=1, height=1,
                      tile_width=rotated_bmp.width, tile_height=rotated_bmp.height)

rotated_tg.x = 20

main_group.append(sprite)
main_group.append(rotated_tg)

board.DISPLAY.root_group = main_group

print_bmp(rotated_bmp)

# shear_rotate(rotated_bmp, 30)
shear_rotated_bmp = shear_rotate(rotated_bmp, 0.523599, palette)
shear_rotated_tg = TileGrid(shear_rotated_bmp, pixel_shader=palette, width=1, height=1,
                            tile_width=shear_rotated_bmp.width, tile_height=shear_rotated_bmp.height)

shear_rotated_tg.x = 40
main_group.append(shear_rotated_tg)

while True:
    time.sleep(0.01)
