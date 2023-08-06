# -*- coding:utf-8 -*-
# Date: 2018-03-07 16:41:50
# Author: dekiven

import os
from DKVTools.Funcs import *

if isPython3() :
    import tkinter as tk
    from tkinter import ttk
    import tkinter.filedialog as fileDialog
    import tkinter.messagebox as messageBox
else:
    import Tkinter as tk
    import  ttk
    import tkFileDialog as fileDialog
    import tkMessageBox as messageBox

try :
    from TkinterDnD2.TkinterDnD import Tk as DND
except Exception as e :
    DND = None
    pass

Pathjoin = os.path.join
PathExists = os.path.exists
# curDir = os.getcwd()
curDir = os.path.split(sys.argv[0])[0]

def getTk() :
    '''return tk, ttk
    '''
    return tk, ttk

def GetEntry(root, default='', onKey=None, title='') :
    frame = ttk.LabelFrame(root, text=title)
    et = tk.StringVar()
    entry = ttk.Entry(frame, textvariable=et)
    if isFunc(onKey) :
        entry.bind('<Key>', lambda event : onKey(event.char))
    entry.pack(fill=tk.BOTH)

    def getValue() :
        return et.get()
    def setValue(value) :
        et.set(str(value))
        entry.icursor(tk.END)
    def setTitle( text ) :
        frame.configure(text=text or '')
    setValue(default)

    frame.getValue = getValue
    frame.setValue = setValue
    frame.setTitle = setTitle
    frame.focus = entry.focus
    frame.icursor = entry.icursor
    frame.insert = entry.insert
    frame.delete = entry.delete

    #select_adjust(idx) 选中索引为idx和光标所有位置之前的所有值
    frame.select_adjust = entry.select_adjust
    #select_clear() 清空文本框
    frame.select_clear = entry.select_clear
    #select_from(idx)
    frame.select_from = entry.select_from
    #select_range(s, e) 选中指定索引之前的值，s必须比e小
    frame.select_range = entry.select_range
    #select_to(idx)
    frame.select_to = entry.select_to

    frame.entry = entry

    return frame


def __getDirOrFileWidget(isFile, root, title='', msgUp='', pathSaved=None, callback=None, enableEmpty=False, showOpen=True, showOpenFolder=False, mustexist=False, exts=None) :
    widget = ttk.LabelFrame(root, text=title)
    widget.title = title

    strUpMsg = tk.StringVar()
    strUpMsg.set(msgUp)
    ttk.Label(widget, textvariable = strUpMsg, justify=tk.CENTER, anchor=tk.CENTER).pack(anchor=tk.CENTER, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)

    column2 = ttk.Frame(widget)
    et = tk.StringVar()
    if pathSaved :
        et.set(pathSaved)
    entry = ttk.Entry(column2, textvariable = et)
    entry.pack(expand=tk.YES, fill=tk.BOTH, side=tk.LEFT, padx=5, pady=5)

    setValue = et.set
    getValue = et.get
    if exts :
        exts = [e.lower() for e in exts]

    def onChosen(path) :
        if ((path is not None) and path != '') or enableEmpty :
            setValue(path)
            if isFunc(callback) :
                callback(path)

    def btnCallback() :
        if isFile :
            p = et.get()
            d = None
            f = None
            types = [('all files', '.*'), ]
            added = []
            ext = None
            if p != '' :
                d,f = os.path.split(p)
                ext = os.path.splitext(f)[-1]
                types.insert(0, ('%s files'%ext, ext))
            if isinstance(exts, list) or isinstance(exts, tuple) :
                for e in exts :
                    types.insert(0, ('%s files'%e, e))

            ShowChooseFileDialog(onChosen, initialdir=d, initialfile=f, defaultextension=ext, filetypes=types, parent=getToplevel(root))
        else :
            initialdir, initialfile = os.path.split(et.get())
            ShowChooseDirDialog(onChosen, initialdir=initialdir, parent=getToplevel(root), mustexist=mustexist)

    strTips = isFile and u'文件\n"%s"\n不存在！' or u'文件夹"%s"不存在！'
    def openBtnCallback() :
        path = et.get()
        if os.path.exists(path) :
            startFile(path)
        else :
            ShowInfoDialog(strTips%(str(path)))

    def openFileFolder() :
        path = et.get()
        if os.path.exists(path) :
            print('dekiven selectInFolder%s'%path)
            selectInFolder(path)
        else :
            ShowInfoDialog(strTips%(str(path)))

    ttk.Button(column2, text = 'Search', command=btnCallback).pack(fill=tk.Y, side=tk.LEFT, padx=2, pady=5)
    if showOpen :
        ttk.Button(column2, text = 'Open', command=openBtnCallback).pack(fill=tk.Y, side=tk.LEFT, padx=2, pady=5)
    if showOpenFolder :
        ttk.Button(column2, text = 'Folder', command=openFileFolder).pack(fill=tk.Y, side=tk.LEFT, padx=2, pady=5)

    column2.pack(expand=tk.YES, fill=tk.BOTH, side=tk.TOP)

    def getTitle() :
        return widget.title

    def setTitle(title) :
        widget.config(text=title)
        widget.title = title

    def drop( event ) :
        if event.data and len(event.data) > 0 :
            for file in entry.tk.splitlist(event.data) :
                if isFile :
                    if (os.path.isfile(file)) and (exts is None or os.path.splitext(file)[-1] in exts) :
                        onChosen(file)
                        return event.action
                elif os.path.isdir(file) :
                    onChosen(file)
                    return event.action
    # if DND :
    #     entry.drop_target_register('DND_Files')
    #     entry.dnd_bind('<<Drop>>', drop)
    bindDragTargetFuncs(entry, 'DND_Files', drop=drop)

    widget.getTitle = getTitle
    widget.setTitle = setTitle

    widget.getValue = getValue
    widget.setValue = setValue

    widget.setUpMsg = strUpMsg.set
    widget.getUpMsg = strUpMsg.get

    return widget

