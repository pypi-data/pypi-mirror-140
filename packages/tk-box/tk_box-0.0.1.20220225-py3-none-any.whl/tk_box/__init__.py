from logging import root
from tkinter.ttk import*
from tkinter import *
from tkinter import messagebox
import json
"""
{
    "title" : "",
    "data" : [
        {
            "name" : "str",
            "f_n" : "str",
            "code" : "lstr",
            "user" : "str",
            "update" : "str"
        }
        
    ]
}
"""

with open("data.json","r") as f:
    data = json.load(f)
root = Tk()
note = Notebook(root)
for x in data["data"]:
    def right(*event):
        messagebox.showinfo(f"""作者：{x["user"] if x["user"]!="" else "这个作者太懒不想留名字"}\n更新时间：{x["update"] if x["update"]!="" else "没有更新时间"}""")
    v = {}
    exec(x["code"],v)
    # v[x["f_n"].bind('<Button-3>', )
    # note.add()
    note.add(v[x["f_n"]],text = x["name"])
note.pack(fill = BOTH,expand=1)
root.title(data["title"])
root.mainloop()