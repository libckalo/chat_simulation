import tkinter
import tkinter.messagebox
import PIL.Image
import PIL.ImageTk
import PIL.ImageOps
import io
import importlib.resources
from ..nine_png import NinePNG
from ..databases.character_database import Character
from .. import data

SUB_BG_FILE = importlib.resources.open_binary(data, "sub_character_chat_box.png")
MAIN_BG_FILE = importlib.resources.open_binary(data, "main_character_chat_box.png")
SUB_BG_NINEPNG = NinePNG(SUB_BG_FILE)
MAIN_BG_NINEPNG = NinePNG(MAIN_BG_FILE)
DELETE_ICON = importlib.resources.read_binary(data, "delete.png")
BACKGROUND_COLOR = "#D9D9D9"
CHAT_BACKGROUND_COLOR = "#FFF"

class SingleTextMsg:
    def __init__(self,
                 root: tkinter.Canvas,
                 people: Character,
                 msg: str,
                 current_y: int,
                 is_main: bool):
        location = (0, current_y)
        self._current_y = current_y
        self.is_main = is_main
        self.root = root
        self.people = people
        self.content = msg
        self.msg_bg_ninepng = SUB_BG_NINEPNG
        self.msg_text_label = root.create_text(
            115 + self.msg_bg_ninepng.bottom_margin[0],
            location[1] + 20 + self.msg_bg_ninepng.right_margin[0],
            anchor=tkinter.NW,
            text=msg,
            font=("Noto Sans CJK SC", 16, ""),
            width=root.winfo_width() - 280
        )
        text_label_size = root.bbox(self.msg_text_label)
        self.msg_bg_tkinterimg = PIL.ImageTk.PhotoImage(
            self.msg_bg_ninepng.scale(
                (max(text_label_size[2] - text_label_size[0] +
                     self.msg_bg_ninepng.img.width -
                     len(self.msg_bg_ninepng.bottom_margin),
                     self.msg_bg_ninepng.img.width),
                 max(text_label_size[3] - text_label_size[1] +
                     self.msg_bg_ninepng.img.height -
                     len(self.msg_bg_ninepng.right_margin),
                     self.msg_bg_ninepng.img.height))
            )
        )
        self.msg_bg_label = root.create_image(
            115, location[1] + 20,
            anchor=tkinter.NW,
            image=self.msg_bg_tkinterimg
        )
        root.lower(self.msg_bg_label, self.msg_text_label)
        self.profile_photo_img = PIL.ImageTk.PhotoImage(
            PIL.Image.open(people.profile_photo).resize((100, 100))
        )
        self.profile_photo = root.create_image(
            location,
            anchor=tkinter.NW,
            image=self.profile_photo_img
        )
        self.name_label = root.create_text(
            105, location[1],
            anchor=tkinter.NW,
            text=people.name
        )
        self.delete_button_img = tkinter.PhotoImage(data=DELETE_ICON)
        self.delete_button_obj = tkinter.Button(
            root,
            image=self.delete_button_img,
            command=self.delete
        )
        self.delete_button = root.create_window(
            root.winfo_width() - 57, location[1] + 25,
            anchor=tkinter.NW,
            window=self.delete_button_obj
        )
        self.top_msg_delete = None
        self.top_location = (0, root.bbox(self.msg_bg_label)[1])
        self.location = (0, root.bbox(self.msg_bg_label)[3] + 20)
        if is_main:
            self.to_main()

    def delete(self):
        if tkinter.messagebox.askokcancel(
            message="Are you sure want to delete this message?"
        ): self._delete()

    def _delete(self):
        self.root.delete(self.profile_photo)
        self.root.delete(self.name_label)
        self.root.delete(self.msg_text_label)
        self.root.delete(self.msg_bg_label)
        self.root.delete(self.delete_button)
        self.delete_button_obj.destroy()
        self.top_msg_delete()

    def to_sub(self):
        self.is_main = False
        self.msg_bg_ninepng = SUB_BG_NINEPNG
        self.root.itemconfigure(self.msg_text_label, anchor=tkinter.NW, width=self.root.winfo_width() - 280)
        self.root.itemconfigure(self.msg_bg_label, anchor=tkinter.NW)
        self.root.itemconfigure(self.profile_photo, anchor=tkinter.NW)
        self.root.itemconfigure(self.name_label, anchor=tkinter.NW)
        self.root.itemconfigure(self.delete_button, anchor=tkinter.NW)
        self.root.coords(self.msg_text_label,
            115 + self.msg_bg_ninepng.bottom_margin[0],
            self._current_y + 20 + self.msg_bg_ninepng.right_margin[0]
        )
        self.root.coords(self.msg_bg_label, 115, self._current_y + 20)
        self.root.coords(self.profile_photo, 0, self._current_y)
        self.root.coords(self.name_label, 105, self._current_y)
        self.root.coords(self.delete_button,
            self.root.winfo_width() - 57, self._current_y + 25
        )
        text_label_size = self.root.bbox(self.msg_text_label)
        self.msg_bg_tkinterimg = PIL.ImageTk.PhotoImage(
            self.msg_bg_ninepng.scale(
                (max(text_label_size[2] - text_label_size[0] +
                     self.msg_bg_ninepng.img.width -
                     len(self.msg_bg_ninepng.bottom_margin),
                     self.msg_bg_ninepng.img.width),
                 max(text_label_size[3] - text_label_size[1] +
                     self.msg_bg_ninepng.img.height -
                     len(self.msg_bg_ninepng.right_margin),
                     self.msg_bg_ninepng.img.height))
            )
        )
        self.root.delete(self.msg_bg_label)
        self.msg_bg_label = self.root.create_image(
            115, self._current_y + 20,
            anchor=tkinter.NW,
            image=self.msg_bg_tkinterimg
        )
        self.root.lower(self.msg_bg_label, self.msg_text_label)

    def to_main(self):
        self.is_main = True
        width = self.root.winfo_width()
        self.msg_bg_ninepng = MAIN_BG_NINEPNG
        self.root.itemconfigure(self.msg_text_label, anchor=tkinter.NE, width=width - 280)
        self.root.itemconfigure(self.msg_bg_label, anchor=tkinter.NE)
        self.root.itemconfigure(self.profile_photo, anchor=tkinter.NE)
        self.root.itemconfigure(self.name_label, anchor=tkinter.NE)
        self.root.itemconfigure(self.delete_button, anchor=tkinter.NE)
        self.root.coords(self.msg_text_label,
            width - 115 -
            (self.msg_bg_ninepng.img.width - self.msg_bg_ninepng.bottom_margin[-1]),
            self._current_y + 20 + self.msg_bg_ninepng.right_margin[0],
        )
        self.root.coords(self.msg_bg_label, width - 115, self._current_y + 20)
        self.root.coords(self.profile_photo, width, self._current_y)
        self.root.coords(self.name_label, width - 105, self._current_y)
        self.root.coords(self.delete_button,
            57, self._current_y + 25
        )
        text_label_size = self.root.bbox(self.msg_text_label)
        self.msg_bg_tkinterimg = PIL.ImageTk.PhotoImage(
            self.msg_bg_ninepng.scale(
                (max(text_label_size[2] - text_label_size[0] +
                     self.msg_bg_ninepng.img.width -
                     len(self.msg_bg_ninepng.bottom_margin),
                     self.msg_bg_ninepng.img.width),
                 max(text_label_size[3] - text_label_size[1] +
                     self.msg_bg_ninepng.img.height -
                     len(self.msg_bg_ninepng.right_margin),
                     self.msg_bg_ninepng.img.height))
            )
        )
        self.root.delete(self.msg_bg_label)
        self.msg_bg_label = self.root.create_image(
            width - 115, self._current_y + 20,
            anchor=tkinter.NE,
            image=self.msg_bg_tkinterimg
        )
        self.root.lower(self.msg_bg_label, self.msg_text_label)