def GetDirWidget(root, title='', msgUp='', pathSaved=None, callback=None, enableEmpty=False, showOpen=True, mustexist=False) :
    '''参数说明:
    root:           tk 父节点
    title:          显示在Entry左边的标题
    msgUp:          显示在Entry上面的说明文字
    pathSaved:      默认的路径，会显示都Entry
    callback:       选择好文件夹的回调
    enableEmpty:    没有选择文件夹时是否回调空串
    showOpen:       是否显示打开文件夹的按钮
    mustexist:      是否必须存在

返回的控件包含方法如下：
    getTitle        获取title
    setTitle        设置title
    getValue        获取文本框的值
    setValue        设置文本框的值
    setUpMsg        设置文本框上面的说明文字
    getUpMsg        获取文本框上面的说明文字
    '''
    return __getDirOrFileWidget(False, root, title=title, msgUp=msgUp, pathSaved=pathSaved, callback=callback, enableEmpty=enableEmpty, showOpen=showOpen, mustexist=mustexist)

def GetFileWidget(root, title='', msgUp='', pathSaved=None, callback=None, enableEmpty=False, showOpen=False, showOpenFolder=True, exts=None) :
    '''参数说明:
    root:           tk 父节点
    title:          显示在Entry左边的标题
    msgUp:          显示在Entry上面的文本
    pathSaved:      默认的路径，会显示都Entry
    callback:       选择好文件夹的回调
    enableEmpty:    没有选择文件夹时是否回调空串
    showOpen:       是否显示打开文件夹的按钮
    showOpenFolder: 是否显示打开文件所在文件夹按钮
    exts: 限定的后缀，可以传入list或tuple，如:('.txt', '.png')

返回的控件包含方法如下：
    getTitle        获取title
    setTitle        设置title
    getValue        获取文本框的值
    setValue        设置文本框的值
    setUpMsg        设置文本框上面的说明文字
    getUpMsg        获取文本框上面的说明文字
    '''
    return __getDirOrFileWidget(True, root, title=title, msgUp=msgUp, pathSaved=pathSaved, callback=callback, enableEmpty=enableEmpty, showOpen=showOpen, showOpenFolder=showOpenFolder, exts=exts)

