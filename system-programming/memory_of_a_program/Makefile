all:
	gcc memory_proccess.c -g -o memory_proccess.out
	objdump -h -d memory_proccess.out > memory_proccess.dis

clean:
	-rm memory_proccess.out memory_proccess.dis *.o 2>/dev/null
