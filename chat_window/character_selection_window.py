import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog
import PIL.Image
import PIL.ImageTk
import io
import importlib.resources
from .main_chat_window import ChatWindow
from .bottom_bar import ChatBottomBar
from ..databases.character_database import (
    Character,
    characters as global_characters
)
from .. import data

DEFAULT_PROFILE_PHOTO = importlib.resources.open_binary(data, "default_avatar.png")
CHARACTER_LISTBOX_BG = "#DDD"
CHARACTER_SELECT_BG = "#999"

class CharacterFrame:
    def __init__(self, root: tkinter.Canvas, people: Character, length: int, on_select_callback):
        self.location = location = (0, length * 50)
        self.root = root
        self.background = root.create_rectangle(
            0, location[1], root.winfo_width(), location[1] + 50,
            fill=CHARACTER_SELECT_BG,
            outline="",
            state="hidden"
        )
        self.orig_char_img = PIL.Image.open(people.profile_photo)
        self.char_img = PIL.ImageTk.PhotoImage(
            self.orig_char_img.resize((50, 50))
        )
        self.char_img_label = root.create_image(
            location, image=self.char_img, anchor=tkinter.NW
        )
        self.char_name_label = root.create_text(
            60, location[1] + 16,
            text=people.name,
            anchor=tkinter.NW,
            width=root.winfo_width() - 120
        )
        self.selection_button = tkinter.Button(
            root, text="Select", command=lambda: self.on_select_main() if self.is_main else self.on_select()
        )
        self.selection_button_id = root.create_window(
            root.winfo_width() - 60, location[1] + 10,
            anchor=tkinter.NW,
            width=60,
            window=self.selection_button
        )
        self.selection_main_button = tkinter.Button(
            root, text="As main", command=self.on_select_main
        )
        self.selection_main_button_id = root.create_window(
            root.winfo_width() - 120, location[1] + 10,
            anchor=tkinter.NW,
            width=60,
            window=self.selection_main_button
        )
        self.is_main = False
        self.people = people
        self.on_select_callback = on_select_callback

    def delete(self):
        self.root.delete(self.char_img_label)
        self.root.delete(self.char_name_label)
        self.root.delete(self.selection_button_id)
        self.root.delete(self.selection_main_button_id)
        self.root.delete(self.background)
        self.selection_main_button.destroy()
        self.selection_button.destroy()

    def on_select(self):
        self.selection_main_button.configure(text="As main", command=self.on_select_main)
        self.is_main = False
        self.on_select_callback(self, False)

    def on_select_main(self):
        self.selection_main_button.configure(text="As sub", command=self.on_select)
        self.is_main = True
        self.on_select_callback(self, True)

    def to_select(self):
        self.root.itemconfigure(self.background, state="normal")

    def to_unselect(self):
        self.root.itemconfigure(self.background, state="hidden")

