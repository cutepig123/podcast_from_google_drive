from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


service = build('drive', 'v3')

def makeGDriveLink(id):
    #return 'https://drive.google.com/file/d/{}/view?usp=sharing'.format(id)
    return 'http://docs.google.com/uc?id={}'.format(id)
 
class RssMaker:
    def __init__(self):
        self.rss = []
        
    def add(self,title, mp3link):
        self.rss.append([title, mp3link])
        
    def save(self,title):
        if len(self.rss)==0: return
        
        print('>>save to', title)
        
        # title, items
        rssTmpl = open('podcast.xml.template','r', encoding='utf-8').read()
        # title, url
        itemTmpl = open('podcast.xml.node.template','r', encoding='utf-8').read()
        
        def makeRssXmlNode(title, mp3link):
            return itemTmpl.replace('$title', title).replace('$url', mp3link)
            
        def makeRssXmlNodes():
            nodes=[]
            for t in self.rss:
                nodes.append(makeRssXmlNode(t[0], (t[1])))
            return ''.join(nodes)
        
        content = rssTmpl.replace('$title', title).replace('$items', makeRssXmlNodes())
        open('podcast{}.xml'.format(title),'w', encoding='utf-8').write(content)
    
def list_folder_recur(folder_id, folder_name):
    
    q = "'{}' in parents".format(folder_id)
    print(q)
    results = service.files().list(supportsAllDrives=True, includeItemsFromAllDrives=True, q=q, fields = "nextPageToken, files(id, name, mimeType)").execute()	

    #print(results)
    #print(len(results)==1)
    #print(len(results['files']))
    
    rss = RssMaker()
    for file in results['files']:
        name = file['name']
        id = file['id']
        full_name = "{}.{}".format(folder_name, name)
        if 'folder' in file['mimeType']:
            list_folder_recur(id, full_name)
        else:
            print(id, full_name)
            if '.mp3' in file['name']:
                rss.add(name, makeGDriveLink(id))
            elif '.mp4' in file['name']:
                rss.add(name + '-mp4', makeGDriveLink(id))
    rss.save(folder_name)

        
def test3():
    folder_jiake={'id':'148cr7xvj8A5PjhGCy2m7pcYiR5Dc51RA','name':''}
    folder_jq_1={'id':'149nXPcIIeAWjpjNR1koyoz15mnRBxnfd','name':''}
    list_folder_recur(folder_jiake['id'], folder_jiake['name'])
        
        
class OpmlMaker:
    def __init__(self):
        self.rss = []
        
    def add(self,title, link):
        self.rss.append([title, link])
        
    def save(self,title):
        if len(self.rss)==0: return
        
        print('>>save to', title)
        
        # items
        rssTmpl = open('opml.template','r', encoding='utf-8').read()
        # title, url
        itemTmpl = open('opml.item.template','r', encoding='utf-8').read()
        
        def makeRssXmlNode(title, link):
            return itemTmpl.replace('$title', title).replace('$url', link)
            
        def makeRssXmlNodes():
            nodes=[]
            for t in self.rss:
                nodes.append(makeRssXmlNode(t[0], (t[1])))
            return ''.join(nodes)
        
        content = rssTmpl.replace('$title', title).replace('$items', makeRssXmlNodes())
        open('opml{}.opml'.format(title),'w', encoding='utf-8').write(content)
       
def opml_from_current_dir():
    import urllib.parse
    opml = OpmlMaker()
    for f in os.listdir('.'):
        if f.endswith('.xml'):
            url = 'http://192.168.1.112:8080/{}'.format(urllib.parse.quote(f))
            opml.add(f, url)
    opml.save('result')
    
if __name__ == '__main__':
    test3()
    opml_from_current_dir()