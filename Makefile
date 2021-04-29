TITLE="Computational Musicology 8824"
IDX=index
STY=style/github-pandoc.css
PDOC=pandoc
PFLAGS=-s --metadata title=$(TITLE) -f markdown -t html5 -c $(STY)

all: $(IDX).md
	$(PDOC) $(PFLAGS) -i $(IDX).md -o $(IDX).html
