from classes import *


def init_root():
    root = tk.Tk()
    root.geometry(SCREEN_SIZE)
    root.title(SCREEN_TITLE)
    return root


def do_quit(root: tk.Tk, manager: FileManager):
    settings.running = False
    manager.join()
    root.destroy()
    settings.save()


def main():
    root = init_root()
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    manager = FileManager(root)
    MainMenu(root, manager)
    root.protocol('WM_DELETE_WINDOW', lambda: do_quit(root, manager))
    root.mainloop()


if __name__ == '__main__':
    main()
