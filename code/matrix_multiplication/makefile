INPUTS1 := $(wildcard data/matrix_input/*_1.txt)

all:
	g++ matrix_multiplication.cpp algorithms/naive.cpp algorithms/strassen.cpp -o MMult

clean:
	rm -f MMult

run_all: all
	@for input1 in $(INPUTS1); do \
		input2="$${input1%_1.txt}_2.txt"; \
		echo "ejecutando $$input1 y $$input2..."; \
		./MMult "$$input1" "$$input2"; \
	done
	echo "Todos archivos ejecutados"