'''
Created on 5 Jul. 2018

@author: Michael

Heavy inspiration form https://github.com/spulec/uncurl for uncurling.
'''
import requests
from requests_toolbelt.multipart import encoder
import shlex, re,json, os
import argparse
from collections import OrderedDict
from six.moves import http_cookies as Cookie
import xml.etree.ElementTree as ET

siteurl = 'https://cloudstor.aarnet.edu.au'

rootdir = '/plus/remote.php/webdav/Shared/Staging/UC-accented-Recordings/'

mimetype = {
            'txt':'text/plain',
            'csv':'text/csv',
            'avi':'video/x-msvideo',
            'json':'application/json',
            'mpeg':'video/mpeg',
            'oga':'audio/ogg',
            'ogv':'audio/ogg',
            'wav':'audio/wav',
            'xml':'application/xml',
            'raw16':'application/octet-stream',
            }

def remove_prefixes(string,prefixes):
    if isinstance(prefixes,str):
        if string.startswith(prefixes):
            return string[len(prefixes):]
    else:
        for p in prefixes:
            if string.startswith(p):
                string = string[len(p):]
    return string

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data')
    parser.add_argument('-b', '--data-binary', default=None)
    parser.add_argument('-X', default='')
    parser.add_argument('-H', '--header', action='append', default=[])
    parser.add_argument('--compressed', action='store_true')
    parser.add_argument('--insecure', action='store_true')

    with open("upload_curl.txt","r") as curlfile:
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

    #Upload file related stuff
    # ('Content-Disposition', 'attachment; filename="cloudstor-request-example.txt"')
    # ('Content-Length', '1831')
    # ('Content-Type', 'text/plain')

    #filename = 'test_upload_file.txt'
    #filedir = os.path.join(os.path.dirname(os.path.abspath( __file__ )),filename)
    dirs = []
    with open("dirs.txt","r") as directories:
        lines = directories.read().splitlines()
        for dir in lines:
            if not dir[-1]==os.sep:
                dirs.append(dir+os.sep)
            else:
                dirs.append(dir)

    too_large = []

    with open("files_to_upload.txt","r") as input_file:
        for file_path in iter(input_file.readline,b''):
            if file_path[-1]=="\n":
                file_path = file_path[:-1]
            size = os.stat(file_path).st_size
            if size > (4*1024*1024*1024):
                too_large.append(file_path)
                print("Skipping "+file_path)
                print("Due to Large Size: "+str(size))
            else:
                filedir, filename = os.path.split(file_path)
                modifiedpath = remove_prefixes(file_path,dirs).replace("\\","/")

                url = siteurl+rootdir+modifiedpath

                print("URL: "+url)

                quoted_headers['Content-Disposition'] = 'attachment; filename="%s"' % filename
                quoted_headers['Content-Length'] = str(os.stat(file_path).st_size)
                quoted_headers['Content-Type'] =  mimetype.get(os.path.splitext(filename)[1][1:],'application/octet-stream')

                with open(file_path,'rb') as to_upload:

                    #print("URL: "+str(url))
                    #print("Method: "+str(args.X))
                    #print("Cookie: "+str(cookie_dict))
                    #print("Headers: "+str(quoted_headers))
                    #print("Params: "+str(data))

                    print("Uploading File: "+filename)

                    response = requests.request(args.X,url,params=data,cookies=cookie_dict,headers=quoted_headers,files={'file':to_upload})

                    print(str(response))
                    print(str(response.text))
    with open("too_large.txt","w") as too_large_file:
        for item in too_large:
            too_large_file.write(item+"\n")

print("File Upload Complete.")