def ShowChooseDirDialog(callback=None, **options) :
    '''callback 回调，传入选中的文件夹名
    options : 传入参数
        # - defaultextension: added to filename if not explicitly given
        # - filetypes: sequence of (label, pattern) tuples.  the same pattern may occur with several patterns.  use "*" as pattern to indicate all files.
        # - initialdir: initial directory.  preserved by dialog instance.
        # - initialfile: initial file (ignored by the open dialog).  preserved by dialog instance.
        # - parent: which window to place the dialog on top of
        # - title: dialog title
        # - multiple: if true user may select more than one file
        # - mustexist: if true, user must pick an existing directory
    示例:
    options = {
        'defaultextension' : '.txt',
        'filetypes' : [('all files', '.*'), ('text files', '.txt')],
        'initialdir' : 'c://',
        'initialfile' : 'windows',
        'parent' : root,
        'title' : 'This is a title',
        'multiple' : False,
    }
    '''
    path = fileDialog.askdirectory(**options)
    if isFunc(callback) :
        # if not isinstance(path, str) :
        #   path = path
        callback(path)
    return path


def ShowChooseFileDialog(callback=None, MultiChoose=False, **options) :
    '''callback 回调，传入选中的文件名Tuple
    MultiChoose 是否是多选模式
    options : 传入参数
        # - defaultextension: added to filename if not explicitly given
        # - filetypes: sequence of (label, pattern) tuples.  the same pattern may occur with several patterns.  use "*" as pattern to indicate all files.
        # - initialdir: initial directory.  preserved by dialog instance.
        # - initialfile: initial file (ignored by the open dialog).  preserved by dialog instance.
        # - parent: which window to place the dialog on top of
        # - title: dialog title
        # - multiple: if true user may select more than one file
    示例:
    options = {
        'defaultextension' : '.txt',
        'filetypes' : [('all files', '.*'), ('text files', '.txt')],
        'initialdir' : 'c://',
        'initialfile' : 'myfile.txt',
        'parent' : root,
        'title' : 'This is a title',
        'multiple' : False,
    }
    '''
    path = None
    if MultiChoose :
        path = fileDialog.askopenfilenames(**options)
        path = [formatPath(p) for p in path]
    else :
        path = fileDialog.askopenfilename(**options)
        path = formatPath(path)
    if isFunc(callback) :
        # if not isinstance(path, str) :
        #   path = path
        callback(path)
    return path

def ShowSaveAsFileDialog(callback=None, **options) :
    '''callback 回调，传入保存的文件名
    options : 传入参数
        # - defaultextension: added to filename if not explicitly given
        # - filetypes: sequence of (label, pattern) tuples.  the same pattern may occur with several patterns.  use "*" as pattern to indicate all files.
        # - initialdir: initial directory.  preserved by dialog instance.
        # - initialfile: initial file (ignored by the open dialog).  preserved by dialog instance.
        # - parent: which window to place the dialog on top of
        # - title: dialog title
        # - multiple: if true user may select more than one file
    示例:
    options = {
        'defaultextension' : '.txt',
        'filetypes' : [('all files', '.*'), ('text files', '.txt')],
        'initialdir' : 'c://',
        'initialfile' : 'myfile.txt',
        'parent' : root,
        'title' : 'This is a title',
        'multiple' : False,
    }
    '''
    path = fileDialog.asksaveasfilename(**options)
    if isFunc(callback) :
        # if not isinstance(path, str) :
        #   path = path
        callback(formatPath(path))

def ShowInfoDialog(msg, title='Tips', level=0) :
    '''显示一个按钮的消息框。
    level:
        0 showinfo
        1 showwarning
        2 showerror
    '''
    if level not in (0, 1, 2) :
        level = 0
    if level == 0 :
        return messageBox.showinfo(title = title, message = msg)
    elif level == 1 :
        return messageBox.showwarning(title = title, message = msg)
    elif level == 2 :
        return messageBox.showerror(title = title, message = msg)

