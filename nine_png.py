import PIL.Image

class NinePNG:
    def __init__(self, png_file: str):
        self.img = PIL.Image.open(png_file)
        pixels = tuple(self.img.getdata())
        is_black = lambda x, y: pixels[y * self.img.width + x] == (0, 0, 0, 255)

        # find margins and patches now
        self.top_patch = tuple(i for i in range(self.img.width)
                          if is_black(i, 0))

        self.left_patch = tuple(i for i in range(self.img.height)
                           if is_black(0, i))

        self.right_margin = tuple(i for i in range(self.img.height)
                             if is_black(self.img.width - 1, i))

        self.bottom_margin = tuple(i for i in range(self.img.width)
                              if is_black(i, self.img.height - 1))

    def scale(self, size: tuple[int]) -> PIL.Image.Image:
        # PIL has no scale function to scale .9.png
        # so we do scaling normally:
        # cut the image into 9 pieces:
        #                    top patch
        #   /------------------|----|------------------\
        #   |                  |hori|                  |
        #   |                  |zont|                  |
        #   |                  |al  |                  |
        #   |   don't scale    |    |   don't scale    |
        # l |                  |    |                  |
        # e |                  |    |                  |
        # f |                  |    |                  |
        # t |                  |    |                  |
        #   |------------------------------------------|
        # p |    vertical      |both|      scale       |
        # a |------------------------------------------|
        # t |                  |scal|                  |
        # c |                  |e   |                  |
        # h |   don't scale    |    |   don't scale    |
        #   |                  |    |                  |
        #   |                  |    |                  |
        #   |                  |    |                  |
        #   \------------------------------------------/

        # non-scale images
        lefttop_orig = self.img.crop(
            (0, 0, self.top_patch[0], self.left_patch[0])
        )
        righttop_orig = self.img.crop(
            (self.top_patch[-1], 0, self.img.width - 1, self.left_patch[0])
        )
        leftbottom_orig = self.img.crop(
            (0, self.left_patch[-1], self.top_patch[0], self.img.height - 1)
        )
        rightbottom_orig = self.img.crop(
            (self.top_patch[-1], self.left_patch[-1], self.img.width - 1, self.img.height - 1)
        )

        # vertical-scale images
        leftvertical_scale = self.img.resize(
            (lefttop_orig.width,
             size[1] - lefttop_orig.height - leftbottom_orig.height + 1),
            PIL.Image.Resampling.BOX,
            (0, self.left_patch[0], self.top_patch[0], self.left_patch[-1])
        )
        rightvertical_scale = self.img.resize(
            (righttop_orig.width,
             size[1] - righttop_orig.height - rightbottom_orig.height + 1),
            PIL.Image.Resampling.BOX,
            (self.top_patch[-1], self.left_patch[0], self.img.width - 1, self.left_patch[-1])
        )

        # horizontal-scale images
        tophorizontal_scale = self.img.resize(
            (size[0] - lefttop_orig.width - righttop_orig.width + 1,
             lefttop_orig.height),
            PIL.Image.Resampling.BOX,
            (self.top_patch[0], 0, self.top_patch[-1], self.left_patch[0])
        )
        bottomhorizontal_scale = self.img.resize(
            (size[0] - leftbottom_orig.width - rightbottom_orig.width + 1,
             leftbottom_orig.height),
            PIL.Image.Resampling.BOX,
            (self.top_patch[0], self.left_patch[-1], self.top_patch[-1], self.img.height - 1)
        )

        # both-scale image
        both_scale = self.img.resize(
            (size[0] - lefttop_orig.width - righttop_orig.width + 1,
             size[1] - lefttop_orig.height - leftbottom_orig.height + 1),
            PIL.Image.Resampling.BOX,
            (self.top_patch[0], self.left_patch[0], self.top_patch[-1], self.left_patch[-1])
        )

        # now paste them together
        ret = PIL.Image.new("RGBA", (size[0] + 1, size[1] + 1))

        ret.paste(lefttop_orig)
        ret.paste(tophorizontal_scale, (self.top_patch[0], 0))
        ret.paste(righttop_orig, (self.top_patch[0] + tophorizontal_scale.width, 0))
        ret.paste(leftvertical_scale, (0, self.left_patch[0]))
        ret.paste(both_scale, (self.top_patch[0], self.left_patch[0]))
        ret.paste(rightvertical_scale, (self.top_patch[0] + both_scale.width, self.left_patch[0]))
        ret.paste(leftbottom_orig, (0, self.left_patch[0] + leftvertical_scale.height))
        ret.paste(bottomhorizontal_scale, (self.top_patch[0], self.left_patch[0] + leftvertical_scale.height))
        ret.paste(rightbottom_orig, (self.top_patch[0] + bottomhorizontal_scale.width, self.left_patch[0] + leftvertical_scale.height))
        ret = ret.crop((1, 1, ret.width, ret.height))

        return ret
