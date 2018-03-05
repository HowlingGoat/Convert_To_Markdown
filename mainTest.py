import unittest

import main


class Test(unittest.TestCase):

    def test_file_rename(self):
        n = 'Test\\main.md'
        n2 = 'main.md'
        renamed = main.file_rename(n)
        renamed2 = main.file_rename(n2)
        self.assertEqual(renamed, "main")
        self.assertEqual(renamed2, "main")

    def test_md5sum(self):
        filename = "main"
        md5_hash = main.filename_md5(filename)
        self.assertEqual(md5_hash, 'fad58de7366495db4650cfefac2fcd61')

    def test_build_html_front_page(self):
        # TODO: Is this the best way to test this?
        paths = ["folder\\a.md", "folder\\second_row.md", "rotten.md"]
        build_instance = main.Build_HTML(paths)
        html = build_instance.html
        sample_html = """<li>folder</li>
<ul>
\t<li><a href="html/b12200e922dd221602d30cea8e763f7e.html" target="_blank">a.md</a></li>
\t<li><a href="html/8643a3ba5e7ae2fb5e58f06e9a266e52.html" target="_blank"second_row.md</a></li>
</ul>
<li><a href="html/3ba11e03dc599bc657a8f395cb10ad88.html" target="_blank">rotten.md</a></li>
"""
        self.assertEqual(sample_html, html)


if __name__ == '__main__':
    unittest.main()