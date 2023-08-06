import tkinter
import tkinter.ttk

class InvalidValue(Exception):
    pass

class Start:
    def __init__(self, title="PySuperGui",color="white", width=250, height=200, posX=400, posY=200):
        try:
            self.Title = title
            self.gui = tkinter.Tk()
            self.gui.configure(bg=color)
            self.gui.title(title)
            self.gui.iconphoto(False, tkinter.PhotoImage(data="iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAABMWlDQ1BBZG9iZSBSR0IgKDE5OTgpAAAoz62OsUrDUBRAz4ui4lArBHFweJMoKLbqYMakLUUQrNUhydakoUppEl5e1X6Eo1sHF3e/wMlRcFD8Av9AcergECGDgwie6dzD5XLBqNh1p2GUYRBr1W460vV8OfvEDFMA0Amz1G61DgDiJI74wecrAuB50647Df7GfJgqDUyA7W6UhSAqQP9CpxrEGDCDfqpB3AGmOmnXQDwApV7uL0ApyP0NKCnX80F8AGbP9Xww5gAzyH0FMHV0qQFqSTpSZ71TLauWZUm7mwSRPB5lOhpkcj8OE5UmqqOjLpD/B8BivthuOnKtall76/wzrufL3N6PEIBYeixaQThU598qjJ3f5+LGeBkOb2F6UrTdK7jZgIXroq1WobwF9+MvwMZP/U6/OGUAAAAJcEhZcwAACxMAAAsTAQCanBgAAAXwaVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/PiA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJBZG9iZSBYTVAgQ29yZSA1LjYtYzE0OCA3OS4xNjQwMzYsIDIwMTkvMDgvMTMtMDE6MDY6NTcgICAgICAgICI+IDxyZGY6UkRGIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+IDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0RXZ0PSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VFdmVudCMiIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bXA6Q3JlYXRvclRvb2w9IkFkb2JlIFBob3Rvc2hvcCAyMS4wIChXaW5kb3dzKSIgeG1wOkNyZWF0ZURhdGU9IjIwMjItMDItMTlUMTc6NTE6MTEtMDM6MDAiIHhtcDpNZXRhZGF0YURhdGU9IjIwMjItMDItMTlUMTc6NTE6MTEtMDM6MDAiIHhtcDpNb2RpZnlEYXRlPSIyMDIyLTAyLTE5VDE3OjUxOjExLTAzOjAwIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOmVjYTYzYjJiLTEzZmMtYzc0ZC05MmJkLTYyMWYyMGNmMzJlNiIgeG1wTU06RG9jdW1lbnRJRD0iYWRvYmU6ZG9jaWQ6cGhvdG9zaG9wOjQ1MTg3YTQ5LTQyN2MtZTU0YS1iNjNjLWIxNzEzNzY1NGRhNCIgeG1wTU06T3JpZ2luYWxEb2N1bWVudElEPSJ4bXAuZGlkOjU4NzRlYmMyLWQwMDYtMWE0MC05ZGJmLTM4N2VlNGM2Mzg1YSIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJBZG9iZSBSR0IgKDE5OTgpIj4gPHhtcE1NOkhpc3Rvcnk+IDxyZGY6U2VxPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0iY3JlYXRlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDo1ODc0ZWJjMi1kMDA2LTFhNDAtOWRiZi0zODdlZTRjNjM4NWEiIHN0RXZ0OndoZW49IjIwMjItMDItMTlUMTc6NTE6MTEtMDM6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCAyMS4wIChXaW5kb3dzKSIvPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6ZWNhNjNiMmItMTNmYy1jNzRkLTkyYmQtNjIxZjIwY2YzMmU2IiBzdEV2dDp3aGVuPSIyMDIyLTAyLTE5VDE3OjUxOjExLTAzOjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgMjEuMCAoV2luZG93cykiIHN0RXZ0OmNoYW5n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"))
            self.gui.geometry(str(width) + "x" + str(height) + "+"+str(posX)+"+"+str(posY))
            self.Size = str(width) + "x" + str(height) + "+"+str(posX)+"+"+str(posY)
            self.gui.resizable(True, True)
        except tkinter.TclError:
            raise InvalidValue("Error")
    def _gettkIG(self):
        return {"gui":self.gui,"title":self.Title,"size":self.Size}
    def show(self):
        self.gui.mainloop()
    def resizable(self, width=True, height=True):
        self.gui.resizable(width, height)
    def size(self, SizeX, SizeY):
        try:
            self.Size = str(SizeX) + "x" + str(SizeY) + "+400+200"
            self.gui.geometry(self.Size)
        except tkinter.TclError:
            raise InvalidValue("Invalid Size")
    def icon(self, image):
        self.gui.iconphoto(False,image._gettkIG()["file"])
