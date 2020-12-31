fig = ./figures/
tab = ./tables/
bib = ./ref.bib
csl = ./template/nature.csl
filters = ./filters
template = ./template/paper.tex
ref = /home/pankaj/Documents/Mendeley/airmass.bib

main = ./main
tem = ./doc.md

lua = --lua-filter=$(filters)/pagebreak.lua \
      --lua-filter=$(filters)/scholarly-metadata.lua \
      --lua-filter=$(filters)/author-info-blocks.lua
      
arg = -F pandoc-crossref -F pandoc-citeproc
com1 = cat $(main).md > $(tem)
com2 = python $(filters)/pandoc-include.py --infile $(tem) --outfile $(tem)
com3 = pandoc $(tem) $(arg) --csl $(csl) --bibliography $(bib) 
com = $(com1); $(com2); $(com3)

all:	pdf docx

bib:    $(ref)
	cp $(ref) $(bib)

pdf:	$(main).md $(bib)
	$(com) -s --template=$(template) --pdf-engine=xelatex -o $(main).pdf
	rm -rf $(tem)

docx:	$(main).md $(bib)
	$(com) $(lua) -o $(main).docx
	rm -rf $(tem)

clean:	
	rm -rf *.pdf *.docx
