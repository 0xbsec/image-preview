"""
  Take list of directories, and get image based on the provided strategy (random, sequential, date desc, recently added ...)
"""

import pathlib
import os
import textwrap
from random import choice


class ImageSelector:
    def __init__(self, directories=[]):
        self.directories = directories
        self.images = self.get_images(self.directories)

    def refresh(self):
        """
        Reload image lists (e.g. when a new image get added, we'll pick it up)
        """
        self.images = self.get_images(self.directories)

    def get_next_image_with_stats(self):
        response = {}

        _index, next_img = self.get_next_image()
        if not next_img:
            return None

        response["img"] = next_img
        response["stats"] = {
            "pos": _index,
            "total": len(self.images),
            "name": self.get_file_name(next_img),
        }

        return response

    def get_file_name(self, file):
        name, ext = os.path.splitext(os.path.basename(file))

        max_width = 15
        if len(name) > max_width:
            start = name[: max_width - 5]
            end = name[-5:]
            name = start + "..." + end

        return f"{name}{ext}"

    def get_next_image(self):
        # return random image for now with index
        if not self.images:
            return None, None

        _index = choice(range(len(self.images)))
        return _index + 1, self.images[_index]

    def get_images(self, directories):
        """
        Return list of images from the provided directories list
        """

        images = []

        # formats supported by QPixmap
        valid_extensions = [
            "bmp",
            "gif",
            "jpg",
            "jpeg",
            "png",
            "pbm",
            "pgm",
            "ppm",
            "xbm",
            "xpm",
        ]
        for directory in directories:
            for ext in valid_extensions:
                files = map(
                    lambda filepath: str(filepath.absolute()),
                    pathlib.Path(directory).glob(f"**/*.{ext}"),
                )

                images.extend(files)

        return images


if __name__ == "__main__":
    image_selector = ImageSelector(["/tmp/teste"])
    print(image_selector.images)
    print(image_selector.get_next_image())
