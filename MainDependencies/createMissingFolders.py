import os

def create_folder_if_missing(folder_path):
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            print(f"Folder created at: {folder_path}")
        except Exception as error_text:
            print(f"Folder creation failed: {error_text}")