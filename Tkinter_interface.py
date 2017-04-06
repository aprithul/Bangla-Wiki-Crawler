from tkinter import *  ## notice lowercase 't' in tkinter here
from tkinter.ttk import *
from tkinter import messagebox
import Crawler
import threading
import MySQLdb

class myThread (threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
   def run(self):
       print("run")
       Crawler.main()
       return

def stop_crawler():
        Crawler.set_is_active(False)

def add_initial_nodes():
      # setup initial nodes    
       Crawler.add_starting_url("https://bn.wikipedia.org/wiki/%E0%A6%86%E0%A6%87%E0%A6%9C%E0%A6%BE%E0%A6%95_%E0%A6%A8%E0%A6%BF%E0%A6%89%E0%A6%9F%E0%A6%A8", 3)
       Crawler.add_starting_url("https://bn.wikipedia.org/wiki/%E0%A6%AC%E0%A6%BE%E0%A6%82%E0%A6%B2%E0%A6%BE%E0%A6%A6%E0%A7%87%E0%A6%B6", 3)
       Crawler.add_starting_url("https://bn.wikipedia.org/wiki/%E0%A6%B0%E0%A6%AC%E0%A7%80%E0%A6%A8%E0%A7%8D%E0%A6%A6%E0%A7%8D%E0%A6%B0%E0%A6%A8%E0%A6%BE%E0%A6%A5_%E0%A6%A0%E0%A6%BE%E0%A6%95%E0%A7%81%E0%A6%B0", 3)
      

crawler_created = False
def start_crawler():
    global crawler_created
    
    if not crawler_created:
        t = myThread(1, "Crawler", 1 ).start()
        crawler_created = True
    else:
        Crawler.set_is_active(True)

# Tniker code
class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent        
        self.initUI()
        
    def initUI(self):
        self.parent.title("Quit button")
        self.style = Style()    
        self.style.theme_use("default")

        self.pack(fill=BOTH, expand=1)
        startButton = Button(self, text="Start",
            command=start_crawler)
        startButton.place(x=50, y=50)
        
        stopButton = Button(self, text="Stop",
            command=stop_crawler)
        stopButton.place(x=150, y=50)

        addNode = Button(self, text="Add Nodes",
            command=add_initial_nodes)
        addNode.place(x=100, y=100)
        
root = Tk()

def on_closing():
    global root

    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        Crawler.do_quit()
        root.destroy()

def main():
    global root
    
    root.geometry("250x150+300+300")
    app = Example(root)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
    


if __name__ == '__main__':
    main()
