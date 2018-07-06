'''
Created on 5 Jul. 2018

@author: Michael
'''
import os,sys
import json

filelist = {}

auditdata = {}

filestoupload = []

test_files = ['E:\\UC-accented-D-final\\Spkr2_56_Session1\\Session1_1\\2_56_1_1_001.xml',
             'E:\\UC-accented-D-final\\Spkr2_56_Session1\\Session1_1\\2_56_1_1_001-ch1-maptask-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_56_Session1\\Session1_1\\2_56_1_1_001-ch2-boundary-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_56_Session1\\Session1_1\\2_56_1_1_001-ch3-strobe-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_56_Session1\\Session1_1\\2_56_1_1_001-ch4-c2Left-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_56_Session1\\Session1_1\\2_56_1_1_001-ch5-c2Right-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_56_Session1\\Session1_1\\2_56_1_1_001-ch6-speaker-yes.wav',
             
             'E:\\UC-accented-D-final\\Spkr2_218_Session4\\Session4_9\\2_218_4_1_002.xml',
             'E:\\UC-accented-D-final\\Spkr2_218_Session4\\Session4_9\\2_218_4_1_002-ch1-maptask-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_218_Session4\\Session4_9\\2_218_4_1_002-ch2-boundary-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_218_Session4\\Session4_9\\2_218_4_1_002-ch3-strobe-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_218_Session4\\Session4_9\\2_218_4_1_002-ch4-c2Left-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_218_Session4\\Session4_9\\2_218_4_1_002-ch5-c2Right-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_218_Session4\\Session4_9\\2_218_4_1_002-ch6-speaker-yes.wav',
             
             'E:\\UC-accented-D-final\\Spkr2_218_Session4\\Session4_9\\2_218_2_9_003.xml',
             'E:\\UC-accented-D-final\\Spkr2_218_Session4\\Session4_9\\2_218_2_9_003-ch1-maptask-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_218_Session4\\Session4_9\\2_218_2_9_003-ch2-boundary-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_218_Session4\\Session4_9\\2_218_2_9_003-ch3-strobe-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_218_Session4\\Session4_9\\2_218_2_9_003-ch4-c2Left-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_218_Session4\\Session4_9\\2_218_2_9_003-ch5-c2Right-yes.wav',
             'E:\\UC-accented-D-final\\Spkr2_218_Session4\\Session4_9\\2_218_2_9_003-ch6-speaker-yes.wav',
        ]

def lookup(fullpath):
    """ Checks to see if the file exists within the online files. It also checks for potential errors.
        Returns true if exists online, false otherwise.
    """
    path_components = os.path.split(fullpath)
    file_name, file_ext = os.path.splitext(path_components[-1])
    folder_bits = path_components[0].split(os.path.sep)
    component_folder = folder_bits[-1]
    session_folder = folder_bits[-2]
    
    file_name_bits = file_name.split('-',1)
    item_id = file_name_bits[0]
    channel = None
    if len(file_name_bits)>1:
        channel = file_name_bits[1]
    bits = item_id.split('_')
    if len(bits)>1:
        #indicates the file should be an item related file
        expected_component_folder = "Session"+bits[2]+"_"+bits[3]
        expected_session_folder = "Spkr"+bits[0]+"_"+bits[1]+"_"+"Session"+bits[2]
        
        if not item_id in auditdata:
            auditdata[item_id] = {'extcount':{},
                                  'channels':[],
                                  'valid_component_folder': component_folder==expected_component_folder,
                                  'valid_session_folder': session_folder==expected_session_folder,
                                 }
        
        if component_folder!=expected_component_folder or session_folder!=expected_session_folder:
            print("Expected Foldername Mismatch: "+item_id)
        
        auditdata[item_id]['extcount'][file_ext] = auditdata[item_id]['extcount'].get(file_ext,0)+1
        if channel:
            auditdata[item_id]['channels'].append(channel)
    
    filesize = os.stat(fullpath).st_size
    auditdata['totalSize'] = auditdata.get("totalSize",0)+filesize
    
    try:
        if filelist['dirs'][session_folder+'/'
                            ]['dirs'][session_folder+'/'+component_folder+'/'
                                      ]['files'][session_folder+'/'+component_folder+'/'+path_components[-1]]:
            auditdata['totalSizeToUpload'] = auditdata.get("totalSizeToUpload",0)+filesize
            return True
    except KeyError:
        pass
    return False

if __name__ == '__main__':
    
    folders = sys.argv[1:]
    
    print("Reading Existing File List...")
    
    #load files that already exist online
    with open("filelist.json","r") as fh:
        filelist = json.load(fh)
    
    print("Starting Folder Scan...")
    #scan files
    for folder in folders:
        print("Scanning Root "+folder+" ...")
        if os.path.exists(folder):
            for root, dirs, files in os.walk(folder):
                print("\t"+root)
                for file in files:
                    fullfile = os.path.join(root,file)
                    if not lookup(fullfile):
                        filestoupload.append(fullfile)
    
    print("Saving Files to Upload List...")
    with open("files_to_upload.txt","w") as output:
        for file in filestoupload:
            output.write(str(file)+'\n')
    
    print("Saving Audit Data...")
    with open("local-file-audit.json","w") as auditfile:
        json.dump(auditdata,auditfile)
    
    print("Scan Complete")
    
    
    