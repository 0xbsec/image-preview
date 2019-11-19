from watchdog.events import PatternMatchingEventHandler  

class DirectoryImagesHandler(PatternMatchingEventHandler):
    patterns = [
            "*.bmp",
            "*.gif",
            "*.jpg",
            "*.jpeg",
            "*.png",
            "*.pbm",
            "*.pgm",
            "*.ppm",
            "*.xbm",
            "*.xpm",
        ]

    def set_image_selector(self, image_selector):
        self.image_selector = image_selector

    def refresh(self):
        if not self.image_selector:
            return

        self.image_selector.refresh()

    def on_moved(self, event):
        self.refresh()

    def on_deleted(self, event):
        self.refresh()

    def on_modified(self, event):
        self.refresh()

    def on_created(self, event):
        self.refresh()

