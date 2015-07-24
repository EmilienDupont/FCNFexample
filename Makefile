all:
	./SimpleServer.py

test:
	./FCNF.py

clean:
	-rm gurobi.log *.pyc *.lp
