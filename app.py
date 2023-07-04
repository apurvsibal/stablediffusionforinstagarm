from diffusers import StableDiffusionPipeline
import torch
from PIL import Image, ImageFont, ImageDraw 

model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

def generate_image(prompt):
    image = pipe(prompt, height=640, width=360).images[0] 
    return image

def overlay_text(image,text):
    #variables for image size
    x1 = 360
    y1 = 640
    title_text = text
    sentence = title_text
    image_editable = ImageDraw.Draw(image)
    d = image_editable
    position = (15,15)
    #image_editable.text(position, title_text, (237, 230, 211))

    font = ImageFont.truetype("Cinzel-VariableFont_wght.ttf", 30)
    fnt = font
    #find the average size of the letter
    sum = 0
    for letter in sentence:
      sum += d.textsize(letter, font=fnt)[0]

    average_length_of_letter = sum/len(sentence)

    #find the number of letters to be put on each line
    number_of_letters_for_each_line = (x1/1.618)/average_length_of_letter
    incrementer = 0
    fresh_sentence = ''

    #add some line breaks
    for letter in sentence:
      if(letter == '-'):
        fresh_sentence += '\n\n' + letter
      elif(incrementer < number_of_letters_for_each_line):
        fresh_sentence += letter
      else:
        if(letter == ' '):
          fresh_sentence += '\n'
          incrementer = 0
        else:
          fresh_sentence += letter
      incrementer+=1

    print (fresh_sentence)

    #render the text in the center of the box
    dim = d.textsize(fresh_sentence, font=fnt)
    x2 = dim[0]
    y2 = dim[1]

    qx = (x1/2 - x2/2)
    qy = (y1-y2*3/2)

    left, top, right, bottom = image_editable.textbbox((qx,qy), fresh_sentence, font=font)
    image_editable.rectangle((left-5, top-5, right+5, bottom+5), fill="white")
    image_editable.text((qx,qy), fresh_sentence, align="center", font=font, fill="black")
    return image

from flask import *
app = Flask(__name__)
 
 
@app.route('/success/')
def success(image):
    return render_template("image.html", user_image = image)
 
 
@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        imageprompt = request.form['imageprompt']
        image=generate_image(imageprompt)
        textoverlay = request.form['textoverlay']
        finalimage = overlay_text(image,textoverlay)
        return redirect(url_for('success', image=finalimage))
    
    return render_template("index.html")
    
    
 
 
if __name__ == '__main__':
    app.run(port=8000)