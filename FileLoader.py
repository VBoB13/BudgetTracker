import datetime
import csv
from Income import Income

class FileLoader:

    data = ""

    def __init__(self, readFile):
        self.file = readFile
        
    def loadPass(self):
        # Open's the 'pass.txt' file
        f = open(f"{self.file}", "r")

        # Attempts to read in the data from the file into variables for extraction
        if f.mode == 'r':
            fileContent = f.read()

        # Closes the file
        f.close()
        
        # Reads the collected data into the object's attribute "data"
        self.data = fileContent
        return self.data




if __name__ == '__main__':
	print("FileLoader.py is being run directly.")
else:
	print("FileLoader.py was imported.")