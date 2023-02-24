import tkinter
import tkinter.filedialog
import tkinter.messagebox
import traceback
import gzip
import base64
import io
import xml.etree.ElementTree as ElementTree
from .character_database import characters as global_characters
from .character_database import Character
from ..chat_window.character_selection_window import CharSelectionWindow
from ..chat_window.main_chat_window import ChatWindow
from ..chat_window.single_chat_msg import SingleTextMsg, SinglePhotoMsg

# The saved chat xml is as follows:
# <chat_simulation_data>
#     <characters>
#         <!-- profile photo is gzip-compressed, base64-encoded -->
#         <character name="TEST 1" profile_photo="..."/>
#         ......
#
#         <!-- optional -->
#         <current_select name="TEST 1"/>
#
#         <main_character>
#             <character name="TEST 1"/>
#             ......
#         </main_character>
#     </characters>
#
#     <messages>
#         <message sender="TEST 1" type="{text|photo}">
#             hello world <!-- content
#                         (when type == photo, the photo is encoded the same as profile photo -->
#         </message>
#         ......
#     </messages>
# </chat_simulation_data>

class SaveTool:
    def __init__(self, root: tkinter.Tk,
                 char_selection_window: CharSelectionWindow,
                 chat_window: ChatWindow):
        self.chat_window = chat_window
        self.char_selection_window = char_selection_window
        self.save_menu = tkinter.Menu(root)
        root.configure(menu=self.save_menu)
        self.save_menu.add_command(
            label="Load saved chat...", command=self.load, underline=0
        )
        self.save_menu.add_command(
            label="Save current chat...", command=self.save, underline=0
        )

    def save(self):
        try:
            write_file = tkinter.filedialog.asksaveasfile(
                initialfile="chat.xml",
                filetypes=[
                    ("XML file", "*.xml")
                ]
            )
        except:
            tkinter.messagebox.showerror(
                title="Error while saving chat",
                message="Error occurred while saving chat.\n"
                        "The full traceback is:\n" +
                        traceback.format_exc()
            )
            return

        if not write_file: return

        root_element = ElementTree.Element("chat_simulation_data")
        xml_tree = ElementTree.ElementTree(root_element)

        characters_element = ElementTree.SubElement(root_element, "characters")
        for character in global_characters.values():
            character_element = ElementTree.SubElement(characters_element, "character")
            character_element.set("name", character.name)
            character.profile_photo.seek(0, io.SEEK_SET)
            character_element.set("profile_photo", base64.b64encode(gzip.compress(character.profile_photo.read(), 9)).decode())

        current_select_element = ElementTree.SubElement(characters_element, "current_select")
        if self.char_selection_window.character_listbox.cur_select:
            current_select_element.set("name", self.char_selection_window.character_listbox.cur_select.people.name)

        mains_element = ElementTree.SubElement(characters_element, "main_character")

        for main in self.char_selection_window.main_char:
            main_name_element = ElementTree.SubElement(mains_element, "character")
            main_name_element.set("name", main.name)

        messages_element = ElementTree.SubElement(root_element, "messages")
        for message in self.chat_window.messages:
            message_element = ElementTree.SubElement(messages_element, "message")
            message_element.set("sender", message.people.name)
            if isinstance(message, SingleTextMsg):
                message_element.set("type", "text")
                message_element.text = message.content
            elif isinstance(message, SinglePhotoMsg):
                message_element.set("type", "photo")
                message.content.seek(0, io.SEEK_SET)
                message_element.text = base64.b64encode(gzip.compress(message.content.read(), 9)).decode()

        ElementTree.indent(xml_tree, space="    ")
        xml_tree.write(write_file, encoding="unicode", xml_declaration=True)
        tkinter.messagebox.showinfo(message="Chat saved to %s." % write_file.name)

    def load(self):
        try:
            read_file = tkinter.filedialog.askopenfile(
                filetypes=[
                    ("XML file", "*.xml")
                ]
            )
        except:
            tkinter.messagebox.showerror(
                title="Error while loading chat",
                message="Error occurred while loading chat.\n"
                        "The full traceback is:\n" +
                        traceback.format_exc()
            )
            return

        if not read_file: return

        for message in self.chat_window.messages:
            message._delete()
        for character in self.char_selection_window.character_listbox.characters[:]:
            character.selection_button.invoke()
            self.char_selection_window._del_character()

        try:
            xml_tree = ElementTree.parse(read_file)
        except:
            tkinter.messagebox.showerror(
                title="Error while loading chat",
                message="Error occurred while loading chat.\n"
                        "The full traceback is:\n" +
                        traceback.format_exc()
            )
            return

        current_select_name = xml_tree.find("characters").find("current_select").get("name")
        for character in xml_tree.find("characters").iterfind("character"):
            name = character.get("name")
            profile_photo = io.BytesIO(gzip.decompress(base64.b64decode(character.get("profile_photo"))))
            if name in global_characters:
                tkinter.messagebox.showerror(message="Duplicate character: %s" % name)
                continue

            self.char_selection_window._internal_add_character(name, profile_photo)
            if current_select_name == name:
                self.char_selection_window.on_selectchar(global_characters[current_select_name], False)

        main_character_name = [i.get("name")
                               for i in xml_tree.find("characters").find("main_character").iterfind("character")]

        for char in self.char_selection_window.character_listbox.characters:
            if char.people.name in main_character_name:
                char.on_select_main()

        for char in self.char_selection_window.character_listbox.characters:
            if char.people.name == current_select_name:
                if global_characters[current_select_name].name in main_character_name:
                    char.on_select_main()
                else:
                    char.on_select()
                break

        for message in xml_tree.find("messages").iterfind("message"):
            sender = message.get("sender")
            if sender not in global_characters:
                tkinter.messagebox.showerror(message="Character not found: %s" % sender)
                continue

            if message.get("type") == "text":
                content = message.text
                self.chat_window.add_msg_text(global_characters[sender], content,
                                         global_characters[sender] in self.char_selection_window.main_char)
            elif message.get("type") == "photo":
                content = io.BytesIO(gzip.decompress(base64.b64decode(message.text)))
                self.chat_window.add_msg_photo(global_characters[sender], content,
                                         global_characters[sender] in self.char_selection_window.main_char)

        tkinter.messagebox.showinfo(message="Chat loaded from %s." % read_file.name)
