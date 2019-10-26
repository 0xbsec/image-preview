"""
  Take list of directories, and get image based on the provided strategy (random, sequential, date desc, recently added ...)
"""

import pathlib
from random import choice

class ImageSelector:
    def __init__(self, directories=[]):
        # self.directories = directories
        self.images = self.get_images(directories)

    def refresh(self):
        """
        Reload image lists (e.g. when a new image get added, we'll pick it up)
        """
        pass

    def get_next_image(self):
        return choice(self.images)

    def get_images(self, directories):
        """
        Return list of images from the provided directories list
        """

        images = []

        # formats supported by QPixmap
        valid_extensions = ["bmp", "gif", "jpg", "jpeg", "png", "pbm", "pgm" ,"ppm", "xbm", "xpm"]
        for directory in directories:
            for ext in valid_extensions:
                files = map(lambda filepath: str(filepath.absolute()), pathlib.Path(directory).glob(f"**/*.{ext}"))

                images.extend(files)

        return images


if __name__ == "__main__":
    image_selector = ImageSelector(['/tmp/teste'])
    print(image_selector.images)
    print(image_selector.get_next_image())
