#!/usr/bin/python
# -*- coding: UTF-8 -*-  
# Description: utility to caculate the mapped share library and offset of vaddr
# Author: lancebai@gmial.com

import re
import sys  
import argparse    
mem_map_dict = {}

class Mem_map_entry(object):
    def __init__ (self, library_name='', start_address=0, end_address=0):
        self.library_name = library_name
        self.start_address = start_address
        self.end_address = end_address

def analyse_memory_of_process(pid):
    # pid_map_filename = "/proc/%d/maps" % (pid,)
    # print pid_map_filename;
    try: 
        maps_file = open("/proc/%d/maps" % (pid,) ,'r')
        # mem_file = open("/proc/self/mem", 'r', 0)
        for line in maps_file.readlines():  # for each mapped region
            #b6fae000-b6faf000 rw-p 0001e000 b3:02 131187     /lib/arm-linux-gnueabihf/ld-2.13.so
            m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([rwxp-]+) ([0-9A-Fa-f]+) ([0-9A-Fa-f]+):([0-9A-Fa-f]+) ([0-9]+) (.*)' , line)

            if m.group(3)[0] == 'r':  # if this is a readable region
                start = int(m.group(1), 16)
                end = int(m.group(2), 16)
                library_name = m.group(8).strip()
                # mem_file.seek(start)  # seek to region start
                # chunk = mem_file.read(end - start)  # read region contents

                #ignore the program data mmap
                if library_name == "" :
                    continue

                if library_name in mem_map_dict :
                    # update end address
                    # print "updating ending address"
                    if end > mem_map_dict[library_name][1] :
                        mem_map_dict[library_name] = (mem_map_dict[library_name][0], end)
                        # print "after updateing %s %x %x" %(library_name, mem_map_dict[library_name][0], mem_map_dict[library_name][1],)

                else :
                    # print library_name, "is not in the list"
                    mem_map_dict[library_name] = (start, end)

                # print "%x - %x %s\n" % (start, end, library_name),  # dump contents to standard output

        #close maps files        
        maps_file.close()
        return True

        # print "===============\n", mem_map_dict
    except IOError:
        print "can not open file", "/proc/%d/maps" % (pid,)
        return False 
    # mem_file.close()



def parse_param():
    parser = argparse.ArgumentParser()
    parser.add_argument("pid", help="file containing nexus cflags",
                        type=int)
    parser.add_argument("vaddr", help="file containing nexus cflags",
                        type=str)
    args = parser.parse_args()
    return args


# return (library name, offset) on success, else None
def lookup_mapped_library(vaddr):
    for key in mem_map_dict:
        if mem_map_dict[key][0] <=  vaddr <=  mem_map_dict[key][1] :
            return (key, vaddr - mem_map_dict[key][0])
    return None        


def iterate_mmap():
    print "======================"
    for key in mem_map_dict:
        print "%x - %x, %s " %(mem_map_dict[key][0], mem_map_dict[key][1], key, )
    print "======================"    


def main():
    print "main function"
    pid = parse_param().pid
    vaddr = int(parse_param().vaddr, 16);

    print "the parsing pid is:", pid  
    print "the address:%x" %(vaddr, )

    if not analyse_memory_of_process(pid) :
        sys.exit(0)

    # iterate_mmap()
        
    ret = lookup_mapped_library(vaddr)
    if ret != None :
        print "%s, offset:%x" %( ret[0], ret[1], )
    else :
        print "%x is not a valid address" %(vaddr,)    

if __name__ == "__main__":
    main()
    sys.exit(0)    
