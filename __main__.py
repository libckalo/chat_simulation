import sys
import tkinter
from .chat_window.main_chat_window import ChatWindow
from .chat_window.bottom_bar import ChatBottomBar
from .chat_window.character_selection_window import CharSelectionWindow
from .databases.save_tool import SaveTool

def main(argc, argv):
    root = tkinter.Tk()
    root.title("Chat simulator")
    root.geometry("600x600")
    main_chat_window = ChatWindow(root)
    main_chat_window.show()
    # recursive requirement
    char_selection_window = CharSelectionWindow(root, main_chat_window)
    char_selection_window.show()
    # recursive requirement
    chat_bottom_bar = ChatBottomBar(root, main_chat_window, char_selection_window)
    chat_bottom_bar.show()
    save_tool = SaveTool(root, char_selection_window, main_chat_window)
    root.mainloop()

if __name__ == "__main__":
    sys.exit(main(len(sys.argv), sys.argv))