def ShowAskDialog(msg, title = 'Asking', kind='yn') :
    '''显示有Yes，NO两个选项的提示框。
    kind:
        'q'         按钮: 是 否          返回值: 'yes' 'no'
        'oc'        按钮: 确定 取消      返回值: True False
        'yn'        按钮: 是 否          返回值: True False
        'rc'        按钮: 重试 取消      返回值: True False
        'ync'       按钮: 是 否 取消      返回值: True False None
    '''
    if kind not in ('q', 'oc', 'yn', 'rc', 'ync') :
        kind = 'yn'
    if kind == 'q' :
        return messageBox.askquestion(title = title, message = msg)
    elif kind == 'oc' :
        return messageBox.askokcancel(title = title, message = msg)
    elif kind == 'yn' :
        return messageBox.askyesno(title = title, message = msg)
    elif kind == 'rc' :
        return messageBox.askretrycancel(title = title, message = msg)
    elif kind == 'ync' :
        return messageBox.askyesnocancel(title = title, message = msg)

def isTkWidget(widget) :
    '''返回widget是否是tk.Widget实例
    '''
    return isinstance(widget, tk.Widget)

def isTK(widget) :
    '''返回widget是否是TK实例
    '''
    return isinstance(widget, tk.Tk)

def getToplevel(widget) :
    '''获取tk(ttk) widget的Toplevel(根节点)
    '''
    if isTkWidget(widget) :
        return widget.winfo_toplevel()
    elif isTK(widget) or isinstance(widget, tk.Toplevel) :
        return widget

    return None

def centerToplevel(widget) :
    '''将给定widget的Toplevel移到屏幕中央
    最好是在UI布局完成后调用
    '''
    top = getToplevel(widget)
    if top :
        top.update()
        topH = max(top.winfo_reqheight(), top.winfo_height())
        topW = max(top.winfo_reqwidth(), top.winfo_width())
        screenW, screenH = top.maxsize()
        top.geometry('+%d+%d'%((screenW-topW)/2, (screenH-topH)/2))

def getScreenSize(widget) :
    '''通过widget获取屏幕大小（toplevel的最大大小）
    '''
    top = getToplevel(widget)
    if top :
        return top.maxsize()

__quitHandleFuncs = {}
def handleToplevelQuit(widget, callback) :
    '''弃用，直接复写 destroy 方法即可
    捕获给定widget的Toplevel的关闭事件。当Toplevel关闭时调用callback'''
    top = getToplevel(widget)

    funcs = __quitHandleFuncs.get(str(top))
    if funcs is None :
        funcs = []
    if not callback in funcs :
        funcs.append(callback)
    __quitHandleFuncs[str(top)] = funcs

    def quit(*args, **dArgs) :
        for f in funcs :
            if isFunc(f) :
                f()
        if __quitHandleFuncs.get(str(top)) :
            del __quitHandleFuncs[str(top)]
        top.destroy()

    if top is not None and isFunc(callback) :
        top.protocol('WM_DELETE_WINDOW', quit)

def startTk(viewCotr, *args, **dArgs) :
    '''传入tk.View的子类构造函数（类名）和除parent之外的参数启动一个tk窗口
如:   startTk(GetDirWidget,  u'选择路径', 'test')
额外参数：
    size： 窗口大小, 以x分割的字符串, 如：500x500
    title: 窗口title,字符串
    menu: 顶部menu,详情见:getMenu方法
'''
    root = None
    if DND :
        root = DND()
    else :
        root = tk.Tk()
    root.withdraw()

    # size = tryGetDictValue(dArgs, 'size', delete=True)
    size = tryGetDictValue(dArgs, 'size', delete=True)
    if size :
        root.geometry(size)
    title = tryGetDictValue(dArgs, 'title', delete=True)
    if title :
        root.title(title)
    menu = tryGetDictValue(dArgs, 'menu', delete=True)
    if menu :
        root.config(menu=getMenu(root, *menu))
    app = viewCotr(root, *args, **dArgs)
    # app.loadConfigs('config/projConfig.json')
    app.pack(fill=tk.BOTH, expand=True)
    centerToplevel(app)
    app.focus_set()
    root.update_idletasks()
    root.deiconify()
    root.mainloop()

