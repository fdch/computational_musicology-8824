#!/usr/local/bin/python3

from pathlib import Path
from html.parser import HTMLParser
from os import system
import pickle

class Parser(HTMLParser):

    def __init__(self, path):
        
        super().__init__()
        self.data = {
            "path"  : '',
            "name"  : '',
            "unit"  : '',
            "tree" : []
        }

        self.path = Path(path)
        self.data["path"] = self.path.as_posix()
        print(self.data['path'])
        self.data["unit"] = self.header(self.data['path'].split('/')[-2])
        self.data["name"] = self.header(self.path.stem)
        # read the file and feed the super class
        # this will call the handle_starttag for us
        # so we only need to update our own data and dump the super() data
        with self.path.open(mode='r', encoding='utf-8') as f:
            for line in f:
                self.feed(line)
            # dump the html rawdata out of the super class
            self.close() 

    def __call__(self):
        return self.data

    def header(self, string):
        return string.replace("-"," ").replace("_"," ").title()

    def handle_starttag(self, tag, attrs):
        if "h" in tag:
            for i in attrs:
                self.data["tree"].append({
                    int(tag[-1]): [
                        self.header(i[-1]),
                        i[-1]
                    ]
                })
## end parser class

def mdl(path,string=None, colab=False):
    if string is None:
        string = path
    if colab:
        name = Path(path).stem
        path2 = "/".join(path.split("/")[:-1]) + "/" + name + ".ipynb"
        return f"{string} [html]({path}) | [*colab*]({path2})"
    else:
        return f"[{string}]({path})"

def parse(path, file=None, ext="*.html"):
    path=Path(path)
    print(f"Loading Files from {path} ...")
    parsed = [ Parser(f) for f in sorted(path.rglob(ext)) ]
    if file is not None:
        print("Saving pickle to " + file)
        with Path(file).open(mode="wb") as f:
            pickle.dump(parsed, f)
    return parsed

def make_index(parsed):

    print("Indexing ...")
    unit = ''
    ln = []
    for i in parsed:
        # update unit if it is different
        if unit != i.data["unit"] :
            ln.append(nl("\n"))
            ln.append(nl("---"))
            ln.append(nl(nl("## " +  i.data["unit"])))
            ln.append(nl("\n"))
            unit = i.data["unit"]
        # append the colab header here
        ln.append(nl("\n"))
        ln.append(nl("### "+mdl(i.data["path"],i.data["name"],colab=True)))
        ln.append(nl("\n"))
        indices=[]
        ul = []
        for t in i.data['tree']:
            sl = []
            for k in t.keys():
                indices.append(k)
                level = ''
                if k > 0:
                    level = "\t " * (k-1)
                hashlink = i.data["path"] + "#" + t[k][1]
                level += str(indices.count(k))+". "
                sl.append(level + mdl(hashlink,t[k][0]))
            ul.append(nl(sl))
            # print(ul)
        ln.append(nl(ul))
        ln.append(nl("\n"))

    return ln

def pandoc(source, target, style, pandoc="/usr/local/bin/pandoc"):
    style  = Path(style).as_posix()
    source = Path(source).as_posix()
    target = Path(target).as_posix()
    PFLAGS=f"-s -f markdown -t html5 -c {style} --toc --toc-depth=6"
    pdc=f"{pandoc} {PFLAGS} -i {source} -o {target}"
    print(f"Running Pandoc with the following command: {pdc} ...")
    system(pdc)

def nl(x):
    """new line char helper
    
    Returns
    ----------
    (string) - If input is array, join the array with newline char, otherwise, force it into a string with an added a newline char
    """
    return "\n".join(x) if isinstance(x,list) else str(x) + "\n"

def parse_deps(a):
    imports = []
    keys=['from', 'as', 'import', '*']
    punct=[',', '.']
    if "as" in a:
        a = a[:a.index('as')]
    for k in keys:
        if k in a:
            a.remove(k)
    for i in a:
        for p in punct:
            if p in i:
                i.replace(p,'')
    return ".".join(a)

