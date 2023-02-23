characters = {}

class Character:
    # name is character name
    # profile_photo is THE OPENED PHOTO FILE OBJECT
    def __init__(self, name, profile_photo):
        self.name = name
        self.profile_photo = profile_photo
