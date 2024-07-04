from gui import *
import threading
from typing import Optional
from tkinter import filedialog as fd
import subprocess


class FileManager:
    def __init__(self, root: tk.Tk):
        self._directory = settings.scan_directory
        self._root = root
        self._file_path = FILE_PATH
        self._status = Status.REST

        self._file_list = []
        self._folder_list = []
        self._errors = 0

        self._thread_lock = threading.Lock()
        self._scan_thread: Optional[threading.Thread] = None
        self._stop_scan = False

        self._frame = tk.Frame(self._root)
        self._frame.grid(row=0, column=0, sticky=tk.NSEW)
        self._frame.grid_columnconfigure(0, weight=1)
        self._frame.grid_rowconfigure(2, weight=1)

        self._log_text = Text(self._frame, '', (0, 0))
        self._log_text.draw(sticky=tk.NSEW)

        self._scan_button = Button(self._frame, 'Scan', (0, 1), self.start_scan)
        self._scan_button.draw(sticky=tk.NSEW)

        self._search_input = InputBox(self._frame, 'Search', (1, 0))
        self._search_input.draw(sticky=tk.NSEW)

        self._search_button = Button(self._frame, 'Search', (1, 1), self._do_search)
        self._search_button.draw(sticky=tk.NSEW)

        self._result = Table(self._frame, ['file name', 'file path'], (2, 0))
        self._result.draw(columnspan=2, sticky=tk.NSEW)
        self._result.bind('<Double-Button-1>', self._open_file)
        self._result.bind('<Return>', self._open_file)

        if not self._read():
            self.start_scan()

    def stop_scan(self):
        self._stop_scan = True
        self.join()
        self._stop_scan = False

    def start_scan(self, stop_if_running=False):
        if stop_if_running:
            self.stop_scan()
        if self._status == Status.REST:
            self._root.after(0, self._check_log)
            self._scan_thread = threading.Thread(target=self._scan)
            self._scan_thread.start()

    def _scan(self):
        self._directory = settings.scan_directory
        self._status = Status.SCAN
        self._file_list = []
        self._folder_list = []
        to_check = [self._directory]
        self._errors = 0
        while to_check and settings.running and not self._stop_scan:
            current_dir = to_check.pop(0)
            try:
                for file_name in os.listdir(current_dir):
                    file_path = os.path.join(current_dir, file_name)
                    if os.path.isdir(file_path):
                        to_check.append(file_path)
                        self._folder_list.append(file_path)
                    else:
                        self._file_list.append(file_path)
            except PermissionError:
                self._errors += 1
        if not to_check:
            self._file_list = [os.path.normpath(f) for f in self._file_list]
            self._folder_list = [os.path.normpath(f) for f in self._folder_list]
            self._file_list.sort(key=os.path.basename)
            self._folder_list.sort(key=os.path.basename)
            self._write()
            self._status = Status.FINISH_SCAN
        else:
            self._status = Status.REST
        self._scan_thread = None

    def _write(self):
        with open(self._file_path, 'wb+') as my_file:
            my_file.write(pickle.dumps((self._file_list, self._folder_list, self._errors)))

    def _read(self):
        self._file_list = []
        try:
            with open(self._file_path, 'rb') as my_file:
                self._file_list, self._folder_list, self._errors = pickle.loads(my_file.read())
            return True
        except FileNotFoundError:
            return False

    def _check_log(self):
        if self._status == Status.SCAN:
            self._thread_lock.acquire()
            self._log_text.text = self._text
            self._thread_lock.release()
            self._root.after(100, self._check_log)
        elif self._status == Status.FINISH_SCAN:
            self._log_text.text = f"Finish! {self._text}"
            self._status = Status.REST
            self._root.after(100, self._check_log)

    @staticmethod
    def remove_by_type(all_files, all_folders):
        allowed_types = set()
        for i in range(len(settings.file_types) - 1):
            if settings.file_types[i]:
                allowed_types.update(FILE_TYPES[i].value)
        allowed_files = []
        for item in all_files:
            if os.path.splitext(item)[1].replace('.', '') in allowed_types:
                allowed_files.append(item)
        if settings.file_types[4]:
            allowed_files += all_folders
        if settings.file_types[-1]:
            not_allowed_types = set()
            for types in FILE_TYPES:
                not_allowed_types.update(types.value)
            for item in all_files:
                if os.path.splitext(item)[1].replace('.', '') not in not_allowed_types:
                    allowed_files.append(item)
        return allowed_files

    @staticmethod
    def remove_by_subfolder(allowed_files):
        return [item for item in allowed_files if settings.source_directory in item]

    @staticmethod
    def _find_by_full_name(value):
        return os.path.basename(value)

    def _find_by_start_name(self, value):
        return os.path.basename(value)[: len(self._search_input.value)]

    def _do_search(self):
        search_function = self._find_by_full_name if settings.find_by == FindBy.FULL_NAME else self._find_by_start_name
        min_index, max_index = find_all(self._file_list, self._search_input.value, search_function)
        all_files = [self._file_list[i] for i in range(min_index, max_index)]
        min_index, max_index = find_all(self._folder_list, self._search_input.value, search_function)
        all_folders = [self._folder_list[i] for i in range(min_index, max_index)]
        allowed_files = self.remove_by_type(all_files, all_folders)
        in_source_dir = self.remove_by_subfolder(allowed_files)
        self._result.empty()
        for i, path in enumerate(in_source_dir):
            self._result.add([os.path.basename(path), path])

    def _open_file(self, _):
        for item in self._result.selection_value:
            path = item[1]
            if os.path.isdir(path):
                subprocess.run(['explorer.exe', path])
            else:
                subprocess.run(['explorer.exe', '/select,', path])

    @property
    def _text(self):
        return f'{len(self._file_list)} files in {len(self._folder_list)} folders and {self._errors} errors'

    def join(self):
        if self._scan_thread:
            self._scan_thread.join()


