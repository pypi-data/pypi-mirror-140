# -*- coding:utf-8 -*-
# 创建时间：2019-03-01 11:42:00
# 创建人：  Dekiven

import os
from DKVTools.Funcs import *
from CommonWidgets import *

tk, ttk = getTk()


class InfoProgressBar(ttk.Frame) :
    '''InfoProgressBar configure keys: ('cursor', 'length', 'maximum', 'mode', 'orient', 'style', 'takefocus')
    '''
    def __init__(self, *args, **dArgs) :
        deleteKeys = ('cursor', 'length', 'maximum', 'mode', 'orient', 'style', 'takefocus')
        newArgs = {}
        for key in deleteKeys :
            if key in list(dArgs.keys()) :
                v = dArgs.pop(key)
                if v :
                    newArgs[key] = v
        ttk.Frame.__init__(self, *args, **dArgs)

        self.confKeys = deleteKeys

        label = ttk.Label(self, text='', justify=tk.CENTER)
        label.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.CENTER, padx=10, pady=1)
        self.label = label

        pbv = tk.DoubleVar()
        self.pbv = pbv
        pb = ttk.Progressbar(self, variable=pbv, **newArgs)
        pb.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH, padx=10, pady=5)
        self.pb = pb

    def start(self, interval=None) :
        '''一个调整的间隔，单位毫秒， 默认50'''
        self.pb.start(interval or 50)

    def step(self, delta=None) :
        '''每次调整的步长'''
        self.pb.step(delta or 1)

    def stop(self) :
        self.pb.stop()

    def setPercent(self, value) :
        '''设置当前进度,同setValue'''
        self.pbv.set(value)

    def getPercent(self) :
        '''获取当前进度,同getValue'''
        return self.pbv.get()

    def setInfo(self, info) :
        self.label.configure(text=info)

    def config(self, **conf) :
        for k in list(conf.keys()) :
            if k not in self.confKeys :
                conf.pop(k)
                raise NameError('InfoProgressBar has not attribute named :'+k)
        self.pb.configure(**conf)

    def setDeterminate( self, value ) :
        '''设置是否是进步样式，选择否就是来回反弹样式'''
        if value :
            self.config(mode='determinate')
        else :
            self.config(mode='indeterminate')

    def setIsVertical( self, value ) :
        self.config(orient= 'vertical' if value else 'horizontal')

    def setValue( self, value ) :
        '''设置当前进度'''
        self.pbv.set(value)

    def getValue( self ) :
        '''获取当前进度'''
        return self.pbv.get()

    def setMaxValue( self, value ) :
        '''设置最大进度'''
        self.config(maximum=value)

def __main() :
    m = InfoProgressBar(None, mode='determinate')
    m.pack(expand=tk.YES,fill=tk.BOTH)
    m.setInfo('hhhhhhhhhhhhhh')
    # m.setPercent(80)
    m.config(mode='indeterminate')
    m.step(90)
    m.setIsVertical(True)
    m.start(50)
    m.mainloop()

if __name__ == '__main__' :
    __main()
