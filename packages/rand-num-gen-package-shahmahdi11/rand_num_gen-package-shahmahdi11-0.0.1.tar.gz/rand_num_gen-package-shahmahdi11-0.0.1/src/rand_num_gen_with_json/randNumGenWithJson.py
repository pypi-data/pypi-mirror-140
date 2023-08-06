#!/usr/bin/env python
# coding: utf-8

# Import required libraries
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import os
import random
import json

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def add_one(number):
    return number + 1

# Generate the image set
def generate_images(edition, random_number, image_id):
    
    op_path = os.path.join('output', 'edition ' + str(edition))

    image_name = '12.png'
    
    # Create output directory if it doesn't exist
    if not os.path.exists(op_path):
        os.makedirs(op_path)
      
    # create card image start
    bg = Image.open("lucky_draw.png")
    width, height = bg.size
    bg.save(os.path.join(op_path, image_name))
    # create card image end

    # create random number image start
    img = Image.new('RGB', (width,height), (255,255,255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("OpenSans.ttf", 35)
    draw.text((width - 150, height - 95), str(random_number),(113,50,211),font=font)
    number_image = os.path.join(op_path, 'digit_number_img_'+str(random_number)+'.png')
    img.save(number_image)
    # create random number image end

    # create random number transparent image start
    img = Image.open(number_image)
    rgba = img.convert("RGBA")
    datas = rgba.getdata()
    
    new_data = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:  # finding white colour by its RGB value
            # storing a transparent value when we find a black colour
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)  # other colours remain unchanged
    
    rgba.putdata(new_data)
    rgba.save(os.path.join(op_path, "transparent_image.png"), "PNG")
    # create random number transparent image end

    # manupulate main image start

    main_image_bg = Image.open(os.path.join(op_path, image_name))
    main_number_img = Image.open(os.path.join(op_path, "transparent_image.png"))
    main_image_bg.paste(main_number_img, (0,0), main_number_img)
    main_image_bg.save(os.path.join(op_path, str(image_id) + ".png"))

    # manupulate main image end

    # remove unused image start
    
    os.remove(os.path.join(op_path, image_name))
    os.remove(os.path.join(op_path, 'digit_number_img_'+str(random_number)+'.png'))
    os.remove(os.path.join(op_path, "transparent_image.png"))

    # remove unused image end

    # create a JSON file start

    json_obj = {
        "id": image_id,
        "name": "Lottery Ticket " + str(image_id),
        "description": "Own to Win", 
        "image": str(image_id) + ".png", 
        "attributes": [
            {
                "trait_type": "ID", 
                "value": image_id,
                "max":100
            },
            {
                "trait_type": "Number",
                "value": random_number
            }
        ]
    }
    serialized_json_object = json.dumps(json_obj, indent = 4)
    # print(serialized_json_object)

    json_file_name = str(image_id) + ".json"
    with open(os.path.join(op_path, json_file_name), "w") as outfile:
        outfile.write(serialized_json_object)

    # create a JSON file end


# Main function. Point of entry
def main():
    
    print("Starting task...")
    print("How many tokens would you like to create? Enter a number greater than 0: ")
    while True:
        total_no_of_images = int(input())
        if total_no_of_images > 0:
            break
    print("What would you like to call this edition?: ")
    edition_name = input()
    for n in range(0,total_no_of_images):
        random_number = random.randint(10000, 99999)
        generate_images(edition_name, random_number, n+1)
        
    print("Task complete!")

main()
