INPUTS := $(wildcard data/array_input/*)

all:
	g++ sorting.cpp algorithms/mergesort.cpp algorithms/quicksort.cpp algorithms/sort.cpp -o sorting

clean:
	rm -f sorting

run_all: all
	@for input in $(INPUTS); do \
		echo "ejecutando $$input..."; \
		./sorting "$$input"; \
	done
	@echo "Todos archivos ejecutados"