def getMenu( root, *conf ) :
    '''获取menu，如果有绑定热键mac上使用command键代替Ctrl
有子菜单的暂不支持热键设置
不建议在右键菜单中使用热键
示例：
    conf = (
        ('1', (
                ('1-1', __test1),
                ('1-2', __test2),
                'line',
                ('3', (
                        ('3-1', __test1),
                        ('3-2', __test2),
                    )
                ),
            )
        ),
        ('2', (
                ('2-1', __test1, 'Ce'),
                ('2-2', __test2),
            )
        ),
    )
    root = getToplevel(m)
    menu = getMenu(m, *conf)
    root.config(menu=menu)

    m: Frame等Tk控件
    '''
    def isLoT(obj) :
        return isinstance(obj, list) or isinstance(obj, tuple)
    def __getMenu(root, menuRoot, *conf) :
        if menuRoot is None :
            menuRoot = tk.Menu(root)
        if isLoT(conf) :
            c1 = conf[0]
            if isStr(c1) and len(conf) > 1:
                label = c1
                c2 = conf[1]
                l = len(conf)

                if isFunc(c2) :
                    accelerator = None
                    bindCom = None
                    if l == 3 :
                        bindCom, accelerator = getHotKeyCommandName(conf[2], True)
                    elif l == 4 :
                        bindCom = conf[2]
                        accelerator = conf[3]
                    if bindCom :
                        label = '{: <32}'.format(c1)
                    menuRoot.add_command(label=label, command=c2, accelerator=accelerator)
                    if bindCom :
                        getToplevel(root).bind(bindCom, c2)

                elif isLoT(c2) :
                    subMenu = __getMenu(root, None, *(c2))
                    if subMenu :
                        menuRoot.add_cascade(label=label, menu=subMenu)
                else :
                    menuRoot.add_separator()
            elif isLoT(c1) :
                for c in conf :
                    if isLoT(c) :
                        __getMenu(root, menuRoot, *c)
                    else :
                        menuRoot.add_separator()
            else :
                menuRoot.add_separator()
        else :
            raise Exception('conf wrong exception')
        return menuRoot

    return __getMenu(root, None, *conf)


def getHotKeyCommandName(com, macUseCommand=False) :
    '''将简单的快捷键转换成bind函数的事件,
参数：
    com：传入的值
    macUseCommand：mac 上是否使用command键替换Ctrl键
返回值：bindCommand, accelerator
    bindCommand: bind方法事件名
    accelerator: 各平台的按键提示
转换规则如下:
C:      Ctrl
A:      Alt
S:      Shift
E:      Escape
U:      Up
D:      Down
L:      Left
R:      Right
*:      AnyKey
W:      鼠标滚轮
(B\\d) :  鼠标1~3
(F\\d+) :   F1~F12
([a-z]) :    a-z
示例：
    win32平台：
    c, a = getHotKeyCommandName(CaF2)
    c: '<Control-KeyRelease-F2-KeyRelease-a>'
    a: 'Ctrl+F2+A'

keysym文档：
http://www.tcl.tk/man/tcl8.4/TkCmd/keysyms.htm
    '''
    import re
    patterns = None
    separator = '+'
    if isWindows() or isMac() :
        patterns = {
            'C' : ('Control', 'Ctrl'),
            'S' : ('Shift', 'Shift'),
            'A' : ('Alt', 'Alt'),
            'E' : ('KeyRelease-Escape', 'Escape'),
            'U' : ('Up', 'Up'),
            'D' : ('Down', 'Down'),
            'L' : ('Left', 'Left'),
            'R' : ('Right', 'Right'),
        }
    # # mac 会自动将 Ctrl、Alt、Shift、Escape、Command 等替换为⌃、⇧、⌥、⎋、⌘，不需要手动转换
    # elif isMac() :
    #     # separator = ''
    #     patterns = {
    #         'C' : ('Control', u'\u2303'),         # 符号 ⌃
    #         'S' : ('Shift', u'\u21e7'),           # 符号 ⇧
    #         'A' : ('Alt', 'Alt'),                 # 符号 ⌥
    #         'E' : ('Escape', u'\u238b'),     # 符号 ⎋
    #     }
    else :
        ShowInfoDialog('only support for win32 and Mac！！！')

    if isMac() and macUseCommand :
        # mac上⌘键使用 Mod1或者 M1 代替，
        # 见https://stackoverflow.com/questions/16379877/how-to-get-tkinter-mac-friendly-menu-shortcuts-cmdkey
        patterns['C'] = ('M1', 'Command')

    upPatters = (
        (r'B(\d)', 'Button-', 'M_'),
        r'(F\d+)',
        r'([a-z]{1})'
    )

    command = []
    accelerator = []

    if patterns :
        patterns['*'] = ('Any-KeyRelease', '*')
        patterns['W'] = ('MouseWheel', 'Scroll')

        for k in list(patterns.keys()) :
            c, a = patterns.get(k)
            # m = re.search(k, com)
            if com.find(k) >= 0 :
                command.append(c)
                accelerator.append(a)

        for k in upPatters :
            if isinstance(k, tuple) or isinstance(k, list) :
                mc = re.findall(k[0], com)
                for v in mc :
                    command.append(k[1]+v)
                    # print()
                    # v = v.upper()
                    accelerator.append(k[2]+v)
            else :
                mc = re.findall(k, com)
                for v in mc :
                    command.append('KeyRelease-'+v)
                    v = v.upper()
                    accelerator.append(v)

    return '<%s>'%'-'.join(command), separator.join(accelerator) # .encode('utf-8')

