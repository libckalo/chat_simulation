import tkinter
import tkinter.filedialog
import gzip
import base64
import io
import xml.etree.ElementTree as ElementTree
from .character_database import characters as global_characters
from .character_database import Character
from ..chat_window.character_selection_window import CharSelectionWindow
from ..chat_window.main_chat_window import ChatWindow

# The saved chat xml is as follows:
# <chat_simulation_data>
#     <characters>
#         <character>
#             <name>TEST 1</name>
#             <profile_photo>
#                 <!-- profile photo, gzip compressed, base64 encoded -->
#             </profile_photo>
#         </character>
#         ......
#         <current_select>TEST 1</current_select>
#         <mains>
#             <name>TEST 1</name> <!-- must be one of the character above -->
#             ......
#         </mains>
#     </characters>
#     <messages>
#         <message>
#             <sender>TEST 1</sender> <!-- must be one of the character above -->
#             <content>hello world</content>
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
        write_file = tkinter.filedialog.asksaveasfile(
            initialfile="chat.xml",
            filetypes=[
                ("XML file", "*.xml")
            ]
        )
        if not write_file: return
        
        root_element = ElementTree.Element("chat_simulation_data")
        xml_tree = ElementTree.ElementTree(root_element)

        characters_element = ElementTree.SubElement(root_element, "characters")
        for character in global_characters.values():
            character_element = ElementTree.SubElement(characters_element, "character")
            name_element = ElementTree.SubElement(character_element, "name")
            name_element.text = character.name
            profile_photo_element = ElementTree.SubElement(character_element, "profile_photo")
            character.profile_photo.seek(0, io.SEEK_SET)
            profile_photo_element.text = base64.b64encode(gzip.compress(character.profile_photo.read(), 9)).decode()

        current_select_element = ElementTree.SubElement(characters_element, "current_select")
        if self.char_selection_window.character_listbox.cur_select:
            current_select_element.text = self.char_selection_window.character_listbox.cur_select.people.name

        mains_element = ElementTree.SubElement(characters_element, "mains")
        for main in self.char_selection_window.main_char:
            main_name_element = ElementTree.SubElement(mains_element, "name")
            main_name_element.text = main.name

        messages_element = ElementTree.SubElement(root_element, "messages")
        for message in self.chat_window.messages:
            message_element = ElementTree.SubElement(messages_element, "message")
            sender_element = ElementTree.SubElement(message_element, "sender")
            sender_element.text = message.people.name
            content_element = ElementTree.SubElement(message_element, "content")
            content_element.text = message.content

        ElementTree.indent(xml_tree, space='    ')
        xml_tree.write(write_file, encoding="unicode", xml_declaration=True)

    def load(self):
        read_file = tkinter.filedialog.askopenfile(
            filetypes=[
                ("XML file", "*.xml")
            ]
        )
        if not read_file: return

        for message in self.chat_window.messages:
            message._delete()
        for character in self.char_selection_window.character_listbox.characters[:]:
            character.selection_button.invoke()
            self.char_selection_window._del_character()

        xml_tree = ElementTree.parse(read_file)
        current_select_name = xml_tree.find("characters").find("current_select").text
        for character in xml_tree.find("characters").iterfind("character"):
            name = character.find("name").text
            profile_photo = io.BytesIO(gzip.decompress(base64.b64decode(character.find("profile_photo").text)))
            if name in global_characters:
                tkinter.messagebox.showerror(message="Duplicate character: %s" % name)
                continue

            self.char_selection_window.add_character_callback(name, profile_photo)
            if current_select_name == name:
                self.char_selection_window.on_selectchar(global_characters[current_select_name], False)

        mains_name = [i.text for i in xml_tree.find("characters").find("mains").iterfind("name")]

        for char in self.char_selection_window.character_listbox.characters:
            if char.people.name in mains_name:
                char.on_select_main()

        for char in self.char_selection_window.character_listbox.characters:
            if char.people.name == current_select_name:
                if global_characters[current_select_name] in mains_name:
                    char.on_select_main()
                else:
                    char.on_select()
                break
        
        for message in xml_tree.find("messages").iterfind("message"):
            sender = message.find("sender").text
            content = message.find("content").text
            if sender not in global_characters:
                tkinter.messagebox.showerror(message="Character not found: %s" % sender)
                continue

            self.chat_window.add_msg(global_characters[sender], content,
                                     global_characters[sender] in self.char_selection_window.main_char)
