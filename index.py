#!/usr/local/bin/python3

from pathlib import Path
from html.parser import HTMLParser

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

        with self.path.open(mode='r', encoding='utf-8') as f:
            for line in f:
                self.feed(line)
            self.close() # dump the html rawdata out of the super class
    
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

def link(string,path):
    return str(f"[{string}]({path})")


if __name__ == "__main__":
    import os

    STY=Path("./style/github-pandoc.css").as_posix()
    TARGET=Path("./index.md")
    HTML=Path("./index.html")
    COLABS=Path("./colabs")

    TITLE="Computational Musicology 8824"
    DESCRIPTION="Jupyter notebooks made for the Computational Musicology Seminar at The Ohio State University's School of Music."
    li = "1. "

    PDOC="/usr/local/bin/pandoc"
    PFLAGS=f"-s --metadata title=\"{TITLE}\" -f markdown -t html5 -c {STY}"
    

    pdc=f"{PDOC} {PFLAGS} -i {TARGET.as_posix()} -o {HTML.as_posix()}"
    
    print("Loading Files...")
    files = [ Parser(f) for f in sorted(COLABS.rglob("*.html")) ]
    
    print("Making index...")
    with TARGET.open(mode='w') as f:
        f.writelines([
            f"{DESCRIPTION}\n\n",
            f"See the [Syllabus](Computational_Musicology_8824.02.pdf)\n\n"
        ])
        unit = ''
        for i in files:
            if unit != i.data["unit"] :
                f.write(li + link(i.data["unit"],i.data["path"]) + "\n")
                unit = i.data["unit"]
            f.write("\t" + li + link(i.data["name"],i.data["path"]) + "\n")
            for t in i.data['tree']:
                for k in t.keys():
                    depth = (k + 1)
                    if depth <= 6:
                        level = "\t" * depth
                        f.write(level+li+link(t[k][0],i.data["path"]+"#"+t[k][1])+"\n")
    print("Running Pandoc...")
    print(pdc)
    os.system(pdc)
    print("Done.")