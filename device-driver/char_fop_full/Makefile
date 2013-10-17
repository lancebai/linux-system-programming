MODULE = char_fop
obj-m := $(MODULE).o
PWD := $(shell pwd)
ccflags += -gdb
all:
	$(MAKE) -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
	objdump -h -d -S $(MODULE).ko > $(MODULE).dis
clean:
	rm -rf *.o *~ core .depend .*.cmd *.ko *.mod.c .tmp_versions Module.symvers *.dis *.order