def check_dependencies(path, depfile):
    import json
    imports=[]
    for i in Path(path).rglob("*.ipynb"):
        with i.open(mode='r') as f:
            data = json.load(f)
        for cell in data['cells']:
            for s in cell['source']:
                if "import " in s and "#" not in s and "!" not in s and "`" not in s:
                    a = s.rstrip().split(" ")
                    imports.append(parse_deps(a))

    with Path(depfile).open(mode='w') as f:
        f.write(nl(sorted(list(set(sorted(imports))))))

if __name__ == "__main__":
    import argparse

    TOPIC       = "Computational Musicology"
    CODE        = "8824"
    SCHOOL      = "The Ohio State University\'s School of Music"
    MD          = "README.md"

    NAME        = f"{TOPIC.lower().replace(' ','_')}-{CODE}" 
    REPO        = f"https://github.com/fdch/{NAME}.git"
    URL         = f"https://fdch.github.io/{NAME}"
    TITLE       = f"{TOPIC} {CODE}"
    SYLLABUS    = Path(f"./syllabus/{TITLE.replace(' ','_')}.02.pdf")
    DEPFILE     = "requirements.txt"
    USAGE       = [
            "```sh",
            "git clone " +REPO,
            "cd " +NAME,
            "./config.py -depic",
            "# or simply",
            "jupyter notebook",
            "```",
    ]

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-c", "--convert", 
        help="Convert all notebooks to html before continuing (True)",
        action="store_false"
    )
    parser.add_argument("-i","--index", 
        help="Custom-made colab index from html files (True)",
        action="store_false"
    )
    parser.add_argument("-p","--pandoc", 
        help="Readme pandoc conversion (True)", 
        action="store_false",
    )
    parser.add_argument("-e","--edit", 
        help="Enable jupyter notebook editor (False)", 
        action="store_true"
    )
    parser.add_argument("-d","--dependencies", 
        help="Check dependencies on your colabs and output a txt file (True)", 
        action="store_false"
    )
    parser.add_argument("-s","--saveto", 
        help="Save your index to a pickle file (eg: -s .index)"
    )
    parser.add_argument("-l","--loadfrom", 
        help="Load your index from a pickle file (eg: -l .index)"
    )
    args = parser.parse_args()

    if args.edit:
        system("jupyter notebook")

    if args.dependencies:
        check_dependencies("colabs", DEPFILE)

    if args.convert is not False:
        system("jupyter nbconvert --to html colabs/*/*.ipynb")
    
    if args.index is not False:
        if args.loadfrom is not None:
            with Path(args.loadfrom).open(mode='rb') as f:
                parsed = pickle.load(f)
        else:
            parsed = parse("colabs", file=args.saveto)
        
        INDEXLINES = make_index(parsed)

        TEXTLINES   = [
            nl(f"---\ntitle: {nl(TITLE)}..."),
            nl("# Description"),
            nl(f"Notebooks made for the {TITLE} seminar at {SCHOOL}."),
            nl("See the syllabus here: "+mdl(SYLLABUS)),
            nl("The code for this website is hosted here: "+mdl(REPO)),
            nl("# Usage"),
            nl(f"You can browse the read-only notebooks (html version) nlfollowing) the links in this website ({mdl(URL)}), or you can download or clone the repository and run the notebooks:"),
            nl("NOTE: see "+mdl("requirements.txt")),
            nl(USAGE),
            nl("Alternatively, you can browse the notebooks online following its corresponding *colab* link"),
            nl("# Index"),
            nl(INDEXLINES),
            nl("# Authors"),
            nl(mdl("https://github.com/fdch", "Fede Camara Halac")),
            nl(mdl("https://github.com/shanahdt", "Daniel Shanahan"))
        ]
        with Path(MD).open(mode='w') as f:
            f.write(nl(TEXTLINES))

    if args.pandoc is not False:
        pandoc(MD, "index.html", "./style/github-pandoc.css")
    