'''
Created on 3 Jul. 2018

@author: Michael

Heavy inspiration form https://github.com/spulec/uncurl for uncurling. 
'''
import requests
import shlex, re,json
import argparse
from collections import OrderedDict
from six.moves import http_cookies as Cookie
import xml.etree.ElementTree as ET

siteurl = 'https://cloudstor.aarnet.edu.au'

rootdir = '/plus/remote.php/webdav/Shared/Staging/UC-accented-Recordings/'

def xml_to_dict(root):
    if root.text:
        return {root.tag:root.text}
    d = {root.tag:{}}
    for child in root:
        if child.tag in d[root.tag]:
            #need to convert dict to list
            if not isinstance(d[root.tag][child.tag],list):
                d[root.tag][child.tag] = [d[root.tag][child.tag]]
            d[root.tag][child.tag].append(xml_to_dict(child))
        else:
            d[root.tag].update(xml_to_dict(child))
    return d

def scan_dir(url,method,**kwargs):
    response = requests.request(method,url,**kwargs)
    
    print(url)
    try:
        modified_resp = response.text.replace("d:","")
        
        root = ET.fromstring(modified_resp)
        
        dirpath = url[len(siteurl):]
        dirs = {}
        files = {}
        
        for resp_item in root:        
            resp_dict = xml_to_dict(resp_item)['response']
            
            if resp_dict.get('propstat',{}).get('prop',{}).get('resourcetype',{}).get('collection',None) is None:
                files[resp_dict['href']] = resp_dict
            else:
                dirs[resp_dict['href']] = resp_dict
    except:
        print(response.text)
        raise
            
    return dirpath,dirs,files
            
def print_all_files(rooturl,method,fd,**kwargs):
    dirpath,dirs,files = scan_dir(rooturl,method,**kwargs)
    for file in files.keys():
        fd.write(str(file)+'\n')
    for dir in dirs.keys():
        if not dir==dirpath:
            print_all_files(siteurl+dir,method,fd,**kwargs)
    
def all_files_with_dir_structure(rooturl,method,**kwargs):
    dirpath,dirs,files = scan_dir(rooturl,method,**kwargs)
    dir = {'files':{},'dirs':{}}
    for file,stats in files.items():
        dir['files'][file.replace(rootdir,"")] = {'type':stats['propstat']['prop']['getcontenttype'],
                              'size':stats['propstat']['prop']['getcontentlength'],
                              }
    for directory in dirs.keys():
        if not directory==dirpath:
            dir['dirs'][directory.replace(rootdir,"")] = all_files_with_dir_structure(siteurl+directory,method,**kwargs)
    return dir

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data')
    parser.add_argument('-b', '--data-binary', default=None)
    parser.add_argument('-X', default='')
    parser.add_argument('-H', '--header', action='append', default=[])
    parser.add_argument('--compressed', action='store_true')
    parser.add_argument('--insecure', action='store_true')

    with open("browse_curl.txt","r") as curlfile:
        curl = curlfile.read()
        curl = curl[curl.find('-X'):]
        
        print(curl+"\n")
        
        splitcurl = shlex.split(curl)
        args = parser.parse_args(splitcurl)
        
        print(args)
        
    cookie_dict = OrderedDict()
    quoted_headers = OrderedDict()
    
    data = args.data or args.data_binary
    
    
    for curl_header in args.header:
        if curl_header.startswith(':'):
            occurrence = [m.start() for m in re.finditer(':', curl_header)]
            header_key, header_value = curl_header[:occurrence[1]], curl_header[occurrence[1] + 1:]
        else:
            header_key, header_value = curl_header.split(":", 1)

        if header_key.lower() == 'cookie':
            cookie = Cookie.SimpleCookie(header_value)
            for key in cookie:
                cookie_dict[key] = cookie[key].value
        else:
            quoted_headers[header_key] = header_value.strip()
    
    url = siteurl+rootdir
    
    print("URL: "+str(url))
    
    print("Generating File List...\n")
    
    with open("filelist.txt","w") as output:
        json.dump(all_files_with_dir_structure(url,args.X,params=data,cookies=cookie_dict,headers=quoted_headers),output)
    
    print("File List Complete.")
    
    
    
    
