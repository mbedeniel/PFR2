from typing import Optional
from imageTreatmentVF.ImageManager import *

def object_finder(color: Optional[Color] = None, nature: Optional[Nature] = None):

    """
    Process :
        -> first we take an image. We analyse that image
            -> step 1 : if the image contain the object we are looking for :
                -> we turn the bot to the left or right so that,
                    the ultrasonic sensor point the object.
                -> the bot go forward to the object.
            -> step 2 : if the image don't contain the object we are looking for :
                -> the bot turn of 60 degree
                -> we execute the "step 1"
                We execute the "step 2" 6 times maximum.
                If after that we haven't identifier the object,
                the bot will go to another position and restart the process.
    """
    image_manager = ImageManager()


    ######## step 2.2 : turn the bot if we have found the object
    object_found = False
    for i in range(7):
        take_image(image_manager)
        object = find_object(image_manager,color,nature)
        if object is not None:
            set_angle(object["angle"]) #Fonction of the rotation of the bot
            return True
        else:
            set_angle(55) #Fonction of the rotation of the bot
    return False ##Dans ce cas on deplace le bot a une nouvelle position et on recommence


def take_image(image_manager : ImageManager):
    ######## step 1 : take and analyse an image
    image_manager.start()

def find_object(image_manager : ImageManager, color : Color, nature : Nature):
    ######## step 2.1 : find the object
    objects = image_manager.objects
    for object in objects :
        if object["color"] == color and object["nature"] == nature :
            return object
    return None




