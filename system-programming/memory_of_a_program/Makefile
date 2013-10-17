all:
	gcc memory_proccess.c -g -o memory_proccess.out
	objdump -h -d memory_proccess.out > memory_proccess.dis

clean:
	rm -fr *.out *.dis *.o 2>/dev/null
