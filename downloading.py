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

#function for writing new row to existing .csv file
#https://thispointer.com/python-how-to-append-a-new-row-to-an-existing-csv-file/

def append_list_as_row(file_name, list_of_elem):
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(list_of_elem)

def downloading_identifying_and_writing():
    global recent_datetime_name 
    global recent_datetime_name_str
    global comparison_datetime_name
    
    #defining dates and filenames
    os.chdir('/home/torka/wissArb_Projektarbeit/Image_Download_Copy')
    now = datetime.datetime.now()
    date_time_format = now.strftime("%Y%m%d%H%M")
    file=date_time_format+'.png'
    path=os.getcwd()
    process_flag = 0
    #open webcam website, take screenshot
    try:
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)
        driver.get('https://camera.deckchair.com/le-meridien-hamburg-germany')
        # Store the ID of the original window
        original_window = driver.current_window_handle

    	
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/dc-app/section/dc-camera-page/camera/div[1]/div[1]/div[1]/div[1]/ul")))
        print('button element located...')
    
        action = webdriver.ActionChains(driver)
    except:
        print('something went wrong in opening firefox... will try again next schedule')
        process_flag = 1
    try:
        element = driver.find_element(By.XPATH, "/html/body/dc-app/section/dc-camera-page/camera/div[1]/div[1]/div[1]/div[1]/ul")
        action.move_to_element(element).click().perform()
        
        #wait until til new tab is opened
        sleep(3)
        wait.until(EC.number_of_windows_to_be(2))
    
        # Loop through until we find a new window handle
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break
            
        driver.switch_to.window(driver.current_window_handle)
        #todo dont tkak   
        img = driver.find_element(By.XPATH, '/html/body/img')
        src = img.get_attribute('src')
        r = requests.get(src)
        with open(path +'/raw/'+file , 'wb') as outfile:
            outfile.write(r.content)
    
        #driver.get_screenshot_as_file(path+'/raw/'+file)
        print('image captured...')
    except:
        print('something went wrong in capturing... will try again next schedule')
        process_flag = 1
    sleep(1)
    # driver.implicitly_wait(20)
    try:
        driver.quit()
    except:
        print('no driver initialised.')
    #retrieve datetime from image (located at bottom left) - text analysis with easyocr
    if process_flag != 1:
        #crop image datetime signature located at bottom left
        im = Image.open(path+'/raw/'+file) 
        left = 10
        top = 1028
        right = 43
        bottom = 1045
        im_stamp = im.crop((left, top, right, bottom))
        
        #calculate brightness (in the night there are no boats (at least you cant see them..))
        brightness = ImageStat.Stat(im.convert('L'))
        brightness = brightness.mean[0]
        
        #read text with ocr tesseract (some preprocessing is necessary)
        #im_stamp = im_stamp.convert('L')
        #ret,im_stamp = cv2.threshold(np.array(im_stamp), 125, 255, cv2.THRESH_BINARY_INV)
        #im_stamp = cv2.resize(im_stamp, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        #rst = pytesseract.image_to_string(im_stamp, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789:')
        #print('first datetime detection: ',rst)
        
        #there are always 2 \n at the end of the detected string & delete spaced
        #rst = rst.replace('\n','')
        #rst = rst.replace(' ','')
        #rst_backup = rst
        #flag = 0
        #flag system: 0 - perfect, 1 - recording time used (results from strange behavior of ocr)
        
        #condition for textdetection seeing no text at all, use recording time in this case
        #if not rst:
        #    print('no text detected...')
        #    rst = file[8:12]
        #    flag = 1
        
        #condition for ':' being mistaken as '1'
        #if len(rst) == 5 and rst[2] == str(1):
        #    rst_list = list(rst)
        #    rst_list[2] = ':'
        #    rst = "".join(rst_list)
            
        
        #condition for text detection missing the : in the timeformat
        #if rst[2] != ':':
        #    rst = rst[0:2] + ':' + rst[-3:4]
            
        #if textdetection to datetime formatting fails from there we will just take the recording time 
        #print(rst)
        #try:
        #    time_obj = datetime.datetime.strptime(rst, '%H:%M ')
        #except:
        #    print('datetime formatting failure')
        #    rst = str(file[8:12])
        #    rst = rst[0:2] + ':' + rst[2:4]
        #    time_obj = datetime.datetime.strptime(rst, '%H:%M')
        #    flag = 1

        datetime_name = now
        datetime_name_str = datetime_name.strftime("%Y%m%d%H%M")
        
        #condition for text detection just being wrong (for example reading 17:__ as 11:__)
        #time diff will be larger than 5 minutes
        #if 'recent_datetime_name' in globals():
        #    k = 3 
        #else:
        #    recent_datetime_name=datetime_name
            
        #if 'comparison_datetime_name' in globals():
        #    comparison_datetime_name = recent_datetime_name
        #    ts = pd.Timestamp(comparison_datetime_name)
        #    ts = ts.floor(freq='5T')
        #    comparison_datetime_name = ts.to_pydatetime()
        #    comparison_datetime_name_str = comparison_datetime_name.strftime("%Y%m%d%H%M")  
        #    
        #    time_diff = abs(comparison_datetime_name - datetime_name)
        #    min5_diff = datetime.timedelta(minutes = 5)
        #    
        #    if time_diff > min5_diff:
        #        print('time diff larger 5')
        #        flag = 1
        #        rst = str(file[8:12])
        #        rst = rst[0:2] + ':' + rst[2:4]
        #        time_obj = datetime.datetime.strptime(rst, '%H:%M')
        #        datetime_name = datetime.datetime.combine(datetime.datetime.date(now), datetime.datetime.time(time_obj))
        #        datetime_name_str = datetime_name.strftime("%Y%m%d%H%M")
        #else:
        #    comparison_datetime_name = recent_datetime_name
        #    comparison_datetime_name_str='sometext'
            
        #print('final datetime: ',rst) 
    
        #condition for first run
        #if 'recent_datetime_name_str' in globals():
        #    k = 3 
        #else:
        #    recent_datetime_name_str='sometext'
    
    
        #if datetime_name_str == comparison_datetime_name_str or datetime_name_str == recent_datetime_name_str or brightness < 100:
        #    print("no new data avaiable/ it is nighttime, brightness: ", str(brightness))  
        #   os.remove(path+'/raw/'+ file)
        #else:
            #crop screenshot 
        left = 0
        top = 0
        right = 1920
        bottom = 1000
        im_proc = im.crop((left, top, right, bottom))
        proc_file = path+'/processed/' + datetime_name_str +'_crop.png'
        im_proc= im_proc.save(proc_file)
        
        #image analysis with yolov4
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
        csvdata = [datetime_name_str,boats,birds,brightness]
        append_list_as_row('webcam_data'+datetime_name.strftime("%Y%m%d")+'.csv', csvdata)
        print("image analysis finished & data is written to csv")
        os.remove(proc_file)
        
        #resize raw pictures for storage
        raw_resize = Image.open(path+'/raw/'+file)
        raw_resize = raw_resize.resize((1280,720))
        raw_resize.save(path+'/raw/'+file[:-4]+'_resize.png')
        os.remove(path+'/raw/'+file)
        
    #save datetime_name for comparison
    #print('recent datetme: ', recent_datetime_name_str)
    #print('comparison datetime: ', comparison_datetime_name_str)
        print('datetime: ', datetime_name_str)
    #print('________________________________')
    
    #recent_datetime_name_str = datetime_name_str
    #recent_datetime_name = datetime_name
        
schedule.every(2).minutes.do(downloading_identifying_and_writing)

while True:
    schedule.run_pending()
    sleep(1)
