import argparse
import tkinter
import os
import cv2
import numpy as np
from PIL import Image, ImageTk

global im

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', type=str, required=True)

class Application(tkinter.Frame):
    def __init__(self, master=None, root_dir=None):
        super().__init__(master)
        self.master = master
        self.master.title('Start-End Picker')

        self.img_path = None

        self.top_left = (0, 0)
        self.bottom_right = (0, 0)

        self.video_list = []
        for class_dir in sorted(os.listdir(root_dir)):
            self.video_list.extend([os.path.join(root_dir, class_dir, video_dir) for video_dir in sorted(os.listdir(os.path.join(root_dir, class_dir)))])

        self.current_video = self.video_list[0]
        self.current_frame = 0

        self.init_keyframes()
        self.init_image()

        self.pack()
        self.create_widgets()
        self.show_frame()

    def init_keyframes(self, load_file=True):
        # キーフレームの初期化
        self.keyframes = {
            'start': [],
            'end': []
        }

        if load_file:
            self.keyframes_txt_path = os.path.join(self.current_video, 'keyframes.txt')
            if os.path.exists(self.keyframes_txt_path):
                with open(self.keyframes_txt_path, 'r') as keyframes_txt:
                    lines = keyframes_txt.readlines()
                    if len(lines) > 1:
                        self.keyframes = {
                            'start': [int(v) for v in lines[0].strip().split(' ')],
                            'end': [int(v) for v in lines[1].strip().split(' ')]
                        }

    def set_keyframe(self):
        # 現在のフレームをキーフレームに追加
        keyframe = [
            self.current_frame,
            self.top_left[0],
            self.top_left[1],
            self.bottom_right[0] - self.top_left[0],
            self.bottom_right[1] - self.top_left[1]
        ]

        if keyframe[3] == 0 or keyframe[4] == 0:
            return

        if len(self.keyframes['start']) == 0:
            self.keyframes['start'] = keyframe
            self.keyframes['end'] = keyframe
            return

        start_frame = self.keyframes['start'][0]
        end_frame = self.keyframes['end'][0]

        if keyframe[0] <= start_frame:
            self.keyframes['start'] = keyframe
        elif keyframe[0] >= end_frame:
            self.keyframes['end'] = keyframe

    def show_frame(self):
        # current_frameに対応する画像を表示
        for i, img_path in enumerate(sorted(os.listdir(os.path.join(self.current_video, 'frames')))):
            if i == self.current_frame:
                self.img_path = os.path.join(self.current_video, 'frames', img_path)
                self.init_image()
                self.show_image()

                if len(self.keyframes['start']) > 0:
                    for frame, x, y, w, h in self.keyframes.values():
                        if frame == self.current_frame:
                            self.top_left = (x, y)
                            self.bottom_right = (x+w, y+h)
                            self.draw_rect()
                            break
                return True

        self.current_frame = i
        return False

    def init_image(self):
        # opencvで実画像ファイルをロード
        if self.img_path is not None:
            self.cv2_img = cv2.imread(self.img_path)
        else:
            self.cv2_img = np.zeros((720, 1280, 3), np.uint8)
        self.rgb_img = cv2.cvtColor(self.cv2_img, cv2.COLOR_BGR2RGB)

    def create_widgets(self):
        read_image = Image.fromarray(self.cv2_img)

        self.test_canvas = tkinter.Canvas(self, width=read_image.width, height=read_image.height)
        self.test_canvas.grid(row=0, column=0)

        self.test_canvas.bind('<Button-1>', self.set_top_left)
        self.test_canvas.bind('<B1-Motion>', self.set_bottom_right)
        self.test_canvas.bind('<ButtonRelease-1>', self.set_bottom_right)
        self.test_canvas.bind('<Motion>', self.draw_support_lines)

        self.show_image()

        self.frame = tkinter.Frame(self)
        self.frame.grid(row=1, column=0, pady=10)

        self.hardleft_button = tkinter.Button(self.frame, text='<<', command=self.hardprev_image)
        self.hardleft_button.grid(row=0, column=0, padx=5)

        self.left_button = tkinter.Button(self.frame, text='<', command=self.prev_image)
        self.left_button.grid(row=0, column=1)

        self.right_button = tkinter.Button(self.frame, text='>', command=self.next_image)
        self.right_button.grid(row=0, column=2, padx=5)

        self.hardright_button = tkinter.Button(self.frame, text='>>', command=self.hardnext_image)
        self.hardright_button.grid(row=0, column=3)

        self.save_button = tkinter.Button(self.frame, text='Save', command=self.save_box)
        self.save_button.grid(row=0, column=5)

        self.clear_button = tkinter.Button(self.frame, text='Clear', command=self.clear_box)
        self.clear_button.grid(row=0, column=4, padx=50)

        list_var = tkinter.StringVar(
            value = self.video_list
        )
        self.list_box = tkinter.Listbox(self, listvariable=list_var, height=20, width=20)
        self.list_box.grid(row=0, column=1, sticky=('n', 's'))
        self.list_box.bind('<<ListboxSelect>>', self.set_video)

        self.vscrollbar = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.list_box.yview)
        self.list_box['yscrollcommand'] = self.vscrollbar.set
        self.vscrollbar.grid(row=0, column=2, sticky=('n', 's'))

        self.hscrollbar = tkinter.Scrollbar(self, orient=tkinter.HORIZONTAL, command=self.list_box.xview)
        self.list_box['xscrollcommand'] = self.hscrollbar.set
        self.hscrollbar.grid(row=1, column=1, sticky=('w', 'e'))

    def show_image(self):
        # ヴィジェットに画像を表示する
        global im

        read_image = Image.fromarray(self.rgb_img)
        im = ImageTk.PhotoImage(image=read_image)
        self.test_canvas.create_image(0, 0, anchor='nw', image=im)

    # callbacks
    def draw_support_lines(self, event):
        # マウスカーソル位置に補助線を引く
        x, y = event.x, event.y
        self.draw_rect()
        cv2.line(self.rgb_img, (x, 0), (x, 720), (255, 140, 0), 1)
        cv2.line(self.rgb_img, (0, y), (1280, y), (255, 140, 0), 1)
        self.show_image()

    def set_top_left(self, event):
        self.top_left = (event.x, event.y)

    def set_bottom_right(self, event):
        x, y = event.x, event.y
        if x < 0:
            x = 0
        if x >= 1280:
            x = 1279
        if y < 0:
            y = 0
        if y >= 720:
            y = 719

        self.bottom_right = (x, y)
        self.draw_rect()

    def draw_rect(self):
        # 長方形を描画し、キーフレームに登録
        self.init_image()
        cv2.rectangle(self.rgb_img, self.top_left, self.bottom_right, (0, 255, 0), 2)
        self.show_image()
        self.set_keyframe()

    def hardprev_image(self):
        self.top_left = (0, 0)
        self.bottom_right = (0, 0)
        self.current_frame = 0
        self.show_frame()

    def prev_image(self):
        # 前のフレームに移動
        self.top_left = (0, 0)
        self.bottom_right = (0, 0)
        self.current_frame -= 1
        if self.current_frame < 0:
            self.current_frame = 0
        self.show_frame()

    def next_image(self):
        # 次のフレームに移動
        self.top_left = (0, 0)
        self.bottom_right = (0, 0)
        self.current_frame += 1
        self.show_frame()

    def hardnext_image(self):
        # 次のフレームに移動
        self.top_left = (0, 0)
        self.bottom_right = (0, 0)

        while self.show_frame():
            self.current_frame += 1

    def save_box(self):
        # キーフレームを保存
        print(self.keyframes)
        with open(self.keyframes_txt_path, 'w') as keyframes_txt:
            for keyframe in self.keyframes.values():
                if len(keyframe) > 0:
                    frame, x, y, w, h = keyframe
                    keyframes_txt.write('{} {} {} {} {}\n'.format(frame, x, y, w, h))

    def clear_box(self):
        # キーフレームの状態や画像をリセット
        self.top_left = (0, 0)
        self.bottom_right = (0, 0)
        self.init_keyframes(load_file=False)
        self.init_image()
        self.show_image()

    def set_video(self, event):
        # 別の動画に移動
        # self.save_box()
        self.clear_box()
        for i in self.list_box.curselection():
            self.current_video = self.list_box.get(i)
            self.current_frame = 0
            self.init_keyframes()
            self.show_frame()
            return

if __name__ == '__main__':
    args = parser.parse_args()
    root_dir = os.path.expanduser(args.input)

    root = tkinter.Tk()
    app = Application(master=root, root_dir=root_dir)
    app.mainloop()
