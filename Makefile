TEXDOC	:= main

.PHONY: tex
tex:
	cd tex && \
		pdflatex $(TEXDOC) && \
		python $(TEXDOC).sympy && \
		bibtex $(TEXDOC) && \
		pdflatex $(TEXDOC) && \
		pdflatex $(TEXDOC)

.PHONY: word
word:
	cd tex && \
		pandoc -s $(TEXDOC).tex --bibliography=assets/references.bib -o article_2022.docx

.PHONY: html
html:
	cd rst && \
		sphinx-build -b html -d _build/doctrees . ../docs

.PHONY: venv
venv:
	echo 'layout python3' > .envrc && \
		direnv allow

.PHONY: reqs
reqs:
	pip install -U pip
	pip install -r requirements.txt

.PHONY: changes
changes:
		git log --oneline --pretty=format:"* %ad: %s" --date=short > CHANGES
