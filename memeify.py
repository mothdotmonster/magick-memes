#!/usr/bin/env python

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from datetime import datetime
import os, sys
import PySimpleGUI as sg
import numpy as np

if sys.platform.startswith('linux'): # load Linux dependency if on Linux
  from gi.repository import GLib

if sys.platform.startswith('win'): # change some paths if on Windows
  iconpath='icons\icon.ico'
else:
  iconpath='icons/icon.png'

version = "memeify 0.2.3"

sg.theme('DarkAmber') # i like it

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def word_wrap(image, draw, text, roi_width, roi_height):
  # Reduce point size until all text fits within a bounding box.
  mutable_message = text
  iteration_attempts = 100

  def eval_metrics(txt):
    # Quick helper function to calculate width/height of text.
    metrics = draw.get_font_metrics(image, txt, True)
    return (metrics.text_width, metrics.text_height)

  while draw.font_size > 0 and iteration_attempts:
    iteration_attempts -= 1
    width, height = eval_metrics(mutable_message)
    if height > roi_height:
      draw.font_size -= 2  # Reduce pointsize
    elif width > roi_width:
      draw.font_size -= 2  # Reduce pointsize
    else:
      break
  if iteration_attempts < 1:
    raise RuntimeError("Unable to calculate word_wrap for " + text)
  return mutable_message

def thumbnail(image, size): # turn an image into a thumbnail
  with Image(blob=image) as img:
    if img.height > img.width:
      img.sample(height=size, width=int((img.width/img.height)*size))
    else:
      img.sample(width=size, height=int((img.height/img.width)*size))
    return img.make_blob()

def caption(image, top_text, bottom_text): # given an image (as a blob), caption it
  with Image(blob=image) as img:
    with Drawing() as draw:
      draw.stroke_color = "black"
      draw.stroke_width = 3
      draw.fill_color = Color('white')
      draw.font_family = 'Impact'
      draw.font_size = 200
      draw.text_alignment = "center"
      if len(top_text) > 0:
        mutable_message = word_wrap(img, draw, top_text, int(img.width), 200)
        draw.text(int(img.width/2), int(draw.font_size), mutable_message)
        draw.draw(img)
      draw.font_size = 200
      if len(bottom_text) > 0:
        mutable_message = word_wrap(img, draw, bottom_text, int(img.width), 200)
        draw.text(int(img.width/2), int(img.height)-20, mutable_message)
        draw.draw(img)
      return img.make_blob()

def deep_fry(image): # attempts to deep fry image
  with Image(blob=image) as img:
    img.transform(resize='200x200>')
    img.posterize(levels=16)
    img.compression_quality = 20
    img.format = "jpg"
    df = img.make_blob()
  with Image(blob=df) as img:
    img.format = "png"
    img.transform(resize='1000x1000<')
    return img.make_blob()

def liquid_rescale(image): 
  with Image(blob=image) as img:
    img.liquid_rescale(height=int(img.height/2), width=int(img.width/2))
    img.transform(resize='1000x1000<')
    return img.make_blob()

def implode(image):
  with Image(blob=image) as img:
    img.implode(amount=0.5)
    return img.make_blob()

def explode(image):
  with Image(blob=image) as img:
    img.implode(amount=-1)
    return img.make_blob()

def invert(image): # obscenely complicated image inverting
  with Image(blob=image) as img:
    img.alpha_channel = 'remove' #close alpha channel   
    img.background_color = Color('white') 
    array = np.array(img) # convert image into array
  with Image.from_array(np.invert(array), channel_map="rgb") as img: # invert array and turn it back into an image
    img.format = 'png' # make sure it's a png so nothing else breaks
    return img.make_blob()

def swirl(image):
  with Image(blob=image) as img:
    img.swirl(degree=180)
    return img.make_blob()

def rotational_blur(image):
  with Image(blob=image) as img:
    img.rotational_blur(angle=10)
    return img.make_blob()

