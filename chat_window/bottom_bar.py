import tkinter
import tkinter.messagebox
import PIL.Image
import PIL.ImageTk
from .main_chat_window import ChatWindow
#from .character_selection_window import CharSelectionWindow
from ..databases.character_database import Character

class ChatBottomBar:
    def __init__(self, root: tkinter.Tk, main_chat_window: ChatWindow, char_selection_window):#: CharSelectionWindow):
        self.main_frame = tkinter.Frame(root)
        self.main_frame.bind("<Configure>", self.on_size_change)
        self.character_photo = None
        self.character_photo_tkimage = None
        self.show_character_window_button = tkinter.Button(
            self.main_frame, command=self.show_character_window,
            text="Show characters selection window"#, image=self.character_photo
        )
        self.message_textbox = tkinter.Text(self.main_frame, wrap="word")
        self.send_button = tkinter.Button(self.main_frame, command=self.send, text="Send")
        self.main_chat_window = main_chat_window
        self.char_selection_window = char_selection_window
        self.character = None
        self.char_window_show = False
        self.is_main = False

    def on_size_change(self, event: tkinter.Event):
        self.character_photo_tkimage = self.character_photo_tkimage and (
            PIL.ImageTk.PhotoImage(
                self.character_photo.resize(
                    (int(event.width * 0.1), event.height),
                    PIL.Image.Resampling.BOX
                )
            )
        )
        if self.character_photo_tkimage:
            self.show_character_window_button.configure(
                image=self.character_photo_tkimage
            )
        self.show_character_window_button.configure(
            wraplength=event.width * 0.1
        )

    def show_character_window(self):
        self.char_window_show = not self.char_window_show
        self.char_selection_window.root.geometry(
            "+%d+%d" % (
                self.show_character_window_button.winfo_rootx(),
                self.show_character_window_button.winfo_rooty() - 340
            )
        )
        self.char_selection_window.root.state("normal" if self.char_window_show else "withdrawn")
        self.show_character_window_button.configure(
            text=("Hide" if self.char_window_show else "Show") +
                  " characters selection window"
        )

    def show(self):
        self.show_character_window_button.place(x=0, y=0, relwidth=0.1, relheight=1)
        self.message_textbox.place(relx=0.1, y=0, relwidth=0.9, relheight=1)
        self.send_button.place(relx=0.9, y=0, relwidth=0.1, relheight=1)
        self.main_frame.place(x=0, rely=0.85, relwidth=1, relheight=0.15)

    def set_character(self, people: Character, is_main: bool):
        self.character = people
        self.is_main = is_main
        if people:
            self.character_photo = PIL.Image.open(people.profile_photo)
            self.character_photo_tkimage = (
                PIL.ImageTk.PhotoImage(
                    self.character_photo.resize(
                        (int(self.main_frame.winfo_width() * 0.1),
                         self.main_frame.winfo_height()),
                        PIL.Image.Resampling.BOX
                    )
                )
            )
            self.show_character_window_button.configure(
                image=self.character_photo_tkimage
            )
        else:
            self.show_character_window_button.configure(
                image=""
            )

    def send(self):
        message = self.message_textbox.get("0.0", "end")[:-1] # there's a trailing '\n'
        if not message:
            tkinter.messagebox.showerror(message="Cannot send empty message")
            return
        if self.character is None:
            tkinter.messagebox.showerror(message="No character selected")
            return

        self.main_chat_window.add_msg(self.character, message, self.is_main)
        self.message_textbox.delete("0.0", "end")
