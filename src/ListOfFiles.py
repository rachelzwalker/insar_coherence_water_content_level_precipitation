import os

def get_list_of_files(directory: str) -> list:
    list_of_files = []
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            list_of_files.append(os.path.join(subdir, file))
    return list_of_files

class GetListShapefiles:
    def __init__(self, shape_file_path: str):
        self.shape_file_path = shape_file_path

    def get_list_of_shapefiles(self) -> list:
        list_of_shape_files_with_additional_files = get_list_of_files(self.shape_file_path)
        list_of_shape_files = [x for x in list_of_shape_files_with_additional_files if "shp" in x]
        list_of_shape_files_focused = self._list_of_focused_shapefiles(list_of_shape_files)
        list_of_shape_files_joined = self._list_of_joined_shape_files(list_of_shape_files_focused)
        return list_of_shape_files_joined

    @staticmethod
    def _list_of_joined_shape_files(list_of_focused_shape_files: list) -> list:
        list_of_shape_files_joined = []
        for list_string in list_of_focused_shape_files:
            list_of_shape_files_joined.append(",".join(list_string))
        return list_of_shape_files_joined

    @staticmethod
    def _list_of_focused_shapefiles(list_of_shape_files: list) -> list:
        list_of_shape_files_focused = []
        for filename in list_of_shape_files:
            folder_file = os.path.split(filename)[-1:]
            list_of_shape_files_focused.append(folder_file)
        return list_of_shape_files_focused