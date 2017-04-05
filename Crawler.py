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
ignored_extensions = [ ".jpg", ".png", ".gif", ".tif", ".bmp", ".raw", ".pdf" ]
u_nw = chr(0x000d)
base_url = "https://bn.wikipedia.org"

def add_starting_url(href):
    crawl_queue.put(href)
    
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
            
def print_frequency(connection):
    cursor = connection.cursor()
    for key, value in vowels.items():
        #increments count. must save state of search on exit
        cursor.execute("update alphabet set count=count+? where character=?", [value,key])
    for key, value in consonants.items():
        cursor.execute("update alphabet set count=count+? where character=?", [value,key])

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
                url_hashs[hash_digest] = 1
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
        

def main():
    global is_active

    # connect to sqlite3 db
    connection = connect_to_db( "bangla_dictionary.db")
    
    # setup initial node
    my_url = "https://bn.wikipedia.org/wiki/%E0%A6%86%E0%A6%87%E0%A6%9C%E0%A6%BE%E0%A6%95_%E0%A6%A8%E0%A6%BF%E0%A6%89%E0%A6%9F%E0%A6%A8"
    # my_url = "https://bn.wikipedia.org/wiki/%E0%A6%A2%E0%A6%BE%E0%A6%95%E0%A6%BE"
    start_node = node(my_url,2)
    crawl_queue.put(start_node)
    links_visited = 0
    is_active = True
        
    # start of dfs
    
    while not is_quit and not crawl_queue.empty():
        # crawling is paused so continue to next cycle
        if not is_active:
            continue
        else:
            # get the first node
            cur_node = crawl_queue.get()
            # get its url
            my_url = cur_node.get_url()
            # prepare webpage
            sauce = urllib.request.urlopen(my_url).read()     
            soup = bs.BeautifulSoup(sauce,'lxml')
            # show page title after every calculation
            print(soup.title.string)
            
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


    print_frequency(connection)
    
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
