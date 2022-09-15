#%%
#einzelne Bilder herunterladen



from selenium import webdriver
from time import sleep
import os 
import datetime
from PIL import Image, ImageStat
import schedule
import subprocess
from csv import writer
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

import urllib
import requests
import pytesseract
import cv2
import numpy as np
import pandas as pd

def append_list_as_row(file_name, list_of_elem):
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(list_of_elem)

datelist=[]
path = '/home/torka/wissArb_Projektarbeit/Image_Download_Copy/timelapses'
dt = datetime.datetime(2022,8,1,6,5,0)
date_str = '20220801'
delta = datetime.timedelta(minutes=5)
for i in range(0,288):
    datelist.append(dt + i*delta)


driver = webdriver.Firefox()
driver.maximize_window()
wait = WebDriverWait(driver, 10)
driver.get('https://camera.deckchair.com/le-meridien-hamburg-germany/v/62e9a7b9d66b8b00090592db')
# Store the ID of the original window
original_window = driver.current_window_handle

for i in range(1,285):
    width = 63.45
    x_off_chunks = width / 10
    current_dt = datelist[i-1]
    current_dt_str = datetime.datetime.strftime(current_dt,"%Y%m%d%H%M")
    file = current_dt_str + '.png'
    

    element_xpath = "/html/body/dc-app/section/dc-camera-page/camera/div[1]/div[2]/div[1]/camera-timeline/div/ol[1]/li[1]"
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, element_xpath)))
    print('first container element located...')
    action = webdriver.ActionChains(driver)
    element = driver.find_element(By.XPATH, element_xpath)


    x_off = (i-1) * x_off_chunks
    action.move_to_element_with_offset(element,x_off,0).click().perform()
    sleep(1)

    save_xpath='/html/body/dc-app/section/dc-camera-page/camera/div[1]/div[1]/div[1]/div[1]/ul/li/a'
    save_action = webdriver.ActionChains(driver)
    save_element = driver.find_element(By.XPATH, save_xpath)
    save_action.move_to_element(save_element).click().perform()
    
    wait.until(EC.number_of_windows_to_be(2))

    # Loop through until we find a new window handle
    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            break
        
    driver.switch_to.window(driver.current_window_handle)
    sleep(2)
    try:
        img = driver.find_element(By.XPATH, '/html/body/img')
        src = img.get_attribute('src')
        r = requests.get(src)
        with open(path + '/raw/' + file, 'wb') as outfile:
            outfile.write(r.content)

        #driver.get_screenshot_as_file(path+'/raw/'+file)
        print('image captured...')
    except:
        print('image not captured...')
    driver.close()
    driver.switch_to.window(original_window)
    try:
        im = Image.open(path+'/raw/'+file) 
        left = 0
        top = 0
        right = 1920
        bottom = 1000
        im_proc = im.crop((left, top, right, bottom))
        proc_file = path+'/processed/' + current_dt_str +'_crop.png'
        im_proc= im_proc.save(proc_file)
        #calculate brightness (in the night there are no boats (at least you cant see them..))
        brightness = ImageStat.Stat(im.convert('L'))
        brightness = brightness.mean[0]

        darknet_path = '/home/torka/darknet'
        os.chdir(darknet_path)
        result = subprocess.check_output('./darknet detect cfg/yolov3.cfg yolov3.weights ' + proc_file + ' -thresh 0.2',shell=True,text=True)
        result = result.splitlines()
        boats = 0
        birds = 0
        #check if object is boat
        for i in range(0,len(result)):
            result_element = str(result[i][0:4])
            if result_element == 'boat':
                boats +=1 
            elif result_element == 'bird':
                birds += 1
        print('detected boats: ', boats, ', detected birds: ', birds)
        print('image brightness: ', str(brightness))
        
        #writing to csv file
        os.chdir('/home/torka/wissArb_Projektarbeit/Image_Download_Copy')
        csvdata = [current_dt_str,boats,birds,brightness]
        append_list_as_row('webcam_data'+date_str+'.csv', csvdata)
        print("image analysis finished & data is written to csv")
        os.remove(proc_file)
        
        #resize raw pictures for storage
        raw_resize = Image.open(path+'/raw/'+file)
        raw_resize = raw_resize.resize((1280,720))
        raw_resize.save(path+'/raw/'+file[:-4]+'_resize.png')
        os.remove(path+'/raw/'+file)#
    except:
        print('Folgefehler, da kein bild aufgenommen')
