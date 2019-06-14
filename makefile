test: main.py display.py Graphics.py matrix.py lex.py mdl.py yacc.py script.py waluigiFinal.mdl racket.obj
	python3 main.py waluigiFinal.mdl

clean:
	rm *pyc *out parsetab.py

clear:
	rm *pyc *out parsetab.py *ppm