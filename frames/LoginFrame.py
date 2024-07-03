import asyncio
import webbrowser
from pathlib import Path

import coc
import customtkinter
import keyring

import settings


class LoginFrame:

    @staticmethod
    def relative_to_assets(path: str) -> Path:
        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / Path(r"D:\clanAnalitics\assets\frame0")
        return ASSETS_PATH / Path(path)

    def __init__(self, root, parent, loop):
        self.root = root
        self.parent = parent
        self.loop = loop
        self.loginFrame = customtkinter.CTkFrame(self.root, width=1280, height=720)

        self.frameName = customtkinter.CTkLabel(self.loginFrame, text=f"Войдите или зарегистрируйтесь",
                                                font=("Sans serif", 32))
        self.frameName.pack(pady=10,padx=10)

        customtkinter.CTkLabel(self.loginFrame, text="Email:").pack()

        self.loginEntry = customtkinter.CTkEntry(self.loginFrame)
        self.loginEntry.pack(pady=10)

        customtkinter.CTkLabel(self.loginFrame, text="Пароль:").pack()
        self.passwordEntry = customtkinter.CTkEntry(self.loginFrame, show="*")
        self.passwordEntry.pack()

        self.passwordEntry.bind("<Return>", lambda x: self.loop.create_task(self.logIn()))

        registerButton = customtkinter.CTkButton(self.loginFrame, text="Зарегестрироватся")
        registerButton.pack(pady=10, padx=30)

        logButton = customtkinter.CTkButton(self.loginFrame, text="войти")
        logButton.pack()

        self.errorLabel = customtkinter.CTkLabel(self.loginFrame, text="", text_color="red")
        self.errorLabel.pack(pady=5)

        registerButton.bind("<Button-1>", lambda x: webbrowser.open_new("https://developer.clashofclans.com/#/"))
        logButton.bind("<Button-1>", lambda x:self.loop.create_task(self.logIn()))

    def show(self):
        self.loginFrame.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

    async def logIn(self):
        self.errorLabel.configure(text="")
        mail = self.loginEntry.get()
        password = self.passwordEntry.get()
        if await self.testLog(mail, password):
            keyring.set_password("OOOMEGALUL", mail, password)
            settings.saveSetting("emailInUse", mail)
            self.loginFrame.place_forget()
            self.loop.create_task(self.parent.create(mail))

    async def testLog(self, login, password):
        async with coc.Client() as coc_client:
            try:
                await self.loop.create_task(coc_client.login(login, password))
                return True
            except coc.InvalidCredentials as error:
                self.errorLabel.configure(text="Проверте введенные данные")
                return False
