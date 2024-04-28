import os

# Specify the folder path
folder_path = os.getcwd()

# List all files in the folder
files = os.listdir(folder_path)

# Specify the name of the text file
txt_file_path = os.getcwd()+'/WheelsNames.txt'

# Open the text file in write mode
with open(txt_file_path, 'w') as txt_file:
    # Write each file name with extension to the text file
    for file in files:
        txt_file.write(file + '\n')

print(f"File names with extensions have been written to {txt_file_path}")