class CharacterListbox:
    def __init__(self, root: tkinter.Toplevel, on_select_callback):
        self.main_canvas = tkinter.Canvas(root, background=CHARACTER_LISTBOX_BG)
        self.main_canvas.bind("<Configure>", self.on_size_change)
        self.scroll_bar = tkinter.Scrollbar(root, orient=tkinter.VERTICAL, command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=self.scroll_bar.set)
        self.cur_select = None
        self.on_select_callback = on_select_callback
        self.characters = []

    def show(self):
        self.main_canvas.place(x=0, rely=0.1, relwidth=0.95, relheight=0.8)
        self.scroll_bar.place(relx=0.95, rely=0.1, relwidth=0.05, relheight=0.8)

    def update_scroll(self):
        self.main_canvas.configure(
            scrollregion=(
                0, 0, self.main_canvas.winfo_width(),
                0 if not self.characters else self.characters[-1].location[1]
            )
        )

    def on_size_change(self, event: tkinter.Event):
        for i, char in enumerate(self.characters):
            self.main_canvas.coords(char.selection_button_id,
                                    (self.main_canvas.winfo_width() - 60, 50 * i + 10))
            self.main_canvas.coords(char.selection_main_button_id,
                                    (self.main_canvas.winfo_width() - 120, 50 * i + 10))
            self.main_canvas.coords(char.background,
                                    (0, 50 * i, self.main_canvas.winfo_width(), 50 * (i + 1)))

    def add_char(self, people: Character):
        new = CharacterFrame(self.main_canvas, people, len(self.characters), self.on_select)
        self.characters.append(new)
        global_characters[people.name] = people
        self.update_scroll()

    def del_char(self):
        self.cur_select.delete()
        index = self.characters.index(self.cur_select)
        self.characters.remove(self.cur_select)
        for i, char in enumerate(self.characters, index):
            self.main_canvas.coords(char.char_img_label, (0, 50 * (i - index)))
            self.main_canvas.coords(char.char_name_label, (60, 50 * (i - index) + 16))
            self.main_canvas.coords(char.selection_button_id,
                                    (self.main_canvas.winfo_width() - 60, 50 * (i - index) + 10))
            self.main_canvas.coords(char.selection_main_button_id,
                                    (self.main_canvas.winfo_width() - 120, 50 * (i - index) + 10))
            self.main_canvas.coords(
                char.background,
                (0, 50 * (i - index), self.main_canvas.winfo_width(), 50 * (i - index + 1))
            )
        global_characters.pop(self.cur_select.people.name)
        self.update_scroll()
        self.cur_select = None

    def on_select(self, frame: CharacterFrame, is_main: bool):
        if self.cur_select:
            self.cur_select.to_unselect()
        frame.to_select()
        self.cur_select = frame
        self.on_select_callback(frame.people, is_main)

class CreateCharWindow(tkinter.simpledialog.Dialog):
    def body(self, master):
        self.name = None
        self.title("Add Character")
        self.wm_geometry("500x300")
        self.wm_resizable(False, False)
        self.create_hint_label = tkinter.Label(self, text="Create new character", font=("", 20, ""), relief=tkinter.SOLID)
        self.profile_photo_frame = tkinter.Frame(self, height=100)
        self.profile_photo = DEFAULT_PROFILE_PHOTO
        self.orig_profile_photo_obj = PIL.Image.open(self.profile_photo)
        self.profile_photo_obj = PIL.ImageTk.PhotoImage(self.orig_profile_photo_obj)
        self.profile_photo_button = tkinter.Button(
            self.profile_photo_frame,
            image=self.profile_photo_obj,
            command=self.choose_photo
        )
        self.profile_photo_button.bind("<Configure>", self.on_window_size_change)
        self.profile_photo_label = tkinter.Label(self.profile_photo_frame, text="Character photo", font=("", 12, ""))
        self.name_frame = tkinter.Frame(self, height=100)
        self.name_entry = tkinter.Entry(self.name_frame)
        self.name_label = tkinter.Label(self.name_frame, text="Character name", font=("", 12, ""))

        #self.create_hint_label.place(anchor=tkinter.N, relx=0.5, relheight=0.2, relwidth=1)
        self.create_hint_label.pack(anchor=tkinter.N, expand=True, fill=tkinter.X)
        #self.profile_photo_frame.place(x=0, rely=0.2, relwidth=1, relheight=0.3)
        self.profile_photo_frame.pack(expand=True, fill=tkinter.X)
        self.profile_photo_button.place(x=0, y=0, relwidth=0.2, relheight=1)
        self.profile_photo_label.place(relx=0.2, y=0, relwidth=0.8, relheight=1)
        #self.name_frame.place(x=0, rely=0.5, relwidth=1, relheight=0.3)
        self.name_frame.pack(expand=True, fill=tkinter.X)
        self.name_entry.place(x=0, y=0, relwidth=0.6, relheight=1)
        self.name_label.place(relx=0.6, y=0, relwidth=0.4, relheight=1)

        return self.name_entry

    def validate(self):
        if not self.name_entry.get():
            tkinter.messagebox.showerror(
                message="Please input character name",
                parent=self
            )
            return False

        self.name = self.name_entry.get()
        self.photo = self.profile_photo
        return True

    def choose_photo(self):
        self.profile_photo = tkinter.filedialog.askopenfile(
            "rb",
            filetypes=[
                ("PNG file", "*.png"),
                ("JPEG file", "*.jpg")
            ],
            parent=self
        ) or DEFAULT_PROFILE_PHOTO
        self.orig_profile_photo_obj = PIL.Image.open(self.profile_photo)
        self.profile_photo_obj = PIL.ImageTk.PhotoImage(self.orig_profile_photo_obj)
        self.profile_photo_button.configure(
            image=self.profile_photo_obj
        )

    def on_window_size_change(self, event: tkinter.Event):
        self.profile_photo_obj = (
            PIL.ImageTk.PhotoImage(
                self.orig_profile_photo_obj
                .resize(
                    (event.width, event.height),
                    PIL.Image.Resampling.BOX
                )
            )
        )
        self.profile_photo_button.configure(image=self.profile_photo_obj)

