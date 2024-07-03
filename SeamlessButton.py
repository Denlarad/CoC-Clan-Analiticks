import customtkinter
from customtkinter import CTkFont


class SeamlessButton(customtkinter.CTkButton):
    def __init__(self, root, text="", command=None, height=40, anchor="w", font=None,corner_radius = 0,border_width = None):
        font = CTkFont() if font is None else font
        super().__init__(root, corner_radius=corner_radius, height=height, border_spacing=10,
                         text=text,
                         fg_color="transparent", text_color=("gray10", "gray90"),
                         hover_color=("gray70", "gray30"),
                         font=font,
                         anchor=anchor,
                         command=command,
                         border_width=border_width)
