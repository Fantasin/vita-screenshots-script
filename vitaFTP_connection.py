import ftplib
from pathlib import Path
import re, json

#td = Path(r'C:\\Users\\user\\Desktop\\JP Screenshots\\PSVITA\\CompiledScreenshots') #target directory as a path object
rd = Path(r'C:\\Users\\user\\Desktop\\JP Screenshots\\PSVITA\\ReviewedScreenshots') #reviewed directory as a path object
fileSaveDir = Path(r'C:\\Users\\user\\Desktop\\JP Screenshots\\PSVITA\\FTPTEST') #directory for saving screenshots
jsonFilePath = Path(r'C:\\Users\\user\\Desktop\\JP Screenshots\\PSVITA\\file_list.json')

ftp_vita = 'YOUR_LOCAL_IP_ADDRESS' 
ftp_port = 'YOUR_LOCAL_PORT'
ftp_twd = 'ux0:picture/SCREENSHOT' #target directory for screenshots on vita
ftp_ps1_twd = 'ux0:picture/ALL' #target directory for ps1 screenshots

#block for establishing FTP connection
ftp = ftplib.FTP()
ftp.connect(host = ftp_vita, port = ftp_port)
ftp.login()
print(f'FTP Connection established successfully')

dir_list = [] #list of files/directories
upd_screenshots_list = [] #list of updated screenshots after download

fileRe_pattern = r'\d{4}-\d{2}-\d{2}-\d{6}\.png$' #main search pattern
ps1_re_pattern = r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.png$' #ps1 search pattern

def getLocalScreenshotsJson(path_to_json_file, screenshots_dir):
    if path_to_json_file.exists():
        with open(path_to_json_file, 'r') as json_file:
            json_list = json.load(json_file)
            return json_list
    else:
        local_files = [file.name for file in screenshots_dir.rglob('*.png') if file.is_file()] #list for storing names of currently saved screenshots

        with open(path_to_json_file, 'w') as json_file:
            json.dump(local_files, json_file)
            return local_files

def fileNamesInDir(re_pattern):
    name_list = [] #list for names to return after executing function

    #take a list of entities in dir-> for each entity check if match exists and return matched string (file[0]) else do nothing
    ftp.retrlines("LIST", lambda file:name_list.append(re.search(re_pattern, file)[0]) if re.search(re_pattern, file) else None) 

    return name_list #return name_list as a list

def downloadFilesFTP(files_in_dir, local_screenshots): #download files to local directory
    for file_name in files_in_dir:
        localFilePath = fileSaveDir / file_name #make a full local path with target directory and vita file_name
        if file_name in local_screenshots:
            print(f'File {file_name} already exists in local directory. Skipping to the next file')
        else:
            with open(localFilePath, 'wb') as f: #open file in local Path
                ftp.retrbinary(f"RETR {file_name}", f.write)
            print(f'Saved file {file_name} to    {localFilePath}')
            upd_screenshots_list.append(file_name)
            print('Screenshot list updated')

def updateLocalScreenshotListJson(path_to_json_file, upd_screenshots): #path to file and list of new added files for directory
    if path_to_json_file.exists():
        with open(path_to_json_file, 'r+') as json_file: #open for reading and writing to avoid double opening
            json_list = json.load(json_file)
            #add new files to a list    
            new_entries = [file for file in upd_screenshots if file not in json_list] #add new entries to a list
            json_list.extend(new_entries) #extend json list with new entries

            json_file.seek(0) #move file pointer to the beginning of the file to overwrite data
            json.dump(json_list, json_file) #write updated json to a file
            print(f'Added {len(upd_screenshots)} to local screenshots json') #FIGURE OUT A WAY TO UPDATE THE NUMBER CORRECTLY
            print(f'Number of entries in a screenshots file {len(json_list)}')
    else:
        print('Local json file does not exists. Skipping running update..')

def processDirectory(base_dir, re_pattern):
    ftp.cwd(base_dir) #navigate to base screenshot directory on vita
    ftp.retrlines("LIST", lambda line: dir_list.append(line[-2:])) #get directory names in base SCREENSHOTS DIRECTORY

    for dir in dir_list: #ADD PS1 SCREENSHOTS TO A MAIN SCRIPT. MAKE IT A METHOD?
        ftp.cwd(dir) #go to directory

        file_names = fileNamesInDir(re_pattern) #return file names for further use for downloading
        local_screenshots_list = getLocalScreenshotsJson(jsonFilePath, rd)
        downloadFilesFTP(file_names, local_screenshots_list) #download files in local dir

        ftp.cwd('..') #return up one directory
        print('Returned to directory:  ' + ftp.pwd())

    updateLocalScreenshotListJson(jsonFilePath, upd_screenshots_list) #update JSON file with added screenshots

processDirectory(ftp_twd, fileRe_pattern) #main script
#processDirectory(ftp_ps1_twd, ps1_re_pattern) #script for ps1 screenshots

ftp.quit()
print('FTP connection closed')