def setMenu2Top(widget, *menu) :
    root = getToplevel(widget)
    if root :
        root.config(menu=getMenu(root, *menu))

# ==================鼠标Enter提示Label  begin----------------
class __ToolTip(object) :
    def __init__(self, widget) :
        self.widget = widget
        self.tipwindow = None
        self.x = self.y = 0

    def showtip(self, **labelConfig) :
        "Display text in tooltip window"
        if self.tipwindow :
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx()
        y = y + cy + self.widget.winfo_rooty() - 50
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))

        keys = list(labelConfig.keys())

        if 'bg' not in keys and 'background' not in keys :
            labelConfig['bg'] = '#aaaaff'
        label = tk.Label(tw, **labelConfig)
        label.pack(ipadx=1)

    def hidetip(self) :
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def regEnterTip(widget, **labelConfig) :
    '''regEnterTip(widget, **labelConfig)
    给widget注册事件，当鼠标移到widget中时显示toolTip
    labelConfig 是tk.Label的构造参数，如：text='toolTip', bg = '#aaaaff'
    '''
    toolTip = __ToolTip(widget)
    def enter(event) :
        toolTip.showtip(**labelConfig)
    def leave(event) :
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
# ----------------鼠标Enter提示Label  end==================

# ----------------鼠标拖拽相关  beign==================
def bindDragTargetFuncs(widget, *dragTypes, drop=None, dropEnter=None, dropPosition=None, dropLeave=None) :
    '''dragType包含"DND_Text","DND_Files","*"等，回调函数参数event， 必须返回event.action'''
    try:
        if DND and isTkWidget(widget) :
            widget.drop_target_register(*dragTypes)
            if isFunc(dropEnter) :
                widget.dnd_bind('<<DropEnter>>', dropEnter)
            if isFunc(dropPosition) :
                widget.dnd_bind('<<DropPosition>>', dropPosition)
            if isFunc(dropLeave) :
                widget.dnd_bind('<<DropLeave>>', dropLeave)
            if isFunc(drop) :
                widget.dnd_bind('<<Drop>>', drop)
    except Exception as e:
        print(u'If you want use TkinterDnD functions using startTk(...) to start a application instead of tk.TK() ')