class MainMenu:
    def __init__(self, master: tk.Tk, manager: FileManager):
        self._master = master
        self._manager = manager

        self._main_menu = tk.Menu(master, tearoff=False)
        self._filter_menu = tk.Menu(self._main_menu, tearoff=False)
        self._main_menu.add_cascade(label='filter', menu=self._filter_menu)

        self._filter_menu.add_command(label='Scan Directory', command=self._scan_dir_cmd)
        self._filter_menu.add_command(label='Source Directory', command=self._source_dir_cmd)

        self._find_by_var = tk.IntVar(value=settings.find_by)
        self._find_by_menu = tk.Menu(self._filter_menu, tearoff=False)
        self._find_by_menu.add_radiobutton(label='Full Name', value=FindBy.FULL_NAME, variable=self._find_by_var,
                                           command=self._find_by_cmd)
        self._find_by_menu.add_radiobutton(label='Start Name', value=FindBy.START_NAME, variable=self._find_by_var,
                                           command=self._find_by_cmd)
        self._filter_menu.add_cascade(label='Find By', menu=self._find_by_menu)

        self._file_type_menu = tk.Menu(self._filter_menu, tearoff=False)
        self._type_all = tk.IntVar()
        self._file_type_menu.add_checkbutton(label='All', variable=self._type_all, command=self._file_type_all_cmd)
        self._type_image = tk.IntVar()
        self._file_type_menu.add_checkbutton(label='Image', variable=self._type_image, command=self._type_changed)
        self._type_video = tk.IntVar()
        self._file_type_menu.add_checkbutton(label='Video', variable=self._type_video, command=self._type_changed)
        self._type_document = tk.IntVar()
        self._file_type_menu.add_checkbutton(label='Document', variable=self._type_document, command=self._type_changed)
        self._type_app = tk.IntVar()
        self._file_type_menu.add_checkbutton(label='App', variable=self._type_app, command=self._type_changed)
        self._type_folder = tk.IntVar()
        self._file_type_menu.add_checkbutton(label='Folder', variable=self._type_folder, command=self._type_changed)
        self._type_audio = tk.IntVar()
        self._file_type_menu.add_checkbutton(label='Audio', variable=self._type_audio, command=self._type_changed)
        self._type_other = tk.IntVar()
        self._file_type_menu.add_checkbutton(label='Other', variable=self._type_other, command=self._type_changed)
        self._filter_menu.add_cascade(label='File Type', menu=self._file_type_menu)

        self._types = settings.file_types

        master.config(menu=self._main_menu)

    @property
    def _types(self):
        return [item.get() for item in [self._type_image,
                                        self._type_video,
                                        self._type_document,
                                        self._type_app,
                                        self._type_folder,
                                        self._type_audio,
                                        self._type_other]]

    @_types.setter
    def _types(self, types):
        items = [self._type_image,
                 self._type_video,
                 self._type_document,
                 self._type_app,
                 self._type_folder,
                 self._type_audio,
                 self._type_other]
        for i in range(len(types)):
            items[i].set(types[i])
        self._type_changed()

    @property
    def _all_types(self):
        all_on = 0 not in self._types
        return 1 if all_on else 0

    def _scan_dir_cmd(self):
        directory = fd.askdirectory()
        if directory:
            settings.scan_directory = os.path.normpath(directory)
            self._manager.start_scan(True)

    @staticmethod
    def _source_dir_cmd():
        directory = fd.askdirectory()
        if directory:
            settings.source_directory = os.path.normpath(directory)

    def _find_by_cmd(self):
        settings.find_by = self._find_by_var.get()

    def _file_type_all_cmd(self):
        value = self._type_all.get()
        self._type_image.set(value)
        self._type_video.set(value)
        self._type_document.set(value)
        self._type_app.set(value)
        self._type_folder.set(value)
        self._type_audio.set(value)
        self._type_other.set(value)
        self._type_changed()

    def _type_changed(self):
        self._type_all.set(self._all_types)
        settings.file_types = self._types

    def _save_settings(self):
        pass

    def _reset_settings(self):
        pass


def binary_search(items, item, key=lambda item: item):
    first = 0
    last = len(items) - 1
    index = -1
    item = key(item)
    while first <= last and index == -1:
        midpoint = (first + last) // 2
        item2 = key(items[midpoint])
        if item == item2:
            index = midpoint
        elif item < item2:
            last = midpoint - 1
        else:
            first = midpoint + 1
    return index


def find_all(items, item, key=lambda item: item):
    index = binary_search(items, item, key)
    if index == -1:
        return -1, -1
    min_index = max_index = index
    while min_index >= 0 and key(items[min_index]) == key(item):
        min_index -= 1
    min_index += 1
    while max_index < len(items) and key(items[max_index]) == key(item):
        max_index += 1
    max_index -= 1
    return min_index, max_index + 1


def open_explorer(path):
    if os.path.isdir(path):
        return lambda: subprocess.run(['explorer.exe', path])
    else:
        return lambda: subprocess.run(['explorer.exe', '/select,', path])
