# This program will compare folders to each other, and change the "folder_to_change" to be an exact copy of
# the "model_folder." Call "traverse_folders" at the bottom of the program
import os
from os import listdir
from os.path import isfile, join, isdir
from send2trash import send2trash
import shutil


class File:

    def __init__(self, path):
        self.path = str(path)
        if "/" in self.path:
            self.path = path.replace("/", "\\")

    def get_path(self):
        return self.path

    def get_size(self):
        return os.stat(self.path).st_size

    def delete_file(self):
        send2trash(self.path)


class Directory:

    def __init__(self, path):
        self.path = str(path)
        if "/" in self.path:
            self.path = path.replace("/", "\\")

    def get_path(self):
        return self.path

    def get_subdirs(self):
        # Returns a list of each subdirectory path
        subdirs = [self.path + "\\" + f for f in os.listdir(self.path) if isdir(join(self.path, f))]
        if subdirs == []:
            return None
        return subdirs

    def subdir_ends(self):
        # returns a list of each
        return [f for f in os.listdir(self.path) if isdir(join(self.path, f))]

    def num_of_subdirs(self):
        subdirs = self.get_subdirs()
        if subdirs == None:
            return 0
        else:
            return len(subdirs)

    def get_files(self):
        # Returns a list of all files inside the directory
        files = [self.path + "\\" + f for f in listdir(self.path) if isfile(join(self.path, f))]
        if "desktop.ini" in files:
            files = files[1:]
        return files

    def delete_dir(self):
        send2trash(self.path)


# This is used rarely, when we need to empty out the contents of and entire folder (and its subfolders) into one place
# This is all done recursively. Parameters taken in as objects
def empty_subdirs(to_empty, destination):
    # print(f"empty_subdirs         {to_empty.get_path()}  |  {destination.get_path()}")

    if to_empty.get_subdirs():
        if to_empty.num_of_subdirs() > 1:
            for folder in to_empty.get_subdirs():
                empty_subdirs(Directory(folder), destination)
        else:
            empty_subdirs(Directory(to_empty.get_subdirs()[0]), destination)

    for file in to_empty.get_files():
        try:
            os.rename(file, destination.get_path() + file[file.rindex("\\"):])
        except FileExistsError:
            file = File(file)
            file.delete_file()
    to_empty.delete_dir()


# When this function is called, it will copy over every file in a directory from model_folder to to_change
# Extra files in to_change but not model_folder will be deleted. Parameters are taken as Directory class objects
def copy_files(to_change, model_folder):
    # print(f"copy_files          {to_change.get_path()}  |  {model_folder.get_path()}")

    # This is where we check to see if there are any subdirectories in to_change that are not in model_folder
    # If there are, then we empty and delete them by calling empty_subdirs() above
    if to_change.num_of_subdirs() > 0:

        if to_change.num_of_subdirs() > 1:
            for subdir in to_change.subdir_ends():
                if subdir not in model_folder.subdir_ends():
                    empty_subdirs(Directory(to_change.get_path() + "\\" + subdir), to_change)
        else:
            if to_change.subdir_ends()[0] not in model_folder.subdir_ends():
                empty_subdirs(Directory(to_change.get_path() + "\\" + to_change.subdir_ends()[0]), to_change)

    # Here we will iterate through every file in to_change. If a file has a matching filepath and byte size it
    # is left alone. If not, it is deleted.
    model_folder_files = [file[file.rindex("\\") + 1:] for file in model_folder.get_files()]
    for file in to_change.get_files():
        if file[file.rindex("\\") + 1:] not in model_folder_files:
            File(file).delete_file()

    # Then, we iterate through every file in model_folder.
    # If there is not a matching filepath in to_change the file is copied over
    to_change_files = [file[file.rindex("\\") + 1:] for file in to_change.get_files()]
    for file in model_folder.get_files():

        if file[file.rindex("\\") + 1:] in to_change_files:
            to_model_file = File(file)
            to_change_file = File(to_change.get_path() + file[file.rindex("\\"):])
            if to_model_file.get_size() == to_change_file.get_size():
                continue
            else:
                to_change_path = to_change_file.get_path()
                to_change_file.delete_file()
                shutil.copyfile(to_model_file.get_path(), to_change_path)
        else:
            shutil.copyfile(file, to_change.get_path() + file[file.rindex("\\"):])




# Here is a function that will copy over an entire folder from scratch. It recurses through each level of
# subdirectories until it finds a directory without any subdirectories. Then each folder is copied over
# Both parameters take in file paths as strings
def copy_entire_folder(to_change, model_folder):
    # print(f"copy_entire_folder  {to_change.get_path()}  |  {model_folder.get_path()}")

    to_change, model_folder = Directory(to_change), Directory(model_folder)
    if model_folder.get_subdirs():
        for folder in model_folder.get_subdirs():
            new_fold = to_change.get_path() + folder[folder.rindex("\\"):]
            os.mkdir(new_fold)
            copy_entire_folder(new_fold, folder)
    copy_files(Directory(to_change.get_path()), Directory(model_folder.get_path()))




# Here is a recursive function that will call copy_folders() on any folder at the lowest level in model_folder,
# and then call copy_folders() on every function coming back up
def traverse_folders(folder_to_change, model_folder):

    to_change = Directory(folder_to_change)
    model_folder = Directory(model_folder)
    if model_folder.get_subdirs():

        if to_change.get_subdirs():
            to_change_subdirs = [dir[dir.rindex("\\") + 1:] for dir in to_change.get_subdirs()]
            model_subdirs = [dir[dir.rindex("\\") + 1:] for dir in model_folder.get_subdirs()]
            for dir in model_subdirs:
                if dir in to_change_subdirs:
                    traverse_folders(to_change.get_path() + "\\" + dir, model_folder.get_path() + "\\" + dir)
                else:
                    new_path = to_change.get_path() + "\\" + dir
                    os.mkdir(new_path)
                    copy_entire_folder(new_path, model_folder.get_path() + "\\" + dir)

        else:
            for subdir in model_folder.get_subdirs():
                new_path = to_change.get_path() + subdir[subdir.rindex("\\"):]
                os.mkdir(new_path)
                copy_entire_folder(new_path, subdir)
            copy_files(to_change, model_folder)

    copy_files(to_change, model_folder)


# Call traverse folders here. Pathways must use either "/" or "\\" to separate folders, not just "\"
# Example: traverse_folders('C:\\Users\\Colby Hehman\\Pictures\\Camera Roll',
# 'C:\\Users\\Colby Hehman\\Pictures\\Backups\\Camera Roll Backup')
# Remember that the folder_to_change (first parameter) will change to be a copy of the model_folder (second parameter)
traverse_folders('', '')
