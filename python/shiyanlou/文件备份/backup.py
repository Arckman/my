import os
import tkinter
import time

def backup():
    global entry_source,entry_target
    source=entry_source.get()
    target=entry_target.get()

    today_dir=target+time.strptime("%Y%m%d")
    time_dir=time.strftime("%H%M%S")

    touch=today_dir+os.sep+time_dir+".zip"
    command_touch="zip -qr "+touch+" "+source

    if os.path.exists(today_dir)==0:
        os.mkdir(today_dir)
    if os.system(command_touch)==0:
        print("success")
    else:
        print("fail")

root=tkinter.Tk()
root.title("BackUp")
root.geometry("200x200")
#row 1
lbl_source=tkinter.Label(root,text="Source")
lbl_source.grid(row=0,column=0)
entry_source=tkinter.Entry(root)
entry_source.grid(row=0,column=1)
#row 2
lbl_target=tkinter.Label(root,text="Target")
lbl_target.grid(row=1,column=0)
entry_target=tkinter.Entry(root)
entry_target.grid(row=1,column=1)
#row 3
but_bak=tkinter.Button(root,text="BackUp")
but_bak.grid(row=2,column=0)
but_bak["command"]=backup

root.mainloop()