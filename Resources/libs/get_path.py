def build_kassettePath(initial_path):
    """ Takes initial Kassette path and return index.js path in order to start a process using Kasette
    """
    path_builder = initial_path.split("/")
    list_to_remove =['','c','mnt','kassette']
    [path_builder.remove(i) for i in list_to_remove]
    final_path='/' + '/'.join(path_builder) + '/node_modules/@amadeus-it-group/kassette/bin/index.js'
    return final_path


if __name__ == "__main__":
    build_kassettePath("/mnt/c/Users/amirhzer/AppData/Roaming/npm/kassette")