class Frame:
    def __init__(self, gui, color="grey",cursor="", posX=0, posY=0, width=0.2, height=0.2):
        info = gui._gettkIG()
        if cursor != "":
            self.Frame = tkinter.Frame(info["gui"], cursor=cursor, bg=color)
        else:
            self.Frame = tkinter.Frame(info["gui"], bg=color)
        self.Frame.place(relx=posX, rely=posY, relwidth=width, relheight=height)
    def _gettkIG(self):
        return {"frame":self.Frame}
class TextButton:
    def __init__(self, frame, text="Text", command="", alignment="center" ,bkColor="white", textColor="black", posX=0, posY=0, width=0.2, height=0.2):
        info = frame._gettkIG()
        if command == "":
            self.Button = tkinter.Button(info["frame"],justify=alignment, bg=bkColor,fg=textColor , text=text)
        else:
            self.Button = tkinter.Button(info["frame"],bg=bkColor,justify=alignment,fg=textColor , text=text, command=command)
        self.Button.place(relx=posX, rely=posY, relwidth=width ,relheight=height)
class TextLabel:
    def __init__(self, frame, text="Text", bkColor="grey",alignment="center" ,textColor="black",font="Arial", fontSize=12, posX=0, posY=0, width=0.2, height=0.2):
        info = frame._gettkIG()
        self.Text = tkinter.Label(info["frame"],font=(font,fontSize),justify=alignment , text=text, bg=bkColor,fg=textColor)
        self.Text.place(relx=posX, rely=posY, relwidth=width, relheight=height)
class TextBox:
    def __init__(self, frame, text="",bkColor="white", textColor="black",alignment="left", posX=0, posY=0, width=0.2, height=0.15):
        info = frame._gettkIG()
        self.TB = tkinter.Entry(info["frame"], bg=bkColor,justify=alignment, fg=textColor)
        self.TB.insert(0,text)
        self.TB.place(relx=posX, rely=posY, relwidth=width, relheight=height)
    def getValue(self):
        return self.TB.get()
class CheckBox:
    def __init__(self, frame, text="",command="" ,cursor="",mode="normal",bkColor="grey" ,alignment="left", textColor="black", posX=0, posY=0, width=0.2, height=0.15):
        info = frame._gettkIG()
        self.var1 = tkinter.IntVar()
        if command == "":
            self.CB = tkinter.Checkbutton(info["frame"], text=text,state=mode,justify=alignment,cursor=cursor,fg=textColor , bg=bkColor,variable=self.var1)
        else:
            self.CB = tkinter.Checkbutton(info["frame"], text=text,state=mode,justify=alignment,cursor=cursor ,fg=textColor, command=command, bg=bkColor,variable=self.var1)
        self.CB.place(relx=posX, rely=posY, relwidth=width, relheight=height)
    def getValue(self):
        if self.var1.get() == 0:
            return False
        elif self.var1.get() == 1:
            return True
class ComboBox:
    def __init__(self, frame, values=[],command="",alignment="center", text="", posX=0, posY=0, width=0.2, height=0.15):
        info = frame._gettkIG()
        if command == "":
            self.ComboBox = tkinter.ttk.Combobox(info["frame"],justify=alignment, state="readonly", values=values)
        else:
            self.ComboBox = tkinter.ttk.Combobox(info["frame"],justify=alignment, state="readonly", postcommand=command, values=values)
        self.ComboBox.set(text)
        self.ComboBox.place(relx=posX, rely=posY, relwidth=width, relheight=height)
    def getValue(self):
        return self.ComboBox.get()

class RadioBox:
    def __init__(self, frame, command=""):
        self.info = frame._gettkIG()
        self.Var = tkinter.IntVar()
        self.Bts = []
        self.Command = command
    def addButton(self, text="RadioButton",alignment="center",active=False,mode="normal",command="",cursor="",bkColor="white", textColor="black", posX=0, posY=0, width=0.2, height=0.15):
        val = 2 if active == False else 1
        self.Bt = tkinter.Radiobutton(self.info["frame"], variable=self.Var, text=text, command=command if command != "" else self.Command,value=val,justify=alignment,state=mode,cursor=cursor,bg=bkColor, fg=textColor)
        self.Bt.place(relx=posX, rely=posY, relwidth=width, relheight=height)
        self.Bts.append(text)
    def getValue(self):
        return self.Bts[self.Var.get()-1]


class Image:
    def __init__(self, file="",data=""):
        if file != "":
            self.file = tkinter.PhotoImage(file=file)
        elif data != "":
            self.file = tkinter.PhotoImage(data=data)
    def _gettkIG(self):
        return {"file":self.file}

def RGB(red,green,blue):
    return "#%02x%02x%02x" % (red, green, blue)