class CharSelectionWindow:
    def __init__(self, root: tkinter.Tk, chat_window: ChatWindow):
        self.root = tkinter.Toplevel()
        self.root.title("Character Selection/Modification Window")
        self.root.wm_geometry("300x300")
        self.root.wm_state("withdrawn")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_self)
        self.character_label = tkinter.Label(self.root, text="Currently selected: ()")
        self.character_listbox = CharacterListbox(self.root, self.on_selectchar)
        self.add_character_button = tkinter.Button(
            self.root,
            text="Add character",
            command=self.add_character
        )
        self.del_character_button = tkinter.Button(
            self.root,
            text="Delete character",
            command=self.del_character
        )
        self.bottom_bar = None
        self.chat_window = chat_window
        self.main_char = []

    def hide_self(self):
        self.bottom_bar.char_window_show = False
        self.bottom_bar.show_character_window_button.configure(
            text="Show characters selection window"
        )
        self.root.wm_state("withdrawn")


    def show(self):
        self.character_label.place(x=0, y=0, relwidth=1, relheight=0.1)
        self.character_listbox.show()
        self.add_character_button.place(x=0, rely=0.9, relwidth=0.5, relheight=0.1)
        self.del_character_button.place(relx=0.5, rely=0.9, relwidth=0.5, relheight=0.1)

    def on_selectchar(self, people: Character, is_main: bool):
        self.character_label.configure(
            text="Currently selected: %s (%s)" % (
                people.name,
                "Main" if is_main else "Sub"
            )
        )
        self.bottom_bar.set_character(people, is_main)
        if is_main:
            if people not in self.main_char:
                self.main_char.append(people)
        else:
            try:
                self.main_char.remove(people)
            except ValueError:
                pass

        for message in self.chat_window.messages:
            if message.people in self.main_char:
                message.to_main()
            else:
                message.to_sub()

    def del_character(self):
        if not self.character_listbox.cur_select:
            tkinter.messagebox.showerror(
                message="No character selected",
                parent=self.root
            )
            return

        if not tkinter.messagebox.askokcancel(
            message=
                "Delete a character will also delete all messages sent by him/her.\n"
                "Do you really want to delete this character?",
            parent=self.root
        ): return

        self._del_character()

    def _del_character(self):
        for message in self.chat_window.messages[:]:
            if message.people == self.character_listbox.cur_select.people:
                message._delete()

        self.character_listbox.del_char()
        self.character_label.configure(text="Currently selected: ()")
        self.bottom_bar.set_character(None, False)

    def add_character(self):
        c = CreateCharWindow(self.root)
        if c.name is None: return

        if c.name in global_characters:
            tkinter.messagebox.showerror(message="Duplicate character for: %s" % name)
            return

        self.character_listbox.add_char(Character(c.name, c.photo))

    def _internal_add_character(self, name, photo):
        self.character_listbox.add_char(Character(name, photo))
