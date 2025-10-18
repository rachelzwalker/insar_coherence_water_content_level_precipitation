from src.ListOfFiles import get_list_of_files


class DirectorySearchTif:
    def __init__(self, root_directory: str, contain: str='corr', not_contain:str='xml',
                 folder_file_location_in_relation_to_forward_slash: int=-2, sentinel_focus:None|str=None):
        self.root_directory = root_directory
        self.contain = contain
        self.not_contain = not_contain
        self.location = folder_file_location_in_relation_to_forward_slash
        self.sentinel_focus = sentinel_focus

    def get_tifs(self) -> list:
        list_of_files = get_list_of_files(self.root_directory)
        reduced_list_of_files = self._check_contain(list_of_files)
        focused_list = self._check_not_contain(reduced_list_of_files)

        if self.sentinel_focus == 'B':
            focused_list = self._check_contain(focused_list, 'S1BB')
        if self.sentinel_focus == 'A':
            focused_list = self._check_not_contain(focused_list, 'S1BB')
        return focused_list

    @staticmethod
    def _get_joined_files_list(folder_file_name: list) -> list:
        joined_files = []
        for list_string in folder_file_name:
            joined_files.append("/".join(list_string))
        return joined_files

    def _get_folder_file_names(self, focused_list:list)->list:
        folder_file_names = []
        for filename in focused_list:
            folder_file = filename.split('/')[self.location:]
            folder_file_names.append(folder_file)
        return folder_file_names

    def _check_not_contain(self, reduced_list_of_files:list):
        return [x for x in reduced_list_of_files if not self.not_contain in x]

    def _check_contain(self, list_of_files: list) -> list:
        return [x for x in list_of_files if self.contain in x]
