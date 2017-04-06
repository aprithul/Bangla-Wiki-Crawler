import bs4 as bs
import urllib.request
import matplotlib.pyplot as plt
import queue
import hashlib
import codecs
from urllib.parse import urljoin
import sys
import threading
import sqlite3
from datetime import datetime, date

class node():
    def __init__(self, url, level):
        self.url = url
        self.level = level
    def get_url(self):
        return self.url
    def get_level(self):
        return self.level
    def set_level(self,value):
        self.level = value

run_lock = threading.Lock()

is_active = False
is_quit = False
url_hashs = dict()
vowels = { 'অ': 0, 'আ' : 0, 'ই' : 0, 'ঈ' : 0, 'উ' : 0, 'ঊ' : 0, 'ঋ' : 0, 'এ' : 0, 'ঐ' : 0, 'ও' : 0, 'ঔ' : 0 } 
consonants = {'ক' : 0, 'খ' : 0, 'গ' : 0, 'ঘ' : 0, 'ঙ' : 0,
                'চ' : 0, 'ছ' : 0, 'জ' : 0, 'ঝ' : 0, 'ঞ': 0,
                'ট' : 0, 'ঠ' : 0,  'ড' : 0,  'ঢ' : 0, 'ণ' : 0,
                'ত' : 0, 'থ' : 0, 'দ' : 0, 'ধ' : 0, 'ন' : 0,
                'প' : 0, 'ফ' : 0, 'ব' : 0, 'ভ' : 0, 'ম' : 0,
                'য' : 0, 'র' : 0, 'ল': 0, 'শ' : 0, 'ষ' : 0,
                'স' : 0, 'হ' : 0, 'ৎ': 0, 'ড়' : 0, 'ঢ়' : 0,
                'য়' : 0, 'ং' : 0, 'ঃ' : 0}
crawl_queue = queue.Queue()
ignored_extensions = [ ".jpg", ".png", ".gif", ".tif", ".bmp", ".raw", ".pdf", ".svg" ]
u_nw = chr(0x000d)
base_url = "https://bn.wikipedia.org"

def add_starting_url(href, level,):
    global crawl_queue
    crawl_queue.put(node(href,level))
    
def set_is_active(value):
    global is_active
    run_lock.acquire()
    is_active = value
    run_lock.release()


def do_quit():
    global is_quit

    is_quit = True
    # do saving here

def special_case(c, nc):
    if c=='ড' and nc=='়':
        consonants['ড়'] += 1
        return True
    elif c=='য' and nc=='়':
        consonants['য়'] += 1
        return True
    elif c=='ঢ' and nc=='়':
        consonants['ঢ়'] += 1
        return True
    else:
        return False


def calculate_frequency(text):
    global vowels
    global consonants
    text_len = len(text)
    for i in range(1,text_len):
        c = text[i-1]
        nc = text[i]
        if c in vowels:
            vowels[c] += 1
        elif c in consonants:
            if  not special_case(c, nc):
                consonants[c] += 1
            
def save_frequency(connection):
    cursor = connection.cursor()
    for key, value in vowels.items():
        cursor.execute("update alphabet set count=count+? where character=?", [value,key])
        vowels[key] = 0
    for key, value in consonants.items():
        cursor.execute("update alphabet set count=count+? where character=?", [value,key])
        consonants[key] = 0
    connection.commit()

'''
    # clear file
    open('frequency.txt', 'w').close()

    # rewrite result
    result = codecs.open("frequency.txt", "a", "utf-8")
    for key, value in vowels.items():
        print(str(key)+"  "+ str(value))
        result.write(str(key)+"  "+ str(value)+str(u_nw)+'\n')
    result.write("-----------------------------------------------------------------\n"+str(u_nw)+'\n')
    print("-----------------------------------")
    for key, value in consonants.items():
        print(str(key)+"  "+ str(value))
        result.write(str(key)+"  "+ str(value)+str(u_nw)+'\n')
    result.close()
'''

def show_bar_plot(dictionary):
    plt.bar(range(len(dictionary)), dictionary.values(), align='center')
    plt.xticks(range(len(dictionary)), dictionary.keys())
    plt.show()

def process_links(links, level):
    global url_hashs

    if level==0:
        return
    
    # for each href
    for link in links:
        # if href is to a a bangla wiki page
        href = link.get('href')
        if "/wiki/" == href[:6] and href[-4:] not in ignored_extensions:
            href = urljoin(base_url, href)
            hashed_obj = hashlib.md5(href.encode())
            hash_digest = hashed_obj.hexdigest()
            if hash_digest not in url_hashs:
                url_hashs[hash_digest] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                crawl_queue.put( node( href , level))
        



def connect_to_db(db_name):
    connection = sqlite3.connect(db_name)
    return connection

def close_connection(connection):
    try:
        connection.commit()
        connection.close()
        return True
    except:
        return False

def save_url_hashs(connection, url_hashs):
    cursor = connection.cursor()
    for key,value in url_hashs.items():
        cursor.execute("insert or ignore into history (digest,time) values (?,?)", [ key, value ] )

def prepare_url_hashs(connection,url_hashs):
    cursor = connection.cursor()
    digests = cursor.execute("select * from history order by time desc limit 1000000").fetchall()
    for h in digests:
        url_hashs[h[0]] = h[1]
    
# so that next run can resume
def save_queue_remainder(connection, my_queue):
    cursor = connection.cursor()
    # remove all previously stored urls
    cursor.execute("delete from queue_remainder")
    # add all urls from my_queue to db
    while not my_queue.empty():
        n = my_queue.get()
        cursor.execute("insert into queue_remainder (url, level) values (?, ?)",[n.get_url(), n.get_level()])

# restore previous state of queue
def prepare_queue(connection, my_queue):
    cursor = connection.cursor()
    # get all previously stored urls
    nodes = cursor.execute("select * from queue_remainder")
    for n in nodes:
        my_queue.put(node(n[0], n[1] ))
    

def main():
    global is_active
    global url_hashs
    global crawl_queue
    
    # connect to sqlite3 db
    connection = connect_to_db( "bangla_dictionary.db")
    # prepare url_hash dictionary
    prepare_url_hashs(connection, url_hashs)
    # prepare crawl_queue
    prepare_queue(connection, crawl_queue)
    
    links_visited = 0
    is_active = True

    # start crawling while not quit and has at least one node to visit
    while not is_quit and not crawl_queue.empty():
        # crawling is paused so continue to next cycle
        if not is_active:
            continue
        else:
            # get the first node
            cur_node = crawl_queue.get()
            # get its url
            my_url = cur_node.get_url()

            try:
                # prepare webpage
                sauce = urllib.request.urlopen(my_url).read()     
                soup = bs.BeautifulSoup(sauce,'lxml')
                # show page title after every calculation
                # print(soup.title.string)
            except:
                print("problem pasing page: "+ str(soup.title))
                continue
            
            # get div named bodyContent
            body = soup.find("div", {"id" : "bodyContent"})
            # get all links and..
            links = body.find_all('a')
            # hash them, if doesn't exist in table, add to queue
            process_links(links, cur_node.get_level()-1)

            # get all paras
            paras = body.find_all('p')
            # analyze each para and find frequency
            for p in paras:
                bangla_string = p.text
                calculate_frequency(bangla_string)

            # so that sudden error doesn't cause big data loss, we save data every 50 links visited
            links_visited += 1
            if links_visited % 50 == 0:
                save_frequency(connection)
                print("saved: "+str(links_visited)+ " links visited") 

    # exiting so save frequency data
    save_frequency(connection)
    # save urls visited
    save_url_hashs(connection, url_hashs)
    # save remaining queue nodes
    save_queue_remainder(connection, crawl_queue)
    
    if close_connection(connection):
        print("end")
    else:
        print("error closing db connection")
    
    #quit()
    #show_bar_plot(consonants)



def alternate():
    print(ord('ঢ়'))
    #print (chr(0x09dc))
    
if __name__=="__main__":
    main()
    #alternate()