class SinglePhotoMsg:
    def __init__(self,
                 root: tkinter.Canvas,
                 people: Character,
                 photo: io.BytesIO | io.BufferedIOBase,
                 current_y: int,
                 is_main: bool):
        location = (0, current_y)
        self._current_y = current_y
        self.is_main = is_main
        self.root = root
        self.people = people
        self.content = photo
        self._photo_pil = PIL.Image.open(photo)
        self._photo = PIL.ImageTk.PhotoImage(PIL.ImageOps.scale(
            self._photo_pil, 200 / self._photo_pil.width
        ))
        self.msg_photo = root.create_image(
            115,
            location[1] + 20,
            anchor=tkinter.NW,
            image=self._photo,
        )
        self.root.tag_bind(self.msg_photo, "<1>", self._photo_pil.show)
        self.profile_photo_img = PIL.ImageTk.PhotoImage(
            PIL.Image.open(people.profile_photo).resize((100, 100))
        )
        self.profile_photo = root.create_image(
            location,
            anchor=tkinter.NW,
            image=self.profile_photo_img
        )
        self.name_label = root.create_text(
            105, location[1],
            anchor=tkinter.NW,
            text=people.name
        )
        self.delete_button_img = tkinter.PhotoImage(data=DELETE_ICON)
        self.delete_button_obj = tkinter.Button(
            root,
            image=self.delete_button_img,
            command=self.delete
        )
        self.delete_button = root.create_window(
            root.winfo_width() - 57, location[1] + 25,
            anchor=tkinter.NW,
            window=self.delete_button_obj
        )
        self.top_msg_delete = None
        self.top_location = (0, root.bbox(self.msg_photo)[1])
        self.location = (0, root.bbox(self.msg_photo)[3] + 20)
        if is_main:
            self.to_main()

    def delete(self):
        if tkinter.messagebox.askokcancel(
            message="Are you sure want to delete this message?"
        ): self._delete()

    def _delete(self):
        self.root.delete(self.profile_photo)
        self.root.delete(self.name_label)
        self.root.delete(self.msg_photo)
        self.root.delete(self.delete_button)
        self.delete_button_obj.destroy()
        self.top_msg_delete()

    def to_sub(self):
        self.is_main = False
        width = self.root.winfo_width()
        self.root.itemconfigure(self.msg_photo, anchor=tkinter.NW)
        self.root.itemconfigure(self.profile_photo, anchor=tkinter.NW)
        self.root.itemconfigure(self.name_label, anchor=tkinter.NW)
        self.root.itemconfigure(self.delete_button, anchor=tkinter.NW)
        self.root.coords(self.msg_photo, 115, self._current_y + 20)
        self.root.coords(self.profile_photo, 0, self._current_y)
        self.root.coords(self.name_label, 105, self._current_y)
        self.root.coords(self.delete_button, width - 57, self._current_y + 25)

    def to_main(self):
        self.is_main = True
        width = self.root.winfo_width()
        self.root.itemconfigure(self.msg_photo, anchor=tkinter.NE)
        self.root.itemconfigure(self.profile_photo, anchor=tkinter.NE)
        self.root.itemconfigure(self.name_label, anchor=tkinter.NE)
        self.root.itemconfigure(self.delete_button, anchor=tkinter.NE)
        self.root.coords(self.msg_photo, width - 115, self._current_y + 20)
        self.root.coords(self.profile_photo, width, self._current_y)
        self.root.coords(self.name_label, width - 105, self._current_y)
        self.root.coords(self.delete_button, 57, self._current_y + 25)