def bindDragSourceFuncs(widget, *dragTypes, button=1, dragInit=None, drop=None, dropEnter=None, dropPosition=None, dropLeave=None, dragEnd=None) :
    '''button是鼠标按键值，1是左键，2是中键或滚轮，3是右键；
dragType包含"DND_Text","DND_Files","*"等，
回调函drop和dropxxx数参数event， 必须返回event.action
dragInit必须实现，返回一个三元组:(dndActions, dndTypes, data),其中每个元组都是字符串或字符串组成的元组，data是拖动的控件对应的数据（文件名等，自定义）
dndActions包含"ask", "copy", "move", "link", "none"等
'''
    try :
        if DND and isTkWidget(widget) :
            widget.drag_source_register(button, *dragTypes)
            if isFunc(dropEnter) :
                widget.dnd_bind('<<DropEnter>>', dropEnter)
            if isFunc(dropPosition) :
                widget.dnd_bind('<<DropPosition>>', dropPosition)
            if isFunc(dropLeave) :
                widget.dnd_bind('<<DropLeave>>', dropLeave)
            if isFunc(drop) :
                widget.dnd_bind('<<Drop>>', drop)
            if isFunc(dragInit) :
                widget.dnd_bind('<<DragInitCmd>>', dragInit)
            if isFunc(dragEnd) :
                widget.dnd_bind('<<DragEndCmd>>', dragEnd)
    except Exception as e :
        print(u'If you want use TkinterDnD functions using startTk(...) to start a application instead of tk.TK() ')

# ----------------鼠标拖拽相关  end==================
#

# ---------------------------------------------test begin --------------------------------------------------

def __testHandleToplevelQuit() :
    f = ttk.Frame()
    f.grid()

    l = ttk.Label(f, text='test')
    f.grid()

    def handleF() :
        print('f')

    def handleL() :
        print('l')

    handleToplevelQuit(f, handleF)
    handleToplevelQuit(l, handleL)

    f.mainloop()

def __testAskFile() :
    def func(*args, **dArgs) :
        print(args, dArgs)
    ShowChooseFileDialog(func)
    ShowChooseFileDialog(func, True)
    # ShowAskDialog('test')

def __testGetDirWid() :
    root = tk.Tk()
    v = GetDirWidget(root, '选择路径', 'test', mustexist=False)
    v.pack(expand=tk.YES, fill=tk.BOTH)
    centerToplevel(v)
    v.setUpMsg('=====================setUpMsg=====================')
    v.setValue('=====================setValue=====================')
    v.setTitle('setTitle')
    v.mainloop()
    # startTk(GetDirWidget,  u'选择路径', 'test')

def __testGetFileWid() :
    startTk(GetFileWidget,  u'选择路径', 'test')

def __testCenterTop() :
    app = tk.Tk()
    centerToplevel(app)
    app.mainloop()

def __testMenu(useStartTk=False) :
    '''测试程序菜单栏菜单和右键菜单'''
    def __test1(event=None) :
        print('test1')

    def __test2(event=None) :
        print('test2')

    conf = (
        ('1', (
                ('1-1', __test1, 'CU'),
                ('1-2', __test2),
                'line',
                ('3', (
                        ('3-1', __test1),
                        ('3-2', __test2),
                    )
                ),
            )
        ),
        ('2', (
                ('2-1', __test1, 'Ce'),
                ('2-2', __test2),
            )
        ),
    )

    if useStartTk :
        startTk(tk.Frame, size='400x300', menu=conf)
    else :
        m = tk.Frame()
        root = getToplevel(m)
        root.title(u'菜单测试')
        menu = getMenu(m, *conf)
        root.config(menu=menu)

        def onClickRight(event) :
            getMenu(root, *conf).post(event.x_root, event.y_root)
        root.bind('<Button-3>', onClickRight)

        menu.mainloop()

def __testMenu2() :
    __testMenu(True)

def __testChooseFiles() :
    # ShowChooseFileDialog(lambda x : print(type(x)), True)
    ShowChooseFileDialog(print, True)


def __main() :
    # __testAskFile()
    # __testHandleToplevelQuit()
    # __testGetDirWid()
    # __testGetFileWid()
    # __testCenterTop()
    # __testMenu()
    __testMenu2()
    # __testChooseFiles()

if __name__ == '__main__':
    __main()

# ============================================test end ===========================================