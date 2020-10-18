import os

list_types = {'numbered': 'enumerate', 'bullet': 'itemize'}


class __main:
    def __init__(self, Packages: list = None):
        self.packages = Packages if Packages else []

    def add_super(self, new_packages: list):
        for i in new_packages:
            self.packages.append(i) if i not in self.packages else None

    def transfer_packages(self):
        return self.packages

    def generate_Tex(self):
        pass


class _section:
    def __init__(self, title: str, _type: int = 0):
        self.title = title
        self.items = []
        self.packages = []
        self.type = _type

    def generate_TeX(self):
        return f'\\{"sub" * self.type}section{{{self.title}}}\n'


class Document:
    def __init__(self, title: str = None, subtitle: str = None, author: str = None, top: int = None, bottom: int = None, left: int = None, right: int = None):
        self.title = title
        self.subtitle = subtitle
        self.author = author
        self.top = f'{top}mm' if top else None
        self.bottom = f'{bottom}mm' if bottom else None
        self.left = f'{left}mm' if left else None
        self.right = f'{right}mm' if right else None
        self.contains = []
        self.__preamble = [('fontenc', 'T1'), ('inputenc', 'utf8'), 'lmodern', 'textcomp', 'geometry']

    def generate_TeX(self, _compile: bool = True, **kwargs):
        if self.contains is []:
            print("Nothing to generate in the file!")
        out = '\\documentclass{article}\n'

        for i in self.contains:
            for n in i.packages:
                self.__preamble.append(n) if n not in self.__preamble else None

        for i in self.__preamble:
            out += self.__add_package(i)

        print(self.__preamble)

        if 'pgfplots' in self.__preamble:
            out += '\\pgfplotsset{compat=newest}\n'

        out += '\\geometry{'
        out += f'\ntop={self.top},' if self.top else ''
        out += f'\nbottom={self.bottom},' if self.bottom else ''
        out += f'\nleft={self.left},' if self.left else ''
        out += f'\nright={self.right},' if self.right else ''
        out += '}\n'

        out += '\n'
        temp = None
        if self.title:
            temp = self.title
            temp += f'\\\\\\large {self.subtitle}' if self.subtitle else None
        out += f'\n\\title{{{temp}}}\n\\date{{}}' if temp else ''
        out += f'\n\\author{{{self.author}}}' if self.author else ''
        out += f'\n\n\\begin{{document}}\n'
        out += '\\maketitle\n' if self.title else ''

        for i in self.contains:
            out += i.generate_TeX()

        out += '\\end{document}'

        temp = self.title
        for i in ["$", "%", "/", "\\"]:
            temp = temp.replace(i, "")
        temp = temp.replace('.', '_')

        katex = open(f'{temp}.tex', "w+")
        katex.truncate()
        katex = katex.write(out)

        if _compile:
            command = f'pdflatex -jobname=\"{temp}\" \"{temp}.tex\"'
            silent = True
            if 'debug' in kwargs:
                if kwargs['debug'] is True:
                    silent = False
            command += ' >/dev/null' if silent else ''

            os.system(command)
            temp = temp.replace(" ", "\ ")
            os.system(f'open ./{temp}.pdf')

    def add(self, item):
        self.contains.append(item)

    def new_section(self, title: str, _type: int = 0):
        _type = _type % 3
        self.contains.append(_section(title, _type))

    def __add_package(self, package: str or tuple):
        out = '\\usepackage'
        if type(package) is tuple:
            out += f'[{package[1]}]{{{package[0]}}}'
        else:
            out += f'{{{package}}}'
        return out + '\n'


class Text(__main):
    def __init__(self, *args, align: str = None):
        self.text = ''
        for arg in args:
            given = (str(arg).replace('->', '$\\rightarrow$')).replace('\n', '\\\\')
            self.text += f'{given} '
        self.align = align
        super().__init__(['ragged2e']) if self.align is not None else super().__init__()

    def generate_TeX(self):
        out = ''
        if self.align:
            out += f'\\begin{{flush{self.align}}}\n'
            out += f'{self.text}\n'
            out += f'\\end{{flush{self.align}}}\n'
        else:
            out += f'{self.text}\n'
        return out

    def __repr__(self):
        return f'Text > [\"{self.text}\", align > {self.align} ]'


class Equation(__main):
    def __init__(self, equation: str = '', numbered: bool = True):
        super().__init__(['amsmath']) if '\\text' in equation else super().__init__()
        self.equation = equation
        self.numbered = '' if numbered else '*'

    def generate_TeX(self):
        out = f'\\begin{{equation{self.numbered}}}\n'
        out += self.equation + '\n'
        out += f'\\end{{equation{self.numbered}}}\n'

        return out


class List(__main):
    def __init__(self, list_type: str = 'numbered', items: list = []):
        super().__init__()
        self.list_type = list_types.get(list_type)
        self.items = items
        self.__clear_list() if items is not [] else None

    def __clear_list(self):
        self.items = []

    def add(self, item):
        self.items.append(item)
        self.add_super(item.packages)

    def generate_TeX(self):
        out = f'\\begin{{{self.list_type}}}\n'
        for item in self.items:
            out += '\\item '
            if type(item) is list:
                out += Text(str(item))
            else:
                out += f'{item.generate_TeX()}\n'
        out += f'\\end{{{self.list_type}}}\n'
        return out

    def __repr__(self):
        out = 'List > [\n'
        for i in self.items:
            out += f'{i}\n'
        out += ']'
        return out


class group(__main):
    def __init__(self, items: list = []):
        super().__init__()
        self.items = items

    def add(self, item):
        self.items.append(item)
        self.add_super(item.packages)

    def generate_TeX(self):
        out = ''
        for i in self.items:
            out += i.generate_TeX()
        return out


class line(__main):
    def __init__(self, coordinates: list, color: str = None, mark: str = None, style: str = None, label_offset: int or float = -0.2):
        super().__init__()
        self.label_offset = label_offset
        self.coordinates = coordinates
        self.color = color
        self.mark = mark
        self.style = style

    def generate_TeX(self):
        out = '\\addplot['
        out += f'\ncolor={self.color}, ' if self.color else ''
        out += f'\nmark={self.mark}, ' if self.mark else ''
        out += f'\nstyle={self.style}, ' if self.style else ''
        out += ']\ncoordinates {'
        for i in self.coordinates:
            out += f'{i} '

        out = self.out[:-1]

        Axis = (self.coordinates[0][0], 'x') if self.coordinates[0][0] == self.coordinates[1][0] else (self.coordinates[0][1], 'y')

        out += f'}};\n\\node at (axis cs:'
        out += f'{Axis[0]}, {self.label_offset})' if Axis[1] == 'x' else f'{self.label_offset}, {Axis[0]})'
        out += f'{{{Axis[1]}={Axis[0]}}};\n'

        return out


class plot(__main):
    def __init__(self, function: str, domain: tuple = None, color=None, name: str = None):
        super().__init__()
        self.function = function
        self.name = name
        self.color = color
        self.domain = domain

        self.generate_TeX()

    def generate_TeX(self):
        out = f'\\addplot['
        out += f'domain={self.domain[0]}:{self.domain[1]}, ' if self.domain else ''
        out += f'color={self.color}, ' if self.color else ''
        out += f']\n{{{self.function}}};\n'
        out += f'\\addlegendentry{{{self.name}}}\n' if self.name else ''

        return out


class coordinates(__main):
    def __init__(self, coords: list, color: list = None, name: str = None):
        super().__init__()
        self.coords = coords
        self.name = name
        self.color = color
        self.color = f'{{rgb:red,{color[0]};green,{color[1]};blue,{color[2]}}}' if self.color is not None else None

        self.generate_TeX()

    def generate_TeX(self):
        out = f'\\addplot['
        out += f'color={self.color}' if self.color else ''
        out += ']\ncoordinates {'
        for i in self.coords:
            out += f'{i}\n'
        out += '};\n'
        out += f'\\addlegendentry{{{self.name}}}\n' if self.name else ''

        return out


class axis(__main):
    def __init__(self, title: str = None, samples: int = 100, labels: list = [None] * 2, showTickMarks: bool = True, clip: bool = False, **kwargs):
        super().__init__(['tikz', 'pgfplots'])
        self.title = title
        self.width = f'{kwargs["width"]}cm' if 'width' in kwargs else None
        self.height = f'{kwargs["height"]}cm' if 'height' in kwargs else None
        self.ymax = kwargs['ymax'] if 'ymax' in kwargs else None
        self.ymin = kwargs['ymin'] if 'ymin' in kwargs else None
        self.xmax = kwargs['xmax'] if 'xmax' in kwargs else None
        self.xmin = kwargs['xmin'] if 'xmin' in kwargs else None
        self.ylab = labels[1]
        self.xlab = labels[0]
        self.samples = samples
        self.showTickMarks = showTickMarks
        self.clip = clip
        self.plots = []

    def generate_TeX(self):
        out = '\\begin{center}\n\\begin{tikzpicture}\n\\begin{axis}[\naxis lines=left,'
        out += f'\nclip={str(self.clip).lower()},'
        out += f'\nsamples={self.samples},' if self.samples else ''
        out += f'\nxlabel={self.xlab},' if self.xlab else ''
        out += f'\nylabel={self.ylab},' if self.ylab else ''
        out += f'\nxmin={self.xmin},' if self.xmin is not None else ''
        out += f'\nxmax={self.xmax},' if self.xmax is not None else ''
        out += f'\nymin={self.ymin},' if self.ymin is not None else ''
        out += f'\nymax={self.ymax},' if self.ymax is not None else ''
        out += '\nticks=none,' if not self.showTickMarks else ''
        out += f'\nwidth={self.width},' if self.width else ''
        out += f'\nheight={self.height},' if self.height else ''
        out += f'\ntitle={self.title}' if self.title else ''
        out += ']\n'

        # axis lines=middle tag inside the [] section option #

        for i in self.plots:
            out += i.generate_TeX()

        out += '\\end{axis}\n\\end{tikzpicture}\n\\end{center}\n'

        return out

    def add_plot(self, new_plot: plot or line):
        self.plots.append(new_plot)

    def __repr__(self):
        return f'x-label: {self.xlab}\ny-label: {self.ylab}\nPlot(s):\n{self.plots}'


class Code(__main):
    def __init__(self, code: str, language: str = None):
        super().__init__(['listings'])
        self.code = code
        self.language = language

    def generate_Tex(self):
        out = f'\\lstset{{language={self.language}}}\n\\begin{{lstlisting}}\n'
        out += self.code
        out += '\\end{lstlisting}\n'

# To add:
# > show_contents bool for Document class
#    - \tableofcontents{} inside \begin{document} after \maketitle
