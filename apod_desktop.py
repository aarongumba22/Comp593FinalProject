""""
COMP 593 - Final Project
Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.
Usage:
  python apod_desktop.py image_dir_path [apod_date]
Parameters:
  image_dir_path = Full path of directory in which APOD image is stored
  apod_date = APOD image date (format: YYYY-MM-DD)
History:
  Date        Author    Description
  2022-03-11  J.Dalby   Initial creation
  2022-04-07  A.Gumba   Finish get_apod_info and get_apod_date
  2022-04-10  A.Gumba   Finish create_image_db and download_apod_image
  2022-04-11  A.Gumba   Finish the rest
  2022-04-13  A.Gumba   Gluing it all together in the main()
  
"""


from sys import argv, exit
from datetime import datetime, date
from datetime import date
from hashlib import sha256 #getting the sha
import hashlib 
import shutil # for copying th file
from os import path
from os.path import exists #check if file exist
import os.path 
from pprint import pprint
import sqlite3# for database use
from pip._vendor import requests # for requesting http connection
import ctypes #for setting up the background
from pprint import pprint

def main():

    # Determine the paths where files are stored
    image_dir_path = get_image_dir_path()
    db_path = path.join(image_dir_path, 'apod_images.db')

    # Get the APOD date, if specified as a parameter
    apod_date = get_apod_date()

    # Create the images database if it does not already exist
    create_image_db(db_path)

    # Get info for the APOD
    apod_info_dict = get_apod_info(apod_date)
    
    # Download today's APOD
    image_url = download_apod_image(apod_info_dict)
    image_msg = image_url
    sha256_ = hashlib.sha256(image_url.encode())
    image_sha256 = str((sha256_.digest())) #get the sha number of a file
    image_path = get_image_path(image_url, image_dir_path)
    image_size = os.path.getsize(image_path) # get the size of the file

    # Print APOD image information
    print_apod_info(image_url, image_path, image_size, image_sha256)

    # Add image to cache if not already present
    if not image_already_in_db(db_path, image_sha256):
        save_image_file(image_msg,image_path)
        add_image_to_db(db_path, image_path, image_size, image_sha256)

    # Set the desktop background image to the selected APOD
    
    filename = image_url.split("/")[-1]
    background =os.path.join(image_path,filename)
    set_desktop_background_image(background)

def get_image_dir_path():
    """
    Validates the command line parameter that specifies the path
    in which all downloaded images are saved locally.

    :returns: Path of directory in which images are saved locally
    """
    
    if len(argv) >= 2:
        dir_path = argv[1]
        if path.isdir(dir_path):
            print("Images directory:", dir_path)
            return dir_path
        else:
            print('Error: Non-existent directory', dir_path)
            exit('Script execution aborted')
    else:
        print('Error: Missing path parameter.')
        exit('Script execution aborted')

def get_apod_date():
    """
    Validates the command line parameter that specifies the APOD date.
    Aborts script execution if date format is invalid.

    :returns: APOD date as a string in 'YYYY-MM-DD' format
    """  
    
    if len(argv) >= 3:
        # Date parameter has been provided, so get it
        apod_date = argv[2]

        # Validate the date parameter format
        try:
            datetime.strptime(apod_date, '%Y-%m-%d')
        except ValueError:
            print('Error: Incorrect date format; Should be YYYY-MM-DD')
            exit('Script execution aborted')
    else:
        # No date parameter has been provided, so use today's date
        apod_date = date.today().isoformat()
    
    print("APOD date:", apod_date)
    return (apod_date)

def get_image_path(image_url, dir_path):
    """
    Determines the path at which an image downloaded from
    a specified URL is saved locally.

    :param image_url: URL of image
    :param dir_path: Path of directory in which image is saved locally
    :returns: Path at which image is saved locally
    """
    url =image_url #image url
    filename= url.split("/")[-1] #get the picture's name
    
    resides =  dir_path # where the photo are saved
    
    full_path= os.path.join(resides,filename)# full path of photo
    print(full_path)
    return resides

def get_apod_info(date):
    """
    Gets information from the NASA API for the Astronomy 
    Picture of the Day (APOD) from a specified date.

    :param date: APOD date formatted as YYYY-MM-DD
    :returns: Dictionary of APOD info
    """    
    #return {"todo" : "TODO"}
    nasa_api= 'https://api.nasa.gov/planetary/apod?api_key='
    my_key='YwiFf9Lh266Z4fLYb61gkwT2vBdOxx6jHZXJ7NDh'
    
    params= (nasa_api + my_key +"&date=" + str(date))
     
    print(params)
    print("Getting  APOD info......")
    
    response = requests.get(params)

    if response.status_code == 200:
        
        
        print('Response:',response.status_code, '🎉🎉🎉', '\n')
        print("Success Date obtained")
        info =response.json()
        info_dict= dict(info)#transform it to a dictionary
        
        return info_dict
        
    else:
        print('Uh Oh, Unsucessful',response.status_code)
        return None

