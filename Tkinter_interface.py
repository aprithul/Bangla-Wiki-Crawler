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
