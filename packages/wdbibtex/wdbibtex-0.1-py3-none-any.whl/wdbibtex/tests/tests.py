import itertools
import glob
import os
import shutil
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import wdbibtex  # noqa E402


class TestLaTeX(unittest.TestCase):
    """Test cases for LaTeX compile and result extraction.
    """

    def test_write(self):
        """Pass if LaTeX class could correctly write .tex file.
        """
        cwd = os.getcwd()
        exampledir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'examples'
        )
        os.chdir(os.path.join(exampledir, 'example1'))

        # Copy LaTeX bib and bst files to workdir
        os.makedirs('.tmp', exist_ok=True)
        for b in glob.glob('*.bib'):
            shutil.copy(b, '.tmp')

        ltx = wdbibtex.LaTeX()
        ltx.write('Test contents\n', bst='ieeetr')

        # File check
        correct = [
            '\\documentclass[latex]{article}\n',
            '\\usepackage{cite}\n',
            '\\bibliographystyle{ieeetr}\n',
            '\\begin{document}\n',
            'Test contents\n',
            '\\bibliography{library}\n',
            '\\end{document}\n',
        ]
        with open('.tmp/wdbib.tex', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents):
            self.assertEqual(c1, c2)

        # Clear working directory
        shutil.rmtree('.tmp/')
        os.chdir(cwd)

    def test_build(self):
        """Pass if LaTeX class could build project.
        """
        cwd = os.getcwd()
        exampledir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'examples'
        )
        os.chdir(os.path.join(exampledir, 'example1'))

        # Copy LaTeX bib and bst files to workdir
        os.makedirs('.tmp', exist_ok=True)
        for b in glob.glob('*.bib'):
            shutil.copy(b, '.tmp/')

        ltx = wdbibtex.LaTeX()
        ltx.write('Test contents\n', bst='ieeetr')
        ltx.build()

        # File check
        correct = [
            '\\relax \n',
            '\\bibstyle{ieeetr}\n',
            '\\bibdata{library}\n',
            '\\gdef \\@abspage@last{1}\n',
        ]
        with open('.tmp/wdbib.aux', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents):
            self.assertEqual(c1, c2)

        # Clear working directory
        shutil.rmtree('.tmp')
        os.chdir(cwd)

    def test_compile_citation(self):
        """Pass if LaTeX could build .tex with citation.
        """
        cwd = os.getcwd()
        exampledir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'examples'
        )
        os.chdir(os.path.join(exampledir, 'example1'))

        # Copy LaTeX bib and bst files to workdir
        os.makedirs('.tmp', exist_ok=True)
        for b in glob.glob('*.bib'):
            shutil.copy(b, '.tmp/')

        ltx = wdbibtex.LaTeX()
        ltx.write(
            'Test contents with one citation \\cite{enArticle1}.\n',
            bst='ieeetr')
        ltx.build()

        # File check
        correct = [
            '\\documentclass[latex]{article}\n',
            '\\usepackage{cite}\n',
            '\\bibliographystyle{ieeetr}\n',
            '\\begin{document}\n',
            'Test contents with one citation \\cite{enArticle1}.\n',
            '\\bibliography{library}\n',
            '\\end{document}\n',
        ]
        with open('.tmp/wdbib.tex', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents):
            self.assertEqual(c1, c2)

        # File check
        correct = [
            '\\relax \n',
            '\\bibstyle{ieeetr}\n',
            '\\citation{enArticle1}\n',
            '\\bibdata{library}\n',
            '\\bibcite{enArticle1}{1}\n',
            '\\gdef \\@abspage@last{1}\n',
        ]
        with open('.tmp/wdbib.aux', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents):
            self.assertEqual(c1, c2)

        # File check
        correct = [
            '\\begin{thebibliography}{1}\n',
            '\n',
            '\\bibitem{enArticle1}\n',
            "I.~Yamada, J.~Yamada, S.~Yamada, and S.~Yamada, ``Title1,'' {\\em Japanese\n",
            '  Journal}, vol.~15, pp.~20--30, march 2019.\n',
            '\n',
            '\\end{thebibliography}\n',
        ]
        with open('.tmp/wdbib.bbl', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents):
            self.assertEqual(c1, c2)

        # Parse test for aux file.
        ltx.read_aux()
        self.assertEqual(
            ltx.cnd['\\\\cite\\{enArticle1\\}'],
            '[1]'
        )
        self.assertEqual(
            ltx.tbt,
            u"[1]\tI. Yamada, J. Yamada, S. Yamada, and S. Yamada, "
            u"“Title1,” Japanese Journal, vol. 15, pp. 20\u201430, "
            u"march 2019.\n"
        )
        # Clear working directory
        shutil.rmtree('.tmp')
        os.chdir(cwd)

    def test_multiple_citations_compile_citation(self):
        """Pass if multiple citations are collectly converted.
        """
        cwd = os.getcwd()
        exampledir = os.path.join(
            os.path.dirname(__file__), '..', '..', 'examples'
        )
        os.chdir(os.path.join(exampledir, 'example2'))

        # Copy LaTeX bib and bst files to workdir
        os.makedirs('.tmp', exist_ok=True)
        for b in glob.glob('*.bib'):
            shutil.copy(b, '.tmp/')

        ltx = wdbibtex.LaTeX()
        ltx.write(
            ('Test contents with one citation \\cite{enArticle1}.\n'
             'Another citation \\cite{enArticle2}.\n'
             'Multiple citations in one citecommand '
             '\\cite{enArticle1,enArticle3}\n'),
            bst='ieeetr')
        ltx.build()

        # File check
        correct = [
            '\\documentclass[latex]{article}\n',
            '\\usepackage{cite}\n',
            '\\bibliographystyle{ieeetr}\n',
            '\\begin{document}\n',
            'Test contents with one citation \\cite{enArticle1}.\n',
            'Another citation \\cite{enArticle2}.\n',
            'Multiple citations in one citecommand \\cite{enArticle1,enArticle3}\n',
            '\\bibliography{library}\n',
            '\\end{document}\n',
        ]
        with open('.tmp/wdbib.tex', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents):
            self.assertEqual(c1, c2)

        # File check
        correct = [
            '\\relax \n',
            '\\bibstyle{ieeetr}\n',
            '\\citation{enArticle1}\n',
            '\\citation{enArticle2}\n',
            '\\citation{enArticle1,enArticle3}\n',
            '\\bibdata{library}\n',
            '\\bibcite{enArticle1}{1}\n',
            '\\bibcite{enArticle2}{2}\n',
            '\\bibcite{enArticle3}{3}\n',
            '\\gdef \\@abspage@last{1}\n',
        ]
        with open('.tmp/wdbib.aux', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents):
            self.assertEqual(c1, c2)

        # File check
        correct = [
            "\\begin{thebibliography}{1}\n",
            "\n",
            "\\bibitem{enArticle1}\n",
            "I.~Yamada, J.~Yamada, S.~Yamada, and S.~Yamada, ``Title1,'' {\em Japanese\n",
            "  Journal}, vol.~15, pp.~20--30, march 2019.\n",
            "\n",
            "\\bibitem{enArticle2}\n",
            "G.~Yamada and R.~Yamada, ``Title2,'' {\\em Japanese Journal}, vol.~15, p.~21,\n",
            "  dec. 2019.\n",
            "\n",
            "\\bibitem{enArticle3}\n",
            "G.~Yamada and R.~Yamada, ``Title2 is true?,'' {\\em IEEE Transactions on Pattern\n",
            "  Analysis and Machine Intelligence}, nov 2018.\n",
            "\n",
            "\\end{thebibliography}\n",
        ]
        with open('.tmp/wdbib.bbl', 'r') as f:
            contents = f.readlines()

        for c1, c2 in itertools.zip_longest(correct, contents):
            self.assertEqual(c1, c2)

        # Parse test for aux file.
        ltx.read_aux()
        self.assertEqual(
            ltx.cnd['\\\\cite\\{enArticle1\\}'],
            '[1]'
        )
        self.assertEqual(
            ltx.cnd['\\\\cite\\{enArticle2\\}'],
            '[2]'
        )
        self.assertEqual(
            ltx.cnd['\\\\cite\\{enArticle1,enArticle3\\}'],
            '[1,3]'
        )
        self.assertEqual(
            ltx.tbt,
            (u"[1]\tI. Yamada, J. Yamada, S. Yamada, and S. Yamada, “Title1,” "
             u"Japanese Journal, vol. 15, pp. 20—30, march 2019.\n"
             u"[2]\tG. Yamada and R. Yamada, “Title2,” Japanese Journal, "
             u"vol. 15, p. 21, dec. 2019.\n"
             u"[3]\tG. Yamada and R. Yamada, “Title2 is true?,” IEEE Transactions "
             u"on Pattern Analysis and Machine Intelligence, nov 2018.\n")
        )
        # Clear working directory
        shutil.rmtree('.tmp')
        os.chdir(cwd)
