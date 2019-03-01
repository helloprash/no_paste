import base64
from pathlib import Path
import os, inspect 
import re
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.ttk import * 
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import font
import queue as Queue
import threading
from selenium import webdriver
import urllib
from urllib.request import urlopen
from subprocess import Popen
import socket
#from pywinauto import clipboard
import complaint_handler
import Images

current_folder = os.getcwd()


class ComplaintHandlerUI(tk.Tk):
    def __init__(self, queue, userNameQueue, clicked, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.queue = queue
        self.userNameQueue = userNameQueue

        self.geometry("468x460")
        self.resizable(width=False, height=False)
        self.title("CATSWeb Automation Tool")

        icondata= base64.b64decode(Images.Jnj32icon)
        tempFile= "icon.ico"
        iconfile= open(tempFile,"wb")
        iconfile.write(icondata)
        iconfile.close()
        self.wm_iconbitmap(tempFile)
        os.remove(tempFile)

        self.configure(background="#FFFFFF")

        container = Frame(self)

        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (LoginPage, PageOne):
            frame = F(container, self, clicked)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.configure(background="#FFFFFF")

        self.show_frame(LoginPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def get_page(self, page_class):
        return self.frames[page_class]


class LoginPage(tk.Frame):
    def __init__(self, parent, controller, clicked):
        tk.Frame.__init__(self, parent)

        self.running = 1
        self.queue = controller.queue
        self.userNameQueue = controller.userNameQueue
        self.flagQueue = Queue.Queue()
        self.controller = controller
        self.clicked = clicked
        self.LinkBind = None

        style = Style()
        #style.configure("BW.TLabel", font = ('Helvetica','10'),foreground="#64B23B")
        #style.configure("BW.TButton", font = ('Helvetica','10'), foreground="#64B23B", background="#FFFFFF")
        style.configure("BW.TEntry", background = "gray90")

        #imgFile = '\\\\'.join(os.path.join(current_folder,"jnj.gif").split('\\'))
        large_font = ('Verdana',17)

        img = tk.PhotoImage(data=Images.jnjGIF)      
        self.logo = Label(self, image=img)
        self.logo.image = img

        self.Link = Entry(self,style="BW.TEntry", font=large_font,foreground = 'grey')
        self.Link.insert(0, 'Insert link here')
        self.Link.bind('<FocusIn>', self.on_Userentry_click)
        self.Link.bind('<FocusOut>', self.on_Userfocusout)

        self.loginStatusMsg = Label(self, text='', font = ('Helvetica','10'), foreground="black", background="#FFFFFF")

        
        self.message = Label(self, text="Please copy your CATSWeb logged in url:")
        self.message.config(font = ('Helvetica','12'), foreground="#638213", background="#FFFFFF")
        self.authorName = Label(self, text='Copyright '+u'\u00a9'+" 2019 Tata Consultancy Services Limited")
        self.authorName.config(font = ('Montserrat','9'),foreground="#112D25", background="#FFFFFF")

        '''

        self.UserEntry = Entry(self,style="BW.TEntry", font=large_font,foreground = 'grey')
        self.UserEntry.insert(0, 'Employee ID')
        self.UserEntry.bind('<FocusIn>', self.on_Userentry_click)
        self.UserEntry.bind('<FocusOut>', self.on_Userfocusout)
        self.UserEntry.bind('<Return>', lambda x: self.clicked(self.UserEntry.get(), self.PassEntry.get()))

        self.PassEntry = Entry(self,style="BW.TEntry", font=large_font, foreground = 'grey')
        self.PassEntry.insert(0, 'Password')
        self.PassEntry.bind('<FocusIn>', self.on_Passentry_click)
        self.PassEntry.bind('<FocusOut>', self.on_Passfocusout)
        self.PassEntry.bind('<Return>', lambda x: self.clicked(self.UserEntry.get(), self.PassEntry.get()))
        '''

        '''
        self.signal = tk.Canvas(self,width=15, height=15)
        self.signal.place(x='470', y='220')
        self.catsWebLabel = Label(self, text='CATSWeb',style='BW.TLabel')
        self.catsWebLabel.place(x='390', y='220')
        '''
        
        
        helv36 = font.Font(family='Helvetica', size=11)
        self.btn = tk.Button(self, text="Login", command=lambda: self.clicked(self.Link.get()))
        self.btn.config(relief='flat', bg='#737370', fg="#FFFFFF", height=2, width=33)
        self.btnBind = self.btn.bind('<Return>', lambda x: self.clicked(self.Link.get()))
        self.btn['font'] = helv36


        self.internet = Label(self, text="Checking...")
        self.internet.config(font = ('Helvetica','11'), foreground="black", background="#FFFFFF")
        
        self.Link.place(x='80', y='200')
        self.logo.place(x='232', y='50', anchor='center')
        self.loginStatusMsg.place(x='232', y='170', anchor="center")
        self.btn.place(x='79', y='305')
        self.message.place(x='232', y='115', anchor="center")
        self.authorName.place(x='0', y='442')

        '''
        
        self.UserEntry.place(x='47', y='200')
        self.PassEntry.place(x='47', y='260')
        
        
        '''

        #self.internet.place(x='270', y='400')

    def on_Userentry_click(self, event):
        """function that gets called whenever entry is clicked"""
        if self.Link.get() == 'Insert link here':
           self.Link.delete(0, "end") # delete all the text in the entry
           self.Link.insert(0, '') #Insert blank for user input
           self.Link.config(foreground = 'black')
           self.LinkBind = self.Link.bind('<Return>', lambda x: self.clicked(self.Link.get()))

    def on_Userfocusout(self, event):
        if self.Link.get() == '':
            self.Link.insert(0, 'Insert link here')
            self.Link.config(foreground = 'grey')



    
class PageOne(tk.Frame):

    def __init__(self, parent, controller, clicked):
        tk.Frame.__init__(self, parent)

        self.running = 1
        self.main_url = ''
        self.treeSelection = ''
        self.userName = 'ABCDEFGHIJKL'
        self.item_iid = []
        self.queue = controller.queue
        self.userNameQueue = controller.userNameQueue
        self.infoQueue = Queue.Queue()
        self.CFnumQueue = Queue.Queue()
        self.flagQueue = Queue.Queue()
        self.controller = controller
        self.clicked = clicked

        self.CFnumBind = None
        self.previewButtonBind = None
        self.button1Bind = None
        self.delButtonBind = None
        self.button2Bind = None
        
        self.login_page = self.controller.get_page(LoginPage)

        style = Style()
        style.configure("BW.TLabel", font = ('Montserrat','10', 'bold'),foreground="#112D25", background="#DBDDDC")
        style.configure("BW.TButton", font = ('Montserrat','10','bold'), foreground="#112D25", background="#DBDDDC")
        style.configure("BW.TEntry", background="gray90")
        style.configure("BW.TCheck", foreground="#112D25", background="#FFFFFF")

        helv36 = font.Font(family='Helvetica', size=9)
        
        self.CF_number = Label(self, text="Complaint Folder:", style="BW.TLabel")
        self.CF_number.config(font = ('Helvetica','10','bold'), foreground="#112D25", background="#FFFFFF")

        self.CFnum = Entry(self, validate="key", validatecommand=(self.register(self.validate), '%P'))

        self.previewButton = tk.Button(self, text="View", command=lambda: self.viewPreview(self.CFnum.get(), self.item_iid, self.main_url))
        self.previewButton.config(relief='flat', bg='#737370', fg="#FFFFFF", height=1, width=8)
        self.previewButton['font'] = helv36

        self.logged_in_user = Label(self)
        self.logged_in_user.config(font = ('Helvetica','10','bold'), foreground="#112D25", background="#FFFFFF")
        
        self.authorName = Label(self, text='Copyright '+u'\u00a9'+" 2019 Tata Consultancy Services Limited")
        self.authorName.config(font = ('Montserrat','9'),foreground="#112D25", background="#FFFFFF")        
    
        self.button1 = tk.Button(self, text="Submit", command=lambda : self.submit(self.CFnum.get(), self.item_iid, self.main_url))
        self.button1.config(relief='flat', bg='#737370', fg="#FFFFFF", height=2, width=38)
        self.button1['font'] = helv36
        self.button1.config(state = 'disabled')

        self.delButton = tk.Button(self, text="Delete", command=lambda: self.delete(self.item_iid))
        self.delButton.config(relief='flat', bg='#737370', fg="#FFFFFF", height=1, width=8)
        self.delButton['font'] = helv36

        self.button2 = tk.Button(self, text="Logout", command=lambda: self.logout())
        self.button2.config(relief='flat', bg='#737370', fg="#FFFFFF", height=1, width=10)
        self.button2['font'] = helv36
        
        # Set the treeview
        self.tree = Treeview( self, columns=('CF number', 'Complaint Status'))
        self.tree.heading('#0', text='No', anchor='w')
        self.tree.heading('#1', text='Complaint Folder', anchor='w')
        self.tree.heading('#2', text='Complaint Status')
        self.tree.column('#0', stretch=tk.YES, width=33, anchor='w')
        self.tree.column('#1', stretch=tk.YES, width=100, anchor='w')
        self.tree.column('#2', stretch=tk.YES, width=318, anchor='w')
    
        self.treeview = self.tree
        self.treeview.bind("<<TreeviewSelect>>",lambda event :self.tree_select_event(event))

        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vsb.set)

        self.internet = Label(self, text="Checking...")
        self.internet.config(font = ('Helvetica','11'), foreground="black", background="#FFFFFF")

        self.logged_in_user.place(x='5', y='7')
        self.CF_number.place(x='67', y='45')
        self.CFnum.place(x='189', y='45')
        self.previewButton.place(x='332', y='42')
        self.button1.place(x='232', y='105', anchor='center')
        self.tree.place(x='0', y='140')
        self.delButton.place(x='15', y='385')
        self.button2.place(x='370', y='385')
        #self.internet.place(x='270', y='420')
        self.authorName.place(x='0', y='442')
        self.vsb.place(x='452', y='140', height=228)

        self.CFnum.focus()
        self.CFnum.bind("<<Paste>>", self.handle_clipboard)

        '''
        self.signal = tk.Canvas(self,width=15, height=15)
        self.signal.place(x='720', y='270')
        self.catsWebLabel = Label(self, text='CATSWeb',style='BW.TLabel')
        self.catsWebLabel.place(x='640', y='270')
        '''

    def handle_clipboard(self, event):
        #self.CFnum.delete(0, "end")
        lines = self.controller.clipboard_get().split("\n")
        lines = [eachCF+',' for eachCF in lines if len(eachCF) != 0]

        if len(lines) == 1:
            self.CFnum['text'] = lines[-1]

        else:
            for each_line in lines:
                print(each_line)
                if len(each_line) == 0:
                    continue

                self.CFnum.insert('end', str(each_line))
                #self.CFnum.insert('end', ',')

    def validate(self, possible_new_value):
        if re.match(r'^[0-9,]*$', possible_new_value):
            return True
        return False

    def tree_select_event(self, event):
        self.item_iid = self.tree.selection()
        print(self.item_iid)
        
    def viewPreview(self, CFnum, item_iid, main_url):
        if not self.internet_on():
            messagebox.showinfo('Error!', 'Internet not connected')
            return
            
        print(item_iid)
        if CFnum:
            self.thread1 = threading.Thread(target=self.workerThread2, args=(CFnum, main_url))
            self.thread1.daemon = True #This line tells the thread to quit if the GUI (master thread) quits
            self.thread1.start()

        elif len(item_iid) == 1:
            print(item_iid)
            self.thread1 = threading.Thread(target=self.workerThread2, args=(item_iid[0], main_url))
            self.thread1.daemon = True #This line tells the thread to quit if the GUI (master thread) quits
            self.thread1.start()

        elif len(CFnum) == 0:
            if len(item_iid) > 1:
                messagebox.showinfo('Error!', 'Multiple CFs cannot be viewed')
            
            else:
                messagebox.showinfo('Error!', 'Enter a complaint folder number')
            return


    def workerThread2(self,CFnum, main_url):
        sessionFlag, previewFlag, previewMsg, fileFlag = complaint_handler.preview(CFnum, main_url)

        if not fileFlag:
            messagebox.showinfo('Error!','chromedriver.exe file not found')

        elif not sessionFlag:
            messagebox.showinfo('Error!', 'Session Expired. Please login again')
            self.logout()

        elif not previewFlag:
            messagebox.showinfo('Error!', previewMsg)


    def delete(self, item_iid):
        if not self.item_iid:
            messagebox.showinfo('Error!', 'Please select a complaint folder')
        else:
            for treeSelection in self.item_iid:
                if 'Ongoing' in self.treeview.item(treeSelection)["tags"]:
                    messagebox.showinfo('Error!', 'Complaint folder in process. Cannot delete')
                    return
                self.treeview.delete(treeSelection)
                self.item_iid = list(self.item_iid)
                self.item_iid.remove(treeSelection)
                self.item_iid = tuple(self.item_iid)
                self.treeSelection = ''


                items = self.treeview.get_children()
                length = len(self.treeview.get_children())

                for counter, item in enumerate(items):
                    self.treeview.item(item, text=str(counter+1))


                #for child in self.treeview.get_children():
                    #print(self.treeview.item(child)["values"])


    def logout(self):
        self.login_page.linkBind = self.login_page.Link.bind('<Return>', lambda x: self.clicked(self.login_page.Link.get()))

        self.CFnum.unbind('<Return>', self.CFnumBind)
        self.button1.unbind('<Return>', self.button1Bind)
        self.previewButton.unbind('<Return>', self.previewButtonBind)
        self.delButton.unbind('<Return>', self.delButtonBind)
        self.button2.bind('<Return>', self.button2Bind)

        self.login_page.btn.config(state = 'normal')
        self.login_page.Link.delete(0, "end")
        self.login_page.Link.insert(0, 'Insert link here')
        self.login_page.Link.config(foreground = 'grey')
        self.button1.config(state = 'disabled')
        self.CFnum.delete(0, "end")
        self.tree.delete(*self.tree.get_children())
        killPhantom = '\\\\'.join(os.path.join(current_folder,"killPhantom.bat").split('\\'))
        killChrome = '\\\\'.join(os.path.join(current_folder,"killChrome.bat").split('\\'))

        killPhan = Path(killPhantom)
        if not killPhan.is_file():
            messagebox.showinfo('Error!','killPhantom.bat file not found')

        else:
            Popen(killPhantom)

        killChro = Path(killChrome)
        if not killChro.is_file():
            messagebox.showinfo('Error!','killChrome.bat file not found')

        else:
            Popen(killChrome)

        self.controller.show_frame(LoginPage)


    def submit(self, CFnum, item_iid, main_url):
        if not self.internet_on():
            messagebox.showinfo('Error!', 'Internet not connected')
            return

        self.running = 1
        if CFnum:
            CFlist = CFnum.split(',')
            CFlist = [eachCF for eachCF in CFlist if len(eachCF) != 0]
            for eachCF in CFlist:
                if eachCF in self.treeview.get_children():
                    print(eachCF, self.treeview.item(eachCF)["tags"])
                    if 'Ongoing' in self.treeview.item(eachCF)["tags"]:
                        messagebox.showinfo('Error!', 'Complaint folder already in process')
            
                    elif any(tag in self.treeview.item(eachCF)["tags"] for tag in ['Error', 'Closed']):
                        self.treeview.item(eachCF, values=(eachCF,'Processing... Please wait'), tags='Ongoing')

                else:
                    self.treeview.insert('', 'end', eachCF, text=str( len(self.treeview.get_children())+1), values=(eachCF,'Processing... Please wait'), tags='Ongoing')
                    print(eachCF, self.treeview.item(eachCF)["tags"])

                self.treeview.tag_configure('Ongoing', background='')
                self.treeview.yview_moveto(1)
                self.CFnum.delete(0, "end")
                ThreadedTask(eachCF, main_url, self.infoQueue,self.CFnumQueue, self.flagQueue, self.controller).start()

        elif len(item_iid) >= 1:
            for treeSelection in item_iid:
                print(treeSelection, self.treeview.item(treeSelection)["tags"])

                if 'Ongoing' in self.treeview.item(treeSelection)["tags"]:
                    messagebox.showinfo('Error!', 'Complaint folder already in process')

                elif any(tag in self.treeview.item(treeSelection)["tags"] for tag in ['Error', 'Closed']):
                    self.treeview.item(treeSelection, values=(treeSelection,'Processing... Please wait'), tags='Ongoing')
                    self.treeview.tag_configure('Ongoing', background='')
                    self.treeview.yview_moveto(1)
                    ThreadedTask(treeSelection, main_url, self.infoQueue,self.CFnumQueue, self.flagQueue, self.controller).start()

        elif len(CFnum) == 0:
            messagebox.showinfo('Error!', 'Enter a complaint folder number')
            return

    def internet_on(self):
        for timeout in [10,15]:
            try:
                socket.setdefaulttimeout(timeout)
                host = socket.gethostbyname("www.google.com")
                s = socket.create_connection((host, 80), 2)
                s.close()
                return True
            except : pass
        return False


    def processQueueIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize( ):
            try:
                self.main_url = self.queue.get(0)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                
            except Queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

    def processUserNameQueueIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.userNameQueue.qsize( ):
            try:
                self.userName = self.userNameQueue.get(0)
                self.logged_in_user.config(text = 'Logged in as '+self.userName)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
                
            except Queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

    def processinfoQueueIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.infoQueue.qsize( ):
            try:
                CFnum = self.CFnumQueue.get(0)
                statusMsg = self.infoQueue.get(0)
                statusFlag = self.flagQueue.get(0)
                print('output: ',CFnum, statusMsg, statusFlag)
                if statusFlag:
                    self.treeview.set(CFnum, 'Complaint Status', statusMsg)
                    self.treeview.item(CFnum, tags='Closed')
                    self.treeview.tag_configure('Closed', background='#51FE1A')
                else:
                    self.treeview.set(CFnum, 'Complaint Status', statusMsg)
                    self.treeview.item(CFnum, tags='Error')
                    self.treeview.tag_configure('Error', background = '#FE3D29')
                # Check contents of message and do whatever is needed. As a
                # simple test, print it in real life, you would
                # suitably update the GUI's display in a richer fashion).
                
            except Queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass



class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. We spawn a new thread for the worker (I/O).
        """
        self.running = 1

        # Create the queue
        self.queue = Queue.Queue()
        self.userNameQueue = Queue.Queue()

        # Set up the GUI part
        self.gui = ComplaintHandlerUI(self.queue, self.userNameQueue, self.clicked)

        self.login_page = self.gui.get_page(LoginPage)
        self.page_one = self.gui.get_page(PageOne)

        self.periodicCall()

        self.gui.mainloop()


    def periodicCall(self):
        self.page_one.processQueueIncoming()
        self.page_one.processinfoQueueIncoming()
        self.page_one.processUserNameQueueIncoming()
        
        #Check every 200 ms if there is an active internet connection
        '''
        if(self.internet_on()):
            self.login_page.internet.config(text='Internet Connected')
            self.page_one.internet.config(text='Internet Connected')

            self.login_page.btn.config(command=lambda: self.clicked(self.login_page.Link.get()))

            self.page_one.button1.config(command=lambda: self.page_one.submit(self.page_one.CFnum.get(), self.page_one.item_iid, self.page_one.main_url))
            
      
            if(self.catsWebconn() == 200):
                self.login_page.signal.config(bg='green')
                self.page_one.signal.config(bg='green')
            else:
                self.login_page.signal.config(bg='red')
                self.page_one.signal.config(bg='red')
         
        else:
            self.login_page.internet.config(text='Internet Not Connected')
            self.page_one.internet.config(text='Internet Not Connected')

            self.login_page.btn.config(command=lambda: self.messagebox())
            
            self.page_one.button1.config(command=lambda: self.messagebox())
           
            #self.login_page.signal.config(bg='red')
        '''
        

        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            self.running = 0
            
        self.gui.after(500, self.periodicCall)

    def messagebox(self):
        messagebox.showinfo('Error!', 'Internet not connected')

    
    def internet_on(self):
        for timeout in [10,15]:
            try:
                socket.setdefaulttimeout(timeout)
                host = socket.gethostbyname("www.google.com")
                s = socket.create_connection((host, 80), 2)
                s.close()
                return True
            except : pass
        return False

    def catsWebconn(self):
        try:
            return (urlopen("http://cwprod/CATSWebNET/").getcode())
        except:
            return False

    def clicked(self, url):
        print('Url: ', url)
        site = None

        if not self.internet_on():
            messagebox.showinfo('Error!', 'Internet not connected')
            return

        elif url == 'Insert link here' or len(url) == 0:
            messagebox.showinfo('Error!', 'Enter catsweb link')
            return
    
        elif 'http://cwprod/CATSWebNET/'.lower() in url.lower():
            site = 'CWPROD'

        elif 'http://cwqa/CATSWebNET/'.lower() in url.lower():
            site = 'CWQA'

        elif 'https://cwdev.jnj.com/catswebnet/'.lower() in url.lower():
            site = 'CWDEV'

        else:
            messagebox.showinfo('Error!', 'Invalid url')
            return

        self.running = 1
        self.login_page.message.config(text='')
        self.login_page.loginStatusMsg.config(text='Logging in... Please wait')
        self.thread1 = threading.Thread(target=self.workerThread1, args=(url, site))
        self.thread1.daemon = True #This line tells the thread to quit if the GUI (master thread) quits
        self.thread1.start()
        self.login_page.Link.unbind('<Return>', self.login_page.LinkBind)


    def workerThread1(self, url, site):
        while self.running:
            self.login_page.btn.config(state = 'disabled')
            
            loginMsg, userName, url, flag, fileFlag = complaint_handler.Login(url, site)
            print('Logged in', site, loginMsg, userName, url, flag, fileFlag )

            if flag:
                self.login_page.message.config(text='Please copy your CATSWeb logged in url:', font = ('Helvetica','11'), foreground="#638213", background="#FFFFFF")
                self.login_page.queue.put(url)
                self.login_page.userNameQueue.put(userName)
                self.page_one.CFnum.focus()
                self.page_one.button1.config(state = 'normal')
                if self.internet_on():
                    self.page_one.CFnumBind = self.page_one.CFnum.bind('<Return>', lambda x: self.page_one.submit(self.page_one.CFnum.get(), self.page_one.item_iid, self.page_one.main_url))
                    self.page_one.button1Bind = self.page_one.button1.bind('<Return>', lambda x: self.page_one.submit(self.page_one.CFnum.get(), self.page_one.item_iid, self.page_one.main_url))
                    self.page_one.previewButtonBind = self.page_one.previewButton.bind('<Return>', lambda x: self.page_one.viewPreview(self.page_one.CFnum.get(), self.page_one.item_iid, self.page_one.main_url))
                    self.page_one.delButtonBind = self.page_one.delButton.bind('<Return>', lambda x: self.page_one.delete(self.page_one.item_iid))
                    self.page_one.button2Bind = self.page_one.button2.bind('<Return>', lambda x: self.page_one.logout())

                    self.login_page.controller.show_frame(PageOne)
                else:
                    messagebox.showinfo('Error!','Internet not connected')
                    self.login_page.LinkBind = self.login_page.Link.bind('<Return>', lambda x: self.login_page.clicked(self.login_page.Link.get()))
                    self.login_page.Link.delete(0, "end")
                    self.login_page.Link.insert(0, 'Insert link here')
                    self.login_page.Link.config(foreground = 'grey')
                    self.login_page.btn.config(state = 'normal')
                    self.page_one.button1.config(state = 'disabled')
                    self.login_page.controller.focus()

                print("Logged in!")
                print('---------------------------------------------')

            else:
                if not fileFlag:
                    messagebox.showinfo('Error!','phantomjs.exe file not found')

                self.login_page.LinkBind = self.login_page.Link.bind('<Return>', lambda x: self.login_page.clicked(self.login_page.Link.get()))

                self.page_one.CFnum.unbind('<Return>', self.page_one.CFnumBind)
                self.page_one.button1.unbind('<Return>', self.page_one.button1Bind)

                self.login_page.message.config(text=loginMsg, font = ('Helvetica','11'), foreground="#E26C1B", background="#FFFFFF")
                self.login_page.btn.config(state = 'normal')
                self.page_one.button1.config(state = 'disabled')
                self.login_page.controller.focus()
                print('Invalid login, please try again.')
                print('----------------------------------------')


            batch_file = '\\\\'.join(os.path.join(current_folder,"killPhantom.bat").split('\\'))

            my_file = Path(batch_file)
            if not my_file.is_file():
                messagebox.showinfo('Error!','killPhantom.bat file not found')

            else:
                Popen(batch_file)

            self.running = 0
            self.login_page.loginStatusMsg.config(text='')
    

class ThreadedTask(threading.Thread):
    def __init__(self, CFnum, main_url, infoQueue, CFnumQueue, flagQueue, controller):
        threading.Thread.__init__(self)
        self.daemon = True #This line tells the thread to quit if the GUI (master thread) quits
        self.CFnum = CFnum
        self.main_url = main_url
        self.infoQueue = infoQueue
        self.CFnumQueue = CFnumQueue
        self.flagQueue = flagQueue
        self.controller = controller
        self.login_page = self.controller.get_page(LoginPage)
        self.page_one = self.controller.get_page(PageOne)

    def run(self):
        sessionFlag, CF_number, statusMsg, statusFlag, fileFlag = complaint_handler.complaintProcess(self.CFnum, self.main_url)

        if not fileFlag:
            messagebox.showinfo('Error!','phantomjs.exe file not found')
            self.page_one.logout()

        elif not sessionFlag:
            messagebox.showinfo('Error!', 'Session Expired. Please login again')
            self.page_one.logout()

        else:
            self.CFnumQueue.put(CF_number)
            self.infoQueue.put(statusMsg)
            self.flagQueue.put(statusFlag)
            


client = ThreadedClient()
