import customtkinter


class LoadingFrame:
    def __init__(self, name, root, max):
        self.root = root
        self.max = max
        self.loadingFrame = customtkinter.CTkFrame(self.root, border_color="white", border_width=1)
        self.loadingFrame.place(relx=0.5, rely=0.4, relwidth=0.5, relheight=0.2, anchor=customtkinter.CENTER)
        self.frameName = customtkinter.CTkLabel(self.loadingFrame, text=f"{name}", font=("Sans serif", 32))
        self.frameName.pack(pady=10)
        self.progressBar = customtkinter.CTkProgressBar(self.loadingFrame)
        self.progressBar.set(0)
        self.progressBar.pack()
        self.loadingLabel = customtkinter.CTkLabel(self.loadingFrame, text="")
        self.loadingLabel.pack()

    def nextStep(self, label="", iter=True, skip=-1):
        self.loadingLabel.configure(text=label)
        if iter:
            self.progressBar.set(self.progressBar.get() + 1 / self.max)
        if skip >= 0:
            self.progressBar.set(skip / self.max)

    def close(self):
        self.loadingFrame.destroy()