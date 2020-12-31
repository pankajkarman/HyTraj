fig = ./figures/
bib = ./ref.bib
csl = ./template/nature.csl
filters = ./filters
template = ./template/paper.tex
ref = /home/pankaj/Documents/Mendeley/airmass.bib

lua = --lua-filter=$(filters)/pagebreak.lua \
      --lua-filter=$(filters)/scholarly-metadata.lua \
      --lua-filter=$(filters)/author-info-blocks.lua
      
arg = -F pandoc-crossref -F pandoc-citeproc
com = pandoc main.md $(arg) --csl $(csl) --bibliography $(bib) 

all:	bib pdf docx

bib:    $(ref)
	cp $(ref) $(bib)

pdf:	main.md $(bib)
	$(com) -s --template=$(template) --pdf-engine=xelatex -o main.pdf

docx:	main.md $(bib)
	$(com) $(lua) -o main.docx

clean:	
	rm -rf *.pdf *.docx
