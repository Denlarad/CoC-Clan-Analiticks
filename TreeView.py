import tkinter
from tkinter import ttk


class CustomTreeView(ttk.Treeview):
    def __init__(self, root, show="", names=(), toSort=(),height=None):
        cols = tuple([f"#{i + 1}" for i in range(len(names))])
        super().__init__(root, show=show, columns=cols,height=height)
        self.columnsCount = len(cols)
        for i, col in enumerate(zip(cols, names)):
            if i in toSort:
                self.heading(col[0], text=col[1], command=lambda x=i: self.sort(x, True))
            else:
                self.heading(col[0], text=col[1])
            self.column(col[0], anchor=tkinter.CENTER, width=max(100,len(col[1])*7))
        ysb = ttk.Scrollbar(root, orient=tkinter.VERTICAL, command=self.yview)
        self.configure(yscroll=ysb.set)

    def sort(self, col, reverse):
        l = [(self.set(k, col), k) for k in self.get_children("")]
        if l[0][0].replace('.', '').isdigit():
            l = sorted(l, key=lambda x: float(x[0]), reverse=reverse)
        else:
            l = sorted(l, key=lambda x: x[0], reverse=reverse)
        for index, (_, k) in enumerate(l):
            self.move(k, "", index)
        for i in range(self.columnsCount):
            self.heading(i, command=lambda x=i: self.sort(x, True))

        self.heading(col, command=lambda: self.sort(col, not reverse))
