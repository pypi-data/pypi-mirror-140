"""
Welcome page is the entry page for your game!
"""

from pyggui.gui import Page, Text


class WelcomePage(Page):
    def __init__(self, controller):
        super().__init__(controller)

        self.add_item(
            item=Text(
                value="Welcome to PyGgui!",
                position=[100, 100],
                font_size=46
            )
        )