def meme_window(): # main meme-making window
  layout = [
    [sg.Image(key="-IMAGE-", expand_x=True, expand_y=True)],
    [sg.Text("", expand_x=True),sg.Text("", key="filedisplay"),sg.Text("", expand_x=True)],
    [sg.Text("", expand_x=True),sg.Text("choose an image: "),sg.FileBrowse(target="filedisplay",key="-FILE-"), sg.Button("load image"), sg.Text("", expand_x=True,)],
    [sg.Text("filter:"), sg.DropDown(['deep fry', 'liquid rescale', 'implode', 'explode', 'swirl', 'invert', 'rotational blur'], key = "filter", expand_x=True)],
    [sg.Text("top text:"), sg.InputText(key="top_text", expand_x=True)],
    [sg.Text("bottom text:"), sg.InputText(key="bottom_text", expand_x=True)],
    [sg.Button("memeify!", expand_x=True), sg.Button("export!", expand_x=True)]]
  return sg.Window(version, layout, icon=resource_path(iconpath), size=(600,700), finalize=True)

def ouroborous_window(): # special version without file selector as to stop users from ruining things
  layout = [
    [sg.Image(key="-IMAGE-", expand_x=True, expand_y=True)],
    [sg.Text("filter:"), sg.DropDown(['deep fry', 'liquid rescale', 'implode', 'explode', 'swirl', 'invert', 'rotational blur'], key = "filter", expand_x=True)],
    [sg.Text("top text:"), sg.InputText(key="top_text", expand_x=True)],
    [sg.Text("bottom text:"), sg.InputText(key="bottom_text", expand_x=True)],
    [sg.Button("memeify!", expand_x=True), sg.Button("export!", expand_x=True)]]
  return sg.Window(version, layout, icon=resource_path(iconpath), size=(600,700), finalize=True)

def export_window(): # output window
  layout = [
    [sg.Image(key="-IMAGE-", expand_x=True, expand_y=True)],
    [sg.Text(key="fintext", expand_x=True, justification="center")]]
  return sg.Window("memeification complete!", layout, icon=resource_path(iconpath), size=(600,600), finalize=True)

def main():
  window = meme_window() # open starting window
  while True: # main event loop
    window, event, values = sg.read_all_windows()
    if event == sg.WIN_CLOSED or event == 'Exit':
      break
    elif event == "load image":
      infile = values["-FILE-"]
      if os.path.exists(infile):
        with Image(filename=infile) as img:
          img.format = 'png'
          meme = img.make_blob()
        window["-IMAGE-"].update(thumbnail(meme, 500))
    elif event == "memeify!":
      meme = caption(meme, values["top_text"], values["bottom_text"])
      if values["filter"] == "liquid rescale":
        meme = liquid_rescale(meme)
      if values["filter"] == "implode":
        meme = implode(meme)
      if values["filter"] == "explode":
        meme = explode(meme)
      if values["filter"] == "invert":
        meme = invert(meme)
      if values["filter"] == "swirl":
        meme = swirl(meme)
      if values["filter"] == "deep fry":
        meme = deep_fry(meme)
      if values["filter"] == "rotational blur":
        meme = rotational_blur(meme)
      window.close()
      window = ouroborous_window() # and so the meme eats its own tail
      window["-IMAGE-"].update(thumbnail(meme, 500))
    elif event == "export!":
      if sys.platform.startswith('linux'): # on linux, puts output image in ~/Pictures or equivalent
        outname = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES) + "/memeify-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".png"
      elif sys.platform.startswith('win'): # on windows, puts output image in ~\Pictures (make better later)
        outname = os.path.expanduser('~\Pictures') + "\memeify-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".png"
      else: # fallback, puts output image in current directory
        outname = "memeify-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".png"
      fintext = "Image saved as: " + outname
      with Image(blob=meme) as img:
        img.save(filename=outname)
      window.close()
      window = export_window()
      window["-IMAGE-"].update(thumbnail(meme, 500))
      window["fintext"].update(fintext)
  window.close()

if __name__ == '__main__':
    main()
