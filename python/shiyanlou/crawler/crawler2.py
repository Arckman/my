'''
事件驱动爬虫,selectors module
'''
import selectors
import re
import socket
import urllib.parse
import time

urls_todo=set(['/'])
seen_urls=set(['/'])
target=('localhost',7002)
concurrency_achieved=0
selector=selectors.DefaultSelector()
stopped=False

class Fetcher:
    def __init__(self,url):
        self.response=b''
        self.url=url
        self.sock=None
    
    def fetch(self):
        global concurrency_achieved
        concurrency_achieved=max(concurrency_achieved,len(urls_todo))
        self.sock=socket.socket()
        self.sock.setblocking(False)
        try:
            self.sock.connect(target)
        except BlockingIOError:
            pass
        selector.register(self.sock.fileno(),selectors.EVENT_WRITE,self.connected)

    def connected(self,key,mask):
        selector.unregister(key.fd)
        get='GET {} HTTP/1.0\r\nHost: localhost\r\n\r\n'.format(self.url)
        self.sock.send(get.encode('ascii'))
        selector.register(key.fd,selectors.EVENT_READ,self.read_response)

    def read_response(self,key,mask):
        global stopped
        chunk=self.sock.recv(4096)
        if chunk:
            self.response+=chunk
        else:
            selector.unregister(key.fd)
            links=self.parse_links()
            for link in links.difference(seen_urls):
                urls_todo.add(link)
                Fetcher(link).fetch()
            seen_urls.update(links)
            urls_todo.remove(self.url)
            if not urls_todo:
                stopped=True
            print(self.url)

    def body(self):
        body=self.response.split(b'\r\n\r\n',1)[1]
        return body.decode('utf-8')

    def parse_links(self):
        if not self.response:
            print('error {}'.format(self.url))
            return set()
        if not self._is_html():
            return set()
        urls=set(re.findall(r'''(?i)href=["']?([^\s"'<>]+)''',self.body()))
        links=set()
        for url in urls:
            normalized=urllib.parse.urljoin(self.url,url)
            parts=urllib.parse.urlparse(normalized)
            if parts.scheme not in ('','http','https'):
                continue
            host,port=urllib.parse.splitport(parts.netloc)     
            if host and host.lower() not in (target[0]):
                continue
            defragmented,frag=urllib.parse.urldefrag(parts.path)
            links.add(defragmented)
        return links
    
    def _is_html(self):
        head,body=self.response.split(b'\r\n\r\n',1)
        headers=dict(h.split(': ') for h in head.decode().split('\r\n')[1:])
        return headers.get('Content-Type','').startswith('text/html')

start=time.time()
fetcher=Fetcher('/')
fetcher.fetch()

while not stopped:
    events=selector.select()
    for event_key,event_mask in events:
        callback=event_key.data
        callback(event_key,event_mask)

print('{} URLs fetched in {:.1f} seconds, achieved concurrency={}'.format(len(seen_urls),time.time()-start,concurrency_achieved))


            
