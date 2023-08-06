# PySuperGui V0.0.4
This library creates guis in a simpler way using Tkinter.
***Remembering this library is in Development, more stuff will be added and bugs will be fixed!***
### Installing
The best way to install is using **pip** or **pip3**
Just type in cmd:
`pip install PySuperGui`
or
`pip3 install PySuperGui`
###Get Started
To create a Gui we will use **Start()**. These are the different parameters or "options" that one may use:

| Option  | Description  |
| ------------ | ------------ |
| title  | Window Title  |
| color  | Background Color  |
| width  | The width of the window  |
| height  | The height of the window  |
| posX  | The X position of the window  |
| posY  | The Y position of the window |
Example:
```python
gui = Start(title="Test",color="grey", width=200, height=200, posX=0.025, posY=0.05)
```
When creating the window it will not appear, to make it appear use:
```python
gui.show()
```

