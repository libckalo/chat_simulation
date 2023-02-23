import tkinter
from .single_chat_msg import SingleChatMsg
from ..databases.character_database import Character

CHAT_BACKGROUND_COLOR = "#EEE"

class ChatWindow:
    def __init__(self, root: tkinter.Tk):
        self.main_canvas = tkinter.Canvas(root, background=CHAT_BACKGROUND_COLOR)
        self.main_canvas.bind("<Configure>", self.on_size_change)
        self.scroll_bar = tkinter.Scrollbar(
            root, orient=tkinter.VERTICAL, command=self.main_canvas.yview
        )
        self.main_canvas.configure(yscrollcommand=self.scroll_bar.set)
        self.messages = []

    def update_scroll(self):
        self.main_canvas.configure(
            scrollregion=(
                0, 0, self.main_canvas.winfo_width(),
                0 if not self.messages else self.messages[-1].location[1]
            )
        )

    def on_size_change(self, event: tkinter.Event):
        for index, omsg in enumerate(self.messages):
            omsg._current_y = 0 if not index else (self.messages[index - 1].location[1])
            omsg.top_location = (0, self.main_canvas.bbox(omsg.msg_bg_label)[1])
            omsg.location = (0, self.main_canvas.bbox(omsg.msg_bg_label)[3] + 20)
            if omsg.is_main:
                omsg.to_main()
            else:
                omsg.to_sub()
        self.update_scroll()

    def show(self):
        self.main_canvas.place(x=0, y=0, relwidth=0.97, relheight=0.85)
        self.scroll_bar.place(relx=0.97, y=0, relwidth=0.03, relheight=0.85)

    def add_msg(self, people: Character, msg: str, is_main: bool):
        new_msg = SingleChatMsg(
            self.main_canvas, people, msg,
            0 if not self.messages else self.messages[-1].location[1],
            is_main
        )
        new_msg.top_msg_delete = lambda: self.del_msg(new_msg)
        self.messages.append(new_msg)
        self.update_scroll()

    def del_msg(self, msg: SingleChatMsg):
        index = self.messages.index(msg)
        height = (
            (msg if index == len(self.messages) - 1 else self.messages[index + 1])
            .top_location[1] -
            msg.top_location[1]
        )
        for omsg in self.messages[index + 1:]:
            omsg._current_y = omsg.top_location[1] - 20 - height
            omsg.top_location = (0, omsg.top_location[1] - height)
            omsg.location = (0, omsg.location[1] - height)
            if omsg.is_main:
                omsg.to_main()
            else:
                omsg.to_sub()
        self.messages.remove(msg)
        self.update_scroll() 
