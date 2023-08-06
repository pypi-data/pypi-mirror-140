import matplotlib
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter.colorchooser import *
import pandas as pd
import numpy as np

config = {
    "font.family": 'serif', # 衬线字体
    "font.size": 12, # 相当于小四大小
    "font.serif": ['SimSun'], # 宋体
    "mathtext.fontset": 'stix', # matplotlib渲染数学字体时使用的字体，和Times New Roman差别不大
    'axes.unicode_minus': False # 处理负号，即-号
}
plt.rcParams.update(config)

class Figs():
    def __init__(self):
        self.fig,self.ax=plt.subplots()
    def Configure(self):
        self.config={
            "title":{"header":"图表标题","size":14,"loc":"center"},
            "plot_type":{"折线图":self.ax.plot,"散点图":self.ax.scatter,"柱状图":self.ax.bar},
            "current_type":["折线图"],
            "border_display":False,
            "label":["Fig-1"],
            "axis_label":{"xlabel":"x轴标签","ylabel":"y轴标签"},
            "axis_font":{"size":10},
            "tick":{"labelsize":10,"direction":"out"},
            "grid":{"display":False,"axis":"both"},
            "xlim":{"xmin":np.array(self.x.min())-1,"xmax":np.array(self.x.max())+1},
            "ylim":{"ymin":np.array(self.y.min())-1,"ymax":np.array(self.y.max())+1},
            "fig_size":{"width":6,"height":4},
            "legend_display":False,
            "axis_pos":False,
            "log_ax":False,
            "text":{"creat_text":False,"x":0,"y":0,"x0":0,"y0":0,"text":""}
            }
    def First(self,master:ttk.Window,x,y,z=None):
        self.root=master
        self.root.title("绘图")
        self.posx_top=400
        self.posy_top=250
        self.root_xsize=1200
        self.root_ysize=1100
        self.posx_right=self.posx_top+self.root_xsize
        #self.posy_bot=self.posy_top+self.root_ysize
        self.root.geometry("{}x{}+{}+{}".format(self.root_xsize,self.root_ysize,self.posx_top,self.posy_top))
        self.x=x
        self.y=y
        self.z=z
        self.filePath = ttk.StringVar()
        self.Configure()
        self.Setting(self.x.shape[1])
        self.init_type(self.x.shape[1])
        self.fig.set_figheight(self.config["fig_size"]["height"])
        self.fig.set_figwidth(self.config["fig_size"]["width"])
    def run(self):
        self.init()
        #post_data=self.po
        self.draw(self.post_data)
        self.Layout()
    def show_menu(self,event):
        self.menu.post(event.x_root, event.y_root)
        self.config["text"]["x"]=0.0011*event.x-0.18
        self.config["text"]["y"]=-0.00181818*event.y+1.1272727272727274
        self.config["text"]["x0"]=event.x_root
        self.config["text"]["y0"]=event.y_root
        print(event.x,event.y)
    def init(self):
        frame1=ttk.LabelFrame(self.root,text="O",width=400,height=250,labelanchor="ne")
        self.canvs = FigureCanvasTkAgg(self.fig, frame1)
        self.canvs.get_tk_widget().pack(side=TOP,fill=X,pady=(5,50))
        self.menu = ttk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="打开文件",command=self.openfile)
        self.menu.add_separator()
        self.menu.add_command(label="绘图类型",command=lambda :self.Type())
        self.menu.add_separator()
        self.menu.add_command(label="绘图设置",command=lambda :self.init_top())
        self.menu.add_separator()
        self.menu.add_command(label="添加文本",command=lambda :self.text_top())
        self.root.bind("<Button-3>",self.show_menu)
        frame1.pack(side=TOP,fill=X)
    def change_figure(self,par1,inpar1,par2=None):
        #print(inpar1)
        if not par2:
            self.config[par1]=inpar1
        else:
            self.config[par1][par2]=inpar1
        post_data=self.post_data
        self.draw(post_data)
    def change_figure_list(self,par1,inpar1,par2):
        self.config[par1][par2]=inpar1
        #print(self.config["current_type"])
        post_data=self.post_data
        self.draw(post_data)
    def Data_open(self,filename):
        try:
            f1=pd.read_csv(filename)
            x=[]
            y=[]
            for i in f1.columns:
                if "x" in i:
                    x.append(i)
                if "y" in i:
                    y.append(i)
            if len(x)==len(y):
                self.x=f1[x]
                self.y=f1[y]
                self.config["xlim"]["xmin"]=np.array(f1[x]).reshape(1,-1).min()-1
                self.config["xlim"]["xmax"]=np.array(f1[x]).reshape(1,-1).max()+1
                self.config["ylim"]["ymin"]=np.array(f1[y]).reshape(1,-1).min()-1
                self.config["ylim"]["ymax"]=np.array(f1[y]).reshape(1,-1).max()+1
                self.config["current_type"]=["折线图" for i in range(len(x))]
                self.config["title"]={"header":"图表标题","size":14,"loc":"center"}
                self.config["axis_label"]={"xlabel":"x轴标签","ylabel":"y轴标签"}
                self.config["text"]={"creat_text":False,"x":0,"y":0,"x0":0,"y0":0,"text":""}
                #self.Configure()
            else:
                print("数据维度不匹配")
            
        except:
            print("数据读取失败")
    def openfile(self):
        file=tk.filedialog.askopenfilename(filetypes=[("csv", ".csv"),("txt",".txt")])
        if(file != ''):
            self.filePath=file
            self.Data_open(self.filePath)
        self.Setting(self.x.shape[1])
        self.init_type(self.x.shape[1])
        post_data=self.post_data
        self.draw(post_data)
    def savepic(self):
        fname = tk.filedialog.asksaveasfilename(title=u'保存文件', filetypes=[("PNG", ".png"),("JPG", ".jpg"),("SVG",".svg")])
        plt.savefig("{}".format(fname))
    def showabout(self):
        self.topa = ttk.Toplevel()
        self.topa.title('About')
        self.topa.geometry("800x500+{}+{}".format(self.root.winfo_x()+self.root_xsize+2,self.root.winfo_y()))
        ttk.Label(self.topa,text="这是一个软件").pack()
    def Layout(self):
        menubar = ttk.Menu(self.root)
        filemenu = ttk.Menu(menubar, tearoff=False)
        filemenu.add_command(label="打开",command=self.openfile)
        filemenu.add_command(label="输出",command=self.savepic)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=filemenu)

        plot_type= ttk.Menu(menubar, tearoff=False)
        plot_type.add_command(label="关于",command=self.showabout)
        menubar.add_cascade(label="其他", menu=plot_type)

        self.root.config(menu=menubar)
        frame2=ttk.Frame(self.root)
        title=ttk.Entry(frame2,width=30)
        ttk.Label(frame2,text="标题:").grid(row=0,column=0,sticky=W)
        title.grid(row=0,column=1,columnspan=3,sticky=(W+E))
        title.bind("<Return>",lambda a:self.change_figure(par1="title",inpar1=title.get(),par2="header"))

        title_size=ttk.Entry(frame2,width=10)
        ttk.Label(frame2,text="标题尺寸:").grid(row=0,column=4)
        title_size.grid(row=0,column=5,sticky=(W+E))
        title_size.bind("<Return>",lambda a:self.change_figure(par1="title",inpar1=title_size.get(),par2="size"))

        ttk.Label(frame2,text="x轴标签:").grid(row=1,column=0,sticky=W)
        xlabel=ttk.Entry(frame2,width=10)
        xlabel.grid(row=1,column=1,sticky=W)
        xlabel.bind("<Return>",lambda a:self.change_figure(par1="axis_label",inpar1=xlabel.get(),par2="xlabel"))

        ttk.Label(frame2,text="y轴标签:").grid(row=1,column=2,sticky=E)
        ylabel=ttk.Entry(frame2,width=10)
        ylabel.grid(row=1,column=3,sticky=E)
        ylabel.bind("<Return>",lambda a:self.change_figure(par1="axis_label",inpar1=ylabel.get(),par2="ylabel"))

        ttk.Label(frame2,text="标签尺寸:").grid(row=1,column=4,sticky=E)
        label_size=ttk.Entry(frame2,width=10)
        label_size.grid(row=1,column=5,sticky=E)
        label_size.bind("<Return>",lambda a:self.change_figure(par1="axis_font",inpar1=label_size.get(),par2="size"))

        ttk.Label(frame2,text="Xmin:").grid(row=2,column=0,sticky=W)
        xmin=ttk.Entry(frame2,width=10)
        xmin.grid(row=2,column=1,sticky=W)
        xmin.bind("<Return>",lambda a:self.change_figure(par1="xlim",inpar1=float(xmin.get()),par2="xmin"))

        ttk.Label(frame2,text="Xmax:").grid(row=2,column=2,sticky=E)
        xmax=ttk.Entry(frame2,width=10)
        xmax.grid(row=2,column=3,sticky=E)
        xmax.bind("<Return>",lambda a:self.change_figure(par1="xlim",inpar1=float(xmax.get()),par2="xmax"))

        ttk.Label(frame2,text="Ymin:").grid(row=3,column=0,sticky=W)
        ymin=ttk.Entry(frame2,width=10)
        ymin.grid(row=3,column=1,sticky=W)
        ymin.bind("<Return>",lambda a:self.change_figure(par1="ylim",inpar1=float(ymin.get()),par2="ymin"))

        ttk.Label(frame2,text="Ymax:").grid(row=3,column=2,sticky=E)
        ymax=ttk.Entry(frame2,width=10)
        ymax.grid(row=3,column=3,sticky=E)
        ymax.bind("<Return>",lambda a:self.change_figure(par1="ylim",inpar1=float(ymax.get()),par2="ymax"))

        ttk.Label(frame2,text="刻度尺寸:").grid(row=2,column=4,sticky=E)
        lim_size=ttk.Entry(frame2,width=10)
        lim_size.grid(row=2,column=5,sticky=E)
        lim_size.bind("<Return>",lambda a:self.change_figure(par1="tick",inpar1=float(lim_size.get()),par2="labelsize"))

        dir_var=ttk.StringVar()
        ttk.Label(frame2,text="刻度方向:").grid(row=3,column=4,sticky=W)
        lim_dir=ttk.Checkbutton(frame2,bootstyle="success-round-toggle",onvalue="in",offvalue="out",variable=dir_var,command=lambda :self.change_figure(par1="tick",inpar1=dir_var.get(),par2="direction"))
        lim_dir.grid(row=3,column=5)

        border_var=ttk.BooleanVar()
        ttk.Label(frame2,text="上/右边框:").grid(row=4,column=0,sticky=W)
        border_display=ttk.Checkbutton(frame2,bootstyle="success-round-toggle",onvalue=True,offvalue=False,variable=border_var,command=lambda :self.change_figure(par1="border_display",inpar1=border_var.get()))
        border_display.grid(row=4,column=1)

        grid_var=ttk.BooleanVar()
        ttk.Label(frame2,text="网格:").grid(row=4,column=2,sticky=E)
        grid_display=ttk.Checkbutton(frame2,bootstyle="success-round-toggle",onvalue=True,offvalue=False,variable=grid_var,command=lambda :self.change_figure(par1="grid",inpar1=grid_var.get(),par2="display"))
        grid_display.grid(row=4,column=3)

        lengend_display_var=ttk.BooleanVar()
        ttk.Label(frame2,text="标签:").grid(row=4,column=4,sticky=E)
        lengend_display=ttk.Checkbutton(frame2,bootstyle="success-round-toggle",onvalue=True,offvalue=False,variable=lengend_display_var,command=lambda :self.change_figure(par1="legend_display",inpar1=lengend_display_var.get()))
        lengend_display.grid(row=4,column=5)
        frame2.pack(pady=20)

        axis_pos_var=ttk.BooleanVar()
        ttk.Label(frame2,text="坐标轴处于原点:").grid(row=5,column=0,sticky=W)
        axis_pos=ttk.Checkbutton(frame2,bootstyle="success-round-toggle",onvalue=True,offvalue=False,variable=axis_pos_var,command=lambda :self.change_figure(par1="axis_pos",inpar1=axis_pos_var.get()))
        axis_pos.grid(row=5,column=1)
        frame2.pack(side=TOP,pady=20)
        log_var=ttk.BooleanVar()
        ttk.Label(frame2,text="对数坐标:").grid(row=5,column=2,sticky=E)
        log_cor=ttk.Checkbutton(frame2,bootstyle="success-round-toggle",onvalue=True,offvalue=False,variable=log_var,command=lambda :self.change_figure(par1="log_ax",inpar1=log_var.get()))
        log_cor.grid(row=5,column=3)
        frame2.pack(side=TOP,pady=20)

    def draw(self,post_data):
        #post_data=self.st.post_data
        figname=list(post_data.keys())
        figname_sc=list(self.post_scatter.keys())
        #print(self.post_scatter)
        #print(self.y.iloc[:,0:1])
        self.ax.clear()
        #self.fig.set_figheight(self.config["fig_size"]["height"])
        #self.fig.set_figwidth(self.config["fig_size"]["width"])
        self.ax.set_title(label=self.config["title"]["header"],fontdict={'size':self.config["title"]["size"]},loc = self.config["title"]["loc"])
        #(self.x.shape)
        for i in range(self.x.shape[1]):
            x_=np.array(self.x.iloc[:,i:i+1])
            y_=np.array(self.y.iloc[:,i:i+1])
            if self.post_type[i]=="折线图":
                if post_data[figname[i]][3]=="无":
                    self.config["plot_type"]["折线图"](x_,y_,label=self.config["label"][i],linestyle=post_data[figname[i]][0],color=post_data[figname[i]][1],linewidth=post_data[figname[i]][2])
                else:
                    self.config["plot_type"]["折线图"](x_,y_,label=self.config["label"][i],
                    linestyle=post_data[figname[i]][0],color=post_data[figname[i]][1],linewidth=post_data[figname[i]][2],marker=post_data[figname[i]][3],markersize=post_data[figname[i]][4])
            elif self.post_type[i]=="散点图":
                self.config["plot_type"]["散点图"](x_,y_,label=self.config["label"][i],marker=self.post_scatter[figname_sc[i]][0],c=self.post_scatter[figname_sc[i]][1],s=self.post_scatter[figname_sc[i]][2])
            elif self.post_type[i]=="柱状图":
                self.config["plot_type"]["柱状图"](x_,y_,label=self.config["label"][i],lw=2)
        self.ax.spines['right'].set_visible(self.config["border_display"])
        self.ax.spines['top'].set_visible(self.config["border_display"])
        self.ax.set_xlabel(self.config["axis_label"]["xlabel"],self.config["axis_font"])
        self.ax.set_ylabel(self.config["axis_label"]["ylabel"],self.config["axis_font"])
        self.ax.tick_params(labelsize=self.config["tick"]["labelsize"],direction=self.config["tick"]["direction"])
        self.ax.grid(visible=self.config["grid"]["display"],axis=self.config["grid"]["axis"])
        self.ax.set_xlim(xmin=self.config["xlim"]["xmin"],xmax=self.config["xlim"]["xmax"])
        self.ax.set_ylim(ymin=self.config["ylim"]["ymin"],ymax=self.config["ylim"]["ymax"])
        if self.config["text"]["creat_text"]:
            self.ax.text(self.config["text"]["x"],self.config["text"]["y"],self.config["text"]["text"],transform=self.ax.transAxes)
        if self.config["log_ax"]:
            self.ax.set_xscale("log")
            self.ax.set_yscale("log")
            print(self.config["xlim"]["xmin"],self.config["ylim"]["ymin"])
            if self.config["xlim"]["xmin"] >0 and self.config["ylim"]["ymin"]>0:
                self.ax.set_xlim(xmin=10**(np.log10(self.config["xlim"]["xmin"])),xmax=10**(np.log10(self.config["xlim"]["xmax"])))
                self.ax.set_ylim(ymin=10**(np.log10(self.config["ylim"]["ymin"])),ymax=10**(np.log10(self.config["ylim"]["ymax"])))
            elif self.config["xlim"]["xmin"]<=0 and self.config["ylim"]["ymin"]>0:
                self.ax.set_xlim(xmin=10**(-7),xmax=10**(np.log10(self.config["xlim"]["xmax"])))
                self.ax.set_ylim(ymin=10**(np.log10(self.config["ylim"]["ymin"])),ymax=10**(np.log10(self.config["ylim"]["ymax"])))
            elif self.config["xlim"]["xmin"]>0 and self.config["ylim"]["ymin"]<=0:
                self.ax.set_xlim(xmin=10**(np.log10(self.config["xlim"]["xmin"])),xmax=10**(np.log10(self.config["xlim"]["xmax"])))
                self.ax.set_ylim(ymin=10**(-7),ymax=10**(np.log10(self.config["ylim"]["ymax"])))
            else:
                self.ax.set_xlim(xmin=10**(-7),xmax=10**(np.log10(self.config["xlim"]["xmax"])))
                self.ax.set_ylim(ymin=10**(-7),ymax=10**(np.log10(self.config["ylim"]["ymax"])))
        axis = plt.gca()
        if  self.config["axis_pos"]:
            axis.spines['right'].set_color('none') 
            axis.spines['top'].set_color('none')
            axis.xaxis.set_ticks_position('bottom')   
            axis.yaxis.set_ticks_position('left')
            axis.spines['bottom'].set_position(('data', 0))
            axis.spines['left'].set_position(('data', 0))
        #self.ax.axis[:].set_visible(False)
        if self.config["legend_display"]:
            self.ax.legend()
        self.canvs.draw()
    def init_type(self,n):
        self.n=n
        self.plot_type=[["折线图","散点图","柱状图"] for i in range(self.n)]
        self.post_type=["折线图" for i in range(self.n)]
        self.frame=[]
        self.plottype_pos=[0 for i in range(self.n)]
        self.type_pos=[0 for i in range(self.n)]
        self.figlabels=["fig-{}".format(i+1) for i in range(self.n)]
        self.config["label"]=self.figlabels
        self.plot_type_cb=[]
        self.figname=[]
        self.lab_entry=[]
        for i in range(self.n):
            self.frame.append("frame{}".format(i))
            self.figname.append("Fig-{}".format(i+1))
            self.plot_type_cb.append("plottype_cb{}".format(i))
            self.lab_entry.append("lab_entry{}".format(i))
    def Type(self):
        try:
            self.top_type.destroy()
        except:
            pass
        try:
            self.top.destroy()
        except:
            pass
        self.top_type = ttk.Toplevel()
        self.top_type.title('Type SettIng')
        self.top_type.geometry("800x500+{}+{}".format(self.root.winfo_x()+self.root_xsize+2,self.root.winfo_y()))
        self.layouts()
    def layouts(self):
        for i in range(self.n):
            self.frame[i] = ttk.Frame(self.top_type,width=600,height=400)
            self.type_cbs(self.frame[i],self.plot_type[i],i)
            self.frame[i].pack(side=TOP,fill=BOTH)
    def combs_typee(self,ind):
        self.plottype_pos[ind]=self.plot_type[ind].index(self.plot_type_cb[ind].get())
        self.plot_type_cb[ind].current(self.plottype_pos[ind])
        self.post_type[ind]=self.plot_type_cb[ind].get()
        self.draw(self.post_data)
        #print(self.post_type)
    def type_cbs(self,master,plot_type,ind):
        ttk.Label(master,text="Fig-{}:".format(ind+1),bootstyle="info").grid(row=0,column=0,padx=20,pady=20)
        self.plot_type_cb[ind]=ttk.Combobox(
            master=master,
            values=plot_type,
            textvariable="",
            width=7
        )
        self.plot_type_cb[ind].current(self.plottype_pos[ind])
        self.plot_type_cb[ind].bind('<<ComboboxSelected>>',lambda e:self.combs_typee(ind))
        self.plot_type_cb[ind].grid(row=0,column=1)
        ttk.Label(master,text="标签:",bootstyle="info").grid(row=0,column=2,padx=20)
        self.lab_entry[ind]=ttk.Entry(master,text="",width=30)
        self.lab_entry[ind].grid(row=0,column=3)
        self.lab_entry[ind].bind("<Return>",lambda a:self.change_figure_list(par1="label",inpar1=self.lab_entry[ind].get(),par2=ind))
    def Setting(self,n_tab):
        self.n_tab=n_tab
        self.vals=[["-","--","-.",":"] for i in range(self.n_tab)]
        self.value_width=[[0.5,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0] for i in range(self.n_tab)]
        self.init_color=["red","black","green","blue","pink","yellow"]
        self.marker_val=[["无",".","o","v","^","<",">","s","*","x","D","d","p"] for i in range(self.n_tab)]
        self.marker_size=[[2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0,13.0,14.0] for i in range(self.n_tab)]
        #self.plot_type=[["折线图","散点图","柱状图"] for i in range(self.n_tab)]
        self.frame=[]
        #self.plottype_pos=[0 for i in range(self.n_tab)]
        self.lw_pos=[0 for i in range(self.n_tab)]
        self.type_pos=[0 for i in range(self.n_tab)]
        self.marker_pos=[0+i for i in range(self.n_tab)]
        self.marker_size_pos=[0 for i in range(self.n_tab)]
        #self.plot_type_cb=[]
        self.cb=[]
        self.c_but=[]
        self.cb_lw=[]
        self.figname=[]
        self.post_data={}
        self.marker_cb=[]
        self.markersize_cb=[]
        for i in range(self.n_tab):
            self.frame.append("frame{}".format(i))
            self.cb.append("cb{}".format(i))
            self.c_but.append("but{}".format(i))
            self.cb_lw.append("cb_lw{}".format(i))
            self.figname.append("Fig-{}".format(i+1))
            self.marker_cb.append("marker_cb{}".format(i))
            self.markersize_cb.append("markersize_cb{}".format(i))
            #self.plot_type_cb.append("plottype_cb{}".format(i))
        for i in range(self.n_tab):
            self.post_data[self.figname[i]]=['-',self.init_color[i],2,"无",8]
        ####散点图
        self.mark_types=[[".","o","v","^","<",">","s","*","x","D","d","p"] for i in range(self.n_tab)]
        self.mark_color=["red","black","green","blue","pink","yellow"]
        self.mark_size=[[2,3,4,5,6,7,8,9,10] for i in range(self.n_tab)]
        self.mark_type_cb=["mark_type_cb{}".format(i) for i in range(self.n_tab)]
        self.mark_type_pos=[0+i for i in range(self.n_tab)]
        self.mark_size_cb=["mark_size_cb{}".format(i) for i in range(self.n_tab)]
        self.mark_size_pos=[0 for i in range(self.n_tab)]
        self.mark_bt=["mark_bt{}".format(i) for i in range(self.n_tab)]
        self.post_scatter={}
        for i in range(self.n_tab):
            self.post_scatter[self.figname[i]]=[self.mark_types[0][i],self.mark_color[i],40]
    def init_top(self):
        try:
            self.top.destroy()
        except:
            pass
        try:
            self.top_type.destroy()
        except:
            pass
        self.top = ttk.Toplevel()
        self.top.title('Figure SettIng')
        self.top.geometry("800x500+{}+{}".format(self.root.winfo_x()+self.root_xsize+2,self.root.winfo_y()))
        self.layout()
    def layout(self):
        tab = ttk.Notebook(self.top,width=800,height=500)
        
        for i in range(self.n_tab):
            self.frame[i] = ttk.Frame(tab,width=600,height=400)
            tab.add(self.frame[i], text = self.figname[i])
            if self.post_type[i]=="折线图":
                self.ZXT(self.frame[i],self.vals[i],self.value_width[i],self.marker_val[i],self.marker_size[i],i)
            if self.post_type[i]=="散点图":
                self.SDT(self.frame[i],self.mark_types[i],self.mark_size[i],i)
        tab.pack(expand = True)
    def Post_data(self):
        temp=self.post_data
        for i in range(self.n_tab):
            try:
                self.post_data[self.figname[i]]=[self.cb[i].get(),self.c_but[i]["bg"],self.cb_lw[i].get(),self.marker_cb[i].get(),self.markersize_cb[i].get()]
            except:
                self.post_data[self.figname[i]]=temp[self.figname[i]]

        #print(self.post_data)
    def displays(self,ind):
        cb=askcolor()
        self.c_but[ind].configure(bg=cb[1])
        self.Post_data()
        self.draw(self.post_data)
        self.init_color[ind]=cb[1]
    def combs_lw(self,ind):
        #print(self.cb_lw[ind].get())
        self.lw_pos[ind]=self.value_width[ind].index(float(self.cb_lw[ind].get()))
        self.cb_lw[ind].current(self.lw_pos[ind])
        self.Post_data()
        self.draw(self.post_data)

    def ZXT(self,master,val_line_type,val_line_wid,marker_type,marker_size,ind):

        ttk.Label(master,text="线型:").grid(row=1,column=0,padx=20,pady=20)
        self.cb[ind]=ttk.Combobox(
            master=master,
            values=val_line_type,
            textvariable="",
            width=5
        )
        self.cb[ind].current(self.type_pos[ind])
        self.cb[ind].bind('<<ComboboxSelected>>',lambda e:self.combs(ind))
        self.cb[ind].grid(row=1,column=1)
        ttk.Label(master,text="颜色:").grid(row=2,column=0,padx=20,pady=20)
        self.c_but[ind]=tk.Button(master,text="",width=7,command=lambda :self.displays(ind))
        self.c_but[ind].configure(bg=self.init_color[ind])
        self.c_but[ind].grid(row=2,column=1)
        ttk.Label(master,text="粗细:").grid(row=3,column=0,padx=20,pady=20)
        self.cb_lw[ind]=ttk.Combobox(
            master=master,
            values=val_line_wid,
            textvariable="",
            width=5
        )
        self.cb_lw[ind].current(self.lw_pos[ind])
        self.cb_lw[ind].bind('<<ComboboxSelected>>',lambda e:self.combs_lw(ind))
        self.cb_lw[ind].grid(row=3,column=1)
        ttk.Label(master,text="标记:").grid(row=4,column=0,padx=20,pady=20)
        self.marker_cb[ind]=ttk.Combobox(
            master=master,
            values=marker_type,
            textvariable="",
            width=5
        )
        self.marker_cb[ind].current(self.marker_pos[ind])
        self.marker_cb[ind].bind('<<ComboboxSelected>>',lambda e:self.combs_marker(ind))
        self.marker_cb[ind].grid(row=4,column=1)
        ttk.Label(master,text="标记尺寸:").grid(row=5,column=0,padx=20,pady=20)
        self.markersize_cb[ind]=ttk.Combobox(
            master=master,
            values=marker_size,
            textvariable="",
            width=5
        )
        self.markersize_cb[ind].current(self.marker_size_pos[ind])
        self.markersize_cb[ind].bind('<<ComboboxSelected>>',lambda e:self.combs_marker_size(ind))
        self.markersize_cb[ind].grid(row=5,column=1)
    def combs(self,ind):
        #print(self.cb[ind].get())
        self.type_pos[ind]=self.vals[ind].index(self.cb[ind].get())
        self.cb[ind].current(self.type_pos[ind])
        self.Post_data()
        self.draw(self.post_data)
    def combs_marker(self,ind):
        self.marker_pos[ind]=self.marker_val[ind].index(self.marker_cb[ind].get())
        self.marker_cb[ind].current(self.marker_pos[ind])
        self.Post_data()
        self.draw(self.post_data)
    def combs_marker_size(self,ind):
        self.marker_size_pos[ind]=self.marker_size[ind].index(float(self.markersize_cb[ind].get()))
        self.markersize_cb[ind].current(self.marker_size_pos[ind])
        self.Post_data()
        self.draw(self.post_data)

        #散点图
    def SDT(self,master,mark_type,mark_sizetype,ind):
        ttk.Label(master,text="类型:").grid(row=1,column=0,padx=20,pady=20)
        self.mark_type_cb[ind]=ttk.Combobox(
            master=master,
            values=mark_type,
            textvariable="",
            width=5
        )
        self.mark_type_cb[ind].current(self.mark_type_pos[ind])
        self.mark_type_cb[ind].bind('<<ComboboxSelected>>',lambda e:self.scatter_type(ind))
        self.mark_type_cb[ind].grid(row=1,column=1)
        ttk.Label(master,text="颜色:").grid(row=2,column=0,padx=20,pady=20)
        self.mark_bt[ind]=tk.Button(master,text="",width=7,command=lambda :self.scatter_color(ind))
        self.mark_bt[ind].configure(bg=self.mark_color[ind])
        self.mark_bt[ind].grid(row=2,column=1)
        ttk.Label(master,text="尺寸:").grid(row=3,column=0,padx=20,pady=20)
        self.mark_size_cb[ind]=ttk.Combobox(
            master=master,
            values=mark_sizetype,
            textvariable="",
            width=5
        )
        self.mark_size_cb[ind].current(self.mark_size_pos[ind])
        self.mark_size_cb[ind].bind('<<ComboboxSelected>>',lambda e:self.scatter_size(ind))
        self.mark_size_cb[ind].grid(row=3,column=1)
    def Post_scatter(self):
        temp=self.post_scatter
        for i in range(self.n_tab):
            try:
                self.post_scatter[self.figname[i]]=[self.mark_type_cb[i].get(),self.mark_bt[i]["bg"],float(self.mark_size_cb[i].get())*10]
            except:
                self.post_scatter[self.figname[i]]=temp[self.figname[i]]
    def scatter_type(self,ind):
        self.mark_type_pos[ind]=self.mark_types[ind].index(self.mark_type_cb[ind].get())
        self.mark_type_cb[ind].current(self.mark_type_pos[ind])
        self.Post_scatter()
        #print(self.post_scatter)
        self.draw(self.post_data)
    def scatter_color(self,ind):
        cb=askcolor()
        self.mark_bt[ind].configure(bg=cb[1])
        self.mark_color[ind]=cb[1]
        self.Post_scatter()
        #print(self.post_scatter)
        self.draw(self.post_data)
        
    def scatter_size(self,ind):
        self.mark_size_pos[ind]=self.mark_size[ind].index(float(self.mark_size_cb[ind].get()))
        self.mark_size_cb[ind].current(self.mark_size_pos[ind])
        self.Post_scatter()
        #print(self.post_scatter)
        self.draw(self.post_data)
    def text_top(self):
        try:
            self.texttop.destroy()
        except:
            pass
        self.texttop = ttk.Toplevel()
        self.texttop.title('Text SettIng')
        self.texttop.geometry("800x500+{}+{}".format(self.config["text"]["x0"],self.config["text"]["y0"]))
        self.config["text"]["creat_text"]=True
        self.draw(self.post_data)
        ttk.Label(self.texttop,text="Text:").grid(row=0,column=0,sticky=W)
        text_en=ttk.Entry(self.texttop,width=30)
        text_en.grid(row=0,column=1,sticky=W)
        text_en.bind("<Return>",lambda a:self.change_figure(par1="text",inpar1=text_en.get(),par2="text"))
    
def start():
    x=np.linspace(0,10,50)
    y=np.sin(x)
    xy=pd.DataFrame([x,y]).T
    xy.columns=["x","y"]
    root = ttk.Window()
    root.resizable(width=False, height=False)
    fig=Figs()
    fig.First(master=root,x=pd.DataFrame(xy.x),y=pd.DataFrame(xy.y))
    fig.run()
    root.mainloop()
if __name__=="__main__":
    start()