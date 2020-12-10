#coding:utf-8
import os
import sys
import platform
import datetime
import time
import numpy as np

def creation_date(filePath):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    
    """
    if platform.system() == 'Windows':
        return os.path.getctime(filePath)
    else:
        stat = os.stat(filePath)
        return max(stat.st_mtime, max(stat.st_atime, stat.st_ctime))

def get_file_size(filename): ##kb
    fsize = os.path.getsize(filename)
    fsize = fsize / 1024.0
    return round(fsize, 2)

def make_dataset(dir, setSize=1024):  ##default k-size >= 1 MB
    files = []
    dir = os.path.expanduser(dir)
    for target in sorted(os.listdir(dir)):
        d = os.path.join(dir, target)
        if not os.path.isdir(d):
            continue

        for root, _, fnames in sorted(os.walk(d, followlinks=True)):
            for fname in sorted(fnames):
                path = os.path.join(root, fname)
                fileSize = get_file_size(path)
                if fileSize >= setSize:
                    files.append((path, fileSize))
    return files

def printf_top(dictMapKey, dictMap, info='size'):
    topN = min(10, len(dictMap))
    print('The top ' + str(topN) + ' files sorted with ' + info + ' are: ')
    #print(dictMapKey[:topN]) 
    for tupleInfo in dictMapKey[:topN]:
        if info == 'size': 
            print(str(tupleInfo[0]) + '\t' + str(tupleInfo[1]) + ' (MB)')
        else:
            print(str(tupleInfo[0]) + '\t' + str(tupleInfo[1]) + ' (day)')
    print('\t')
 
def printf_info(files):
    sizeMap = {}
    daysMap = {}
    print('There are ' + str(len(files)) + ' found...') 
    for fileP in files:
        sizeMap[fileP[0]] = float(fileP[1])
        daysMap[fileP[0]] = float(fileP[-1])
    
    sizeMapKey = sorted(sizeMap.items(), key=lambda x:x[1], reverse=True)
    daysMapKey = sorted(daysMap.items(), key=lambda x:x[1], reverse=True)
    
    printf_top(sizeMapKey, sizeMap, info='size')
    printf_top(daysMapKey, daysMap, info='days')
    
def read_dir(folderPath, setSize=1024, oldDays=10):  ## file-size >= 1 MB, 10 days not used
    #today = datetime.date.today()
    #print(today)
    t = time.time()
    files = make_dataset(folderPath, setSize=setSize)
    if len(files) == 0:
        print("invalid files...")
        return -1, None
    newFiles = []
    for fileP in files:
        mtime = creation_date(fileP[0])
        passTimeHour = (t - mtime) / 3600.0 / 24.0
        fileInfo = []
        fileInfo.extend(fileP)
        if passTimeHour >= oldDays:
            fileInfo.append(passTimeHour)
            newFiles.append(fileInfo)
    if len(newFiles) >= 1:
        printf_info(newFiles)
    return 0, newFiles

def clean_old_files(files):
    length = len(files)
    for index, fileP in enumerate(files):
        os.remove(fileP)
        print(fileP[0] + ' (' + str(index + 1) + '/' + str(length) + ') ' + ' is deleted.')
    print('')
    
if __name__ == '__main__':
    defaultSize = 1024
    defaultOldDays = 10
    while True:
        try:    
            folderName = raw_input("Please enter the name of your desired folder: ('q' for quit, 'a' for alter the default setting) ")
        except:
            folderName = input("Please enter the name of your desired folder:  ('q' for quit, 'a' for alter the default setting) ")
        
        if folderName == 'q':
            print('Thanks for your using..')
            break
        elif folderName == 'a':
            while True:
                try:
                    choice = raw_input("'s-number' for altering the file-size(MB), 't-number' for days not used (day), 'q' for quit: ")
                except:
                    choice = input("'s-number' for altering the file-size(MB), 't-number' for days not used (day), 'q' for quit: ")
                if choice == 'q':
                    break
                elif 's' in choice or 't' in choice:
                    digit = choice.split('-')[-1]
                    if digit.isdigit() == False:
                        print('invalid inputs.')
                    else:
                        changeS = int(digit)
                        if changeS < 0:
                            print('invalid inputs.')
                        if 's' in choice:
                            print('Yes, altering the file-size.')
                            defaultSize = changeS
                        else:
                            print('Yes, altering the days.')
                            defaultOldDays = changeS
                else:
                    print('invalid inputs.')
            print('filter file-size with ' + str(defaultSize) + '(MB) and the day filted with ' + str(defaultOldDays) + ' (day)')
            continue
        if os.path.exists(folderName) and os.path.isdir(folderName):
            print('Yes, the desired folder is exist.')
            returnCode, returnLists = read_dir(folderName, defaultSize, defaultOldDays)
            if returnCode == 0 and len(returnLists) >= 1:
                while True:
                    try:
                        choice = raw_input("Do you want to delete the files: ('q' for quit, 'y' for yes) ")
                    except:
                        choice = input("Do you want to delete the files: ('q' for quit, 'y' for yes) ")
                    if choice == 'q':
                        break
                    elif choice == 'y':
                        clean_old_files(returnLists)
                        break
                    else:
                        print('invalid inputs.') 
        else:
            print("Sorry, the desired folder does not exist.") 
