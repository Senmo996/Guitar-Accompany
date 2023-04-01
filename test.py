import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinter import simpledialog
import os
import shutil
import pickle

class GuitarTrainerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Guitar Trainer")  #设置窗口标题
        self.master.geometry("800x600")      #设置窗口尺寸
        self.song_list = self.load_songs()   #读取歌曲清单
        self.selected_song = ""              #目前选中的歌曲
        self.song_tab = {}                   #每首歌的曲谱文件地址
        self.load_tabs()                     #读取每首歌的曲谱文件地址
        self.img_url = "./guitar accompany .png"      #当前显示的img图片地址

        # 添加全屏显示和退出全屏的功能
        # self.master.attributes('-fullscreen', True)
        
        # 添加一个按钮，用于退出全屏
        button_exit_fullscreen = tk.Button(self.master, text="Exit Fullscreen", command=self.exit_fullscreen)
        button_exit_fullscreen.pack()

        #添加按钮，用于添加歌曲
        self.add_tab_button = tk.Button(self.master, text="添加曲谱", command=self.add_tab)
        self.add_tab_button.pack(side="bottom", padx=10, pady=10)
        self.add_tab_button.config(state='disabled')

    
        # 创建一个包含两个Frame的Frame
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill="both", expand=True)

        # 创建左侧song_Frame
        self.song_frame = tk.Frame(self.frame)
        self.song_frame.pack(side="left", fill="both", expand=True)
        
        # 创建左侧歌曲名的Label和Listbox
        self.song_label = tk.Label(self.song_frame, text="吉他谱名", font=("宋体", 20), width=10)
        self.song_label.pack(side="top", padx=10, pady=10)
        
        self.song_listbox = tk.Listbox(self.song_frame, height=40, width=5)
        self.song_listbox.pack(side="left", fill="both", expand=True)
        
        #在song_listbox内右击出现菜单
        self.menu = tk.Menu(self.song_listbox, tearoff=0)
        self.menu.add_command(label="添加新歌曲", command=self.add_new_song)
        
        #针对歌曲右击出现的菜单
        self.song_listbox_menu = tk.Menu(self.song_listbox, tearoff=0)
        self.song_listbox_menu.add_command(label="重命名", command=self.edit_song_name)
        

        # 添加现存歌曲
        for song_name in self.song_list:
            self.song_listbox.insert(tk.END, song_name)
        
        # 创建右侧图片Frame
        self.tab_frame = tk.Frame(self.frame)
        self.tab_frame.pack(side="right", fill="both", expand=True)

        # 创建右侧Label和Listbox
        self.tab_label = tk.Label(self.tab_frame, text="吉他谱", font=("宋体", 20))
        self.tab_label.pack(side="top", padx=10, pady=10)

        self.image_label = tk.Label(self.tab_frame)
        self.image_label.pack(side="left", fill="both", expand=True)

        # 改变窗口尺寸时，同时改变照片大小
        self.image_label.bind("<Configure>", self.resize_image)
        # 右键listbox的内容，触发事件
        self.song_listbox.bind("<Button-3>", self.show_menu)
        # 左键listbox内空白处，取消选中
        self.song_listbox.bind("<Button-1>", self.clear_selection)
        #监听是否选中listbox内容
        self.song_listbox.bind("<<ListboxSelect>>", self.on_select)
    
    def exit_fullscreen(self):       #退出全屏
        self.master.attributes('-fullscreen', False)

    def resize_image(self, event):    #改变图像大小
        img_url = self.img_url
        # 获取Label的大小
        label_width = self.image_label.winfo_width()
        label_height = self.image_label.winfo_height()

        img = Image.open(img_url)

        # 计算缩放比例
        img_width, img_height = img.size
        width_ratio = label_width / img_width
        height_ratio = label_height / img_height
        ratio = min(width_ratio, height_ratio)

        # 缩放图片
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 更新图片
        self.image = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.image)
        self.image_label.update()
        self.image_label.update_idletasks()

    def popup_menu(self, event):     #弹出菜单
        self.menu.post(event.x_root, event.y_root)

    def add_new_song(self):          #添加新歌曲
        new_song_name = simpledialog.askstring("添加新歌曲", "输入新歌曲的名称：")
        if new_song_name:
            if new_song_name not in self.song_list:
                self.song_list.append(new_song_name)
                self.song_listbox.insert(tk.END, new_song_name)
                self.save_songs()
            else:
                tk.messagebox.showwarning("歌曲重复", "这个歌曲已经存在了.")

    def load_songs(self):            #从文件中加载所有歌曲名称
        song_list = []
        if os.path.exists('./config/song_list.txt'):
            with open('./config/song_list.txt', "r") as f:
                song_list = f.read().splitlines()
        return song_list
    
    def save_songs(self):            #将所有歌曲名称保存到文件中
        with open("./config/song_list.txt", "w") as f:
            f.write("\n".join(self.song_list))

    def edit_song_name(self):        #重命名操作
        # 获取选中的歌曲名称和索引
        selection_index = self.song_listbox.curselection()[0]
        old_song_name = self.song_listbox.get(selection_index)

        # 显示修改歌曲名称的对话框
        new_song_name = tk.simpledialog.askstring("Edit Song Name", "Enter new song name:", initialvalue=old_song_name)

        # 如果用户输入了新名称
        if new_song_name:
            # 判断新名称是否与已有的名称重复
            if new_song_name in self.song_listbox.get(0, tk.END):
                tk.messagebox.showwarning("Warning", "Song name already exists.")
            else:
                # 修改列表框中的歌曲名称
                self.song_listbox.delete(selection_index)
                self.song_listbox.insert(selection_index, new_song_name)

                # 修改文件名
                os.rename(f"{old_song_name}.txt", f"{new_song_name}.txt")

    def show_menu(self, event):      #判断出现哪种菜单
        if self.song_listbox.curselection():
            self.song_listbox_menu.post(event.x_root, event.y_root)
        else:
            self.menu.post(event.x_root, event.y_root)

    def clear_selection(self, event):#取消选中
        self.song_listbox.select_clear(0, tk.END)
        self.selected_song = ""
        self.add_tab_button.config(state='disabled')

    def add_tab(self):               #增加吉他谱
        selected_song = self.selected_song
        if not selected_song:
            messagebox.showerror("错误", "请先选择曲目")
            return
        
        tab_path = filedialog.askopenfilename(title="选择照片", filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
        if not tab_path:
            return

        # 创建一个文件夹，用于存放对应的吉他谱
        target_dir = os.path.join("./pic", f"{selected_song}")
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        # 将选中的歌曲复制到缓存文件中
        _, ext = os.path.splitext(tab_path)

        if selected_song in self.song_tab:
            num = len(self.song_tab[selected_song]) + 1
        else:
            num = 1
        
        target_file = os.path.join(target_dir, f"{num}{ext}")
        shutil.copy2(tab_path, target_file)

        if selected_song in self.song_tab:
            self.song_tab[selected_song].append(target_file)
        else:
            self.song_tab[selected_song] = [target_file]
        
        self.save_tabs()
        messagebox.showinfo("保存成功", "图像已保存.")
        
    def on_select(self, event):      #判断当前选中的歌曲名
        # 获取选中的歌曲名称
        selected_index = self.song_listbox.curselection()
        if self.song_listbox.curselection():
            self.selected_song = self.song_listbox.get(selected_index)
            # 设置“添加曲谱”按钮为可点击状态
            self.add_tab_button.config(state=tk.NORMAL)

        if self.selected_song in self.song_tab:
            self.img_url = self.song_tab[self.selected_song][0]
            self.resize_image

        else:
            self.img_url = './guitar accompany .png'
            self.resize_image
            
    def save_tabs(self):             #保存乐谱信息
        with open('./config/song_dict.pkl', 'wb') as f:
            pickle.dump(self.song_tab, f)
    
    def load_tabs(self):             #读取乐谱信息
        if os.path.exists('./config/song_dict.pkl'):
            with open('./config/song_dict.pkl', 'rb') as f:
                self.song_tab = pickle.load(f)
        
root = tk.Tk()
app = GuitarTrainerApp(root)
root.mainloop()