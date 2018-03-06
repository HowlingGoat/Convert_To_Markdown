import argparse
import gzip
import hashlib
import itertools

from glob import glob
from os import chdir
from os import getcwd
from os import makedirs
from os import path

import markdown

from styles import get_string


class Build_HTML():
    """
    Main class to build the file / folder tree. Currently creates files then folders. Both are in alphabetical order.
    """

    def __init__(self, filepaths):
        self.previous_filelist = []
        self.html = ""
        self.tree = {}
        self.i = 0
        self.position = 1
        self.started = 0
        self.closed = 0
        self.filepaths = filepaths
        self.build_html_front_page()

    def build_html_front_page(self):
        for filepath in self.filepaths:
            filelist = filepath.split(path.sep)
            self.i = 0
            # Add folder or file
            for entry in filelist:
                if entry[-3:] == ".md":
                    self.add_file(entry, filepath)
                else:
                    self.add_folder(entry)
                self.i += 1

            self.close_expansion(filelist)
            self.position += 1

    def close_expansion(self, filelist):
        """
        Makes sure that you have the correct amount of </ul>.
        :param filelist:
        :return:
        """
        filelist.pop(-1)
        try:
            next_path = self.filepaths[self.position].split(path.sep)[:-1]
        except IndexError:
            next_path = ""
        if next_path != filelist and self.started > self.closed:
            self.append_ul_breaks(filelist)
            self.previous_filelist = filelist
            self.closed += 1

    def add_file(self, entry, filepath):
        """
        Add files entry types.
        :param entry:
        :param filepath:
        :return:
        """
        try:
            if entry not in self.tree[self.i]['file']:
                self.tree[self.i]['file'].append(entry)
                self.wrap_list_html(entry, filepath)
        except KeyError:
            self.tree[self.i] = {'file': [], 'folder': [],}
            self.tree[self.i]['file'].append(entry)
            self.wrap_list_html(entry, filepath)

    def add_folder(self, entry):
        """
        Add folder entry types.
        :param entry:
        :return:
        """
        try:
            if entry not in self.tree[self.i]['folder']:
                self.tree[self.i]['folder'].append(entry)
                self.wrap_list_html(entry)
                self.html += self.add_tab() + "<ul>\n"
                self.started += 1
        except KeyError:
            self.tree[self.i] = {'file': [], 'folder': [], }
            self.tree[self.i]['folder'].append(entry)
            self.wrap_list_html(entry)
            self.html += self.add_tab() + "<ul>\n"
            self.started += 1

    def append_ul_breaks(self, filelist):
        """
        Figure out if a </ul> need to be added.
        :param filelist:
        :return:
        """
        increment = 2
        for f, p in itertools.zip_longest(filelist, self.previous_filelist):
            if f != p:
                self.html += self.add_tab(increment) + "</ul>\n"
                increment += 1

    def wrap_list_html(self, entry, filepath=None):
        """
        Main entry to add the correct html for a file or a folder.
        :param entry:
        :param filepath:
        :return:
        """
        if filepath is not None:
            md5 = filename_md5(filepath)
            self.html += self.add_tab() + '<li><a href="html/%s.html" target="_blank">%s</a></li>\n' % (md5, entry)
        else:
            self.html += self.add_tab() + '<li>%s</li>\n' % entry

    def add_tab(self, increment=0):
        """
        Add the correct amount of tabs to have proper line indents.
        :param increment:
        :return:
        """
        return (self.i - increment) * "\t"


def read_mkd(filepath):
    """
    Read the markdown files.
    :param filepath:
    :return:
    """
    with open(filepath, 'r') as f:
        markdown_data = f.read()
    return markdown_data


def convert_mkd(markdown_data):
    """
    Convert markdown files to html
    :param markdown_data:
    :return:
    """
    html = markdown.markdown(markdown_data, ['markdown.extensions.extra', 'markdown.extensions.toc',
                                             'codehilite', 'pymdownx.tasklist', 'pymdownx.progressbar',])
    return html


def setup_html(html):
    """
    Helper function to define the header / footer of the index.html file.
    :param html:
    :return:
    """
    block_html = """<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
<link rel="stylesheet" type="text/css" href="styles.css">
</head>
<body>
%s
</head>
<body>""" % html
    return block_html


def write_html(html, filepath, buildpath):
    """
    Write the html file to an md5 named file.
    :param html:
    :param filepath:
    :return:
    """
    md5_filename = filename_md5(filepath)
    final_name = path.join(buildpath, "html", md5_filename + ".html")
    with open(final_name, "w") as f:
        f.write(html)


def file_rename(filename):
    """
    Strip file and '.md' extension from filename to more easily rebuild.
    :param filename: str(), filename.
    :return: str(), filename, no extension.
    """
    stripped_filename = filename.split(path.sep)[-1].replace('.md', '')
    return stripped_filename


def get_markdown_files():
    """
    Parse and get all files that end in '.md' in the current path.
    :return:
    """
    # TODO: Make it so you can specify the starting location.
    filenames = glob("**/*.md", recursive=True)
    return filenames


def filename_md5(markdown_data):
    """
    Convert the filepath to an md5 hash.
    :param markdown_data:
    :return:
    """
    hash = hashlib.new('md5', markdown_data.encode('utf-8'))
    return hash.hexdigest()


def write_index(html, buildpath):
    """
    Write the index.html file to the main folder.
    :param html:
    :return:
    """
    # TODO: make sure the file is written to the correct folder.
    with open(path.join(buildpath, 'index.html'), 'w') as f:
        f.write(html)


def decompress_styles(buildpath):
    """
    Decompress the stylesheet.
    :return:
    """
    data = get_string()

    with open(path.join(buildpath, 'html', 'styles.css'), "w") as f:
        f.write(data.decode('utf-8'))


def init_folder(buildpath):
    """
    Helper functions to make certain supporting folders and files are present.
    :return:
    """
    try:
        makedirs(path.join(buildpath, "html"))
    except OSError:
        pass
    decompress_styles(buildpath)


def init_argparse():
    parser = argparse.ArgumentParser(description='Convert Markdown files to HTML.')
    parser.add_argument(
        "-t", '--target',
        help="Starting point to look for markdown files.",
        # nargs="?",
        # nargs=1,
        default="",  # Should be current folder. Also might need to be
        metavar="PATH",
    )
    parser.add_argument(
        '-b', '--build',
        help="Location were index.html and the html folder will be dropped.",
        # nargs=1,
        metavar="PATH",
        default="",
    )

    # TODO: Might need some basic path checking?
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = init_argparse()
    current_path = getcwd()

    chdir(args.target)
    filepaths = get_markdown_files()
    build_html = Build_HTML(filepaths)
    index_html = setup_html(build_html.html)

    html_memory = {}
    for filepath in filepaths:
        filename = file_rename(filepath)
        markdown_data = read_mkd(filepath)
        html = convert_mkd(markdown_data)
        block_html = setup_html(html)
        html_memory[filepath] = block_html


    # Write operations need to be done after folder change.
    chdir(current_path)
    init_folder(args.build)
    write_index(index_html, args.build)
    for filepath, block_html in html_memory.items():
        write_html(block_html, filepath, args.build)