def print_apod_info(image_url, image_path, image_size, image_sha256):
    """
    Prints information about the APOD

    :param image_url: URL of image
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """    
    print("the Url is " + image_url,".")
    print("Full path is " + image_path,".")
    print("The Image size is ", image_size,"KB.")
    print("The Sha-256 is ", image_sha256)
    
    return None
    
    

def download_apod_image(image_url):
    """
    Downloads an image from a specified URL.

    :param image_url: URL of image
    :returns: Response message that contains image data
    """
    image =(image_url['url']) #the image data info saved here
    
    image_data = requests.get(image) #connection to url
    
   
    if image_data.status_code == 200:
        print('Response:',image_data.status_code, '🎉🎉🎉', '\n')
        print("Success connection")
        return image
       
            
    else:
        print('failed to download photo',image_data.status_code)
        return None
    
    
def save_image_file(image_msg, image_path):
    """
    Extracts an image file from an HTTP response message
    and saves the image file to disk.

    :param image_msg: HTTP response message
    :param image_path: Path to save image file
    :returns: None
    """
    url =image_msg #url of the photo thats gonna get saved
    req=requests.get(url,stream = True) #stream to guranteed no interruption gathering the content without it its corrupted and 0KB
    
    if req.status_code == 200:
        print('Response:',req.status_code, '🎉🎉🎉', '\n')
        print("Successfully saved")
             
    else:
        print('failed to download photo',req.status_code)
        
    filename = url.split("/")[-1] #to get the name of the file
    req.raw.decode_content = True #so data file size will not be 0
    path = image_path #where it will resides
    complete = os.path.join(path,filename)
        
    
    with open(complete,'wb') as f: #open file in write mode and binary
        shutil.copyfileobj(req.raw, f)
        
    
    
    return None

def create_image_db(db_path):
    """
    Creates an image database if it doesn't already exist.

    :param db_path: Path of .db file
    :returns: None
    """
    path = db_path
    
    
    f_exist= exists(path)
    if f_exist == False:
        db_path =sqlite3.connect(path) #connect to sqlite
        c = db_path.cursor() #give coammands to database
    #create a table
        c.execute("""CREATE TABLE 'NASA Pictures'(
            image_path text,
            image_url text,
            image_size integer,
            image_sha256 text
            
        )
                
                
                """)
        
        db_path.commit() #save changes
        db_path.close()#close file
        
    return None
    

    
def add_image_to_db(db_path, image_path, image_size, image_sha256):
    """
    Adds a specified APOD image to the DB.

    :param db_path: Path of .db file
    :param image_path: Path of the image file saved locally
    :param image_size: Size of image in bytes
    :param image_sha256: SHA-256 of image
    :returns: None
    """
    
    
    
     #connect to the database and add the informations
     
    connect =sqlite3.connect(db_path) 
    c =connect.cursor()
    c.execute("INSERT INTO 'NASA Pictures'( image_path, image_url, image_size,image_sha256) VALUES ( ?,?,?,?)",(db_path,image_path,image_size,image_sha256))
    
    
    connect.commit()
    connect.close()
    return None

def image_already_in_db(db_path, image_sha256):
    """
    Determines whether the image in a response message is already present
    in the DB by comparing its SHA-256 to those in the DB.

    :param db_path: Path of .db file
    :param image_sha256: SHA-256 of image
    :returns: True if image is already in DB; False otherwise
    """ 
    
    #open a connecttion to an exisitng db file and select all sha items to check if its already in there.
    
    connect=sqlite3.connect(db_path)
    c =connect.cursor()
    c.execute("SELECT image_sha256 FROM 'NASA Pictures'")
    all_sha =c.fetchall()#will get the single sha compare
    #converts it to tuple to compare
    c.close()
    if (image_sha256,)in all_sha:
        
        return True
    
        
    else:
        
        return False
    
    
   
    


def set_desktop_background_image(background):
    """
    Changes the desktop wallpaper to a specific image.

    :param image_path: Path of image file
    :returns: None
    """
    
    ctypes.windll.user32.SystemParametersInfoW(20,0,background,3)
    
    
    return None



               
main()