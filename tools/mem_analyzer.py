#!/usr/bin/python
# -*- coding: UTF-8 -*-  
# Description: utility to caculate the mapped share library and offset of vaddr
# Author: lancebai@gmial.com
#

import re
import sys, subprocess  
import argparse    
mem_map_dict = {}

class Mem_map_entry(object):
    def __init__ (self, library_name='', start_address=0, end_address=0):
        self.library_name = library_name
        self.start_address = start_address
        self.end_address = end_address


#TODO: instead of store different sections of library in on entry, store as text, ro data, rw data section, etc 
def analyse_memory_of_process(pid):
    # pid_map_filename = "/proc/%d/maps" % (pid,)
    # print pid_map_filename;
    try: 
        maps_file = open("/proc/%d/maps" % (pid,) ,'r')
        # mem_file = open("/proc/self/mem", 'r', 0)
        for line in maps_file.readlines():  # for each mapped region
            #b6fae000-b6faf000 rw-p 0001e000 b3:02 131187     /lib/arm-linux-gnueabihf/ld-2.13.so
            m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([rwxp-]+) ([0-9A-Fa-f]+) ([0-9A-Fa-f]+):([0-9A-Fa-f]+) ([0-9]+) (.*)' , line)

            if m and m.group(3)[0] == 'r':  # if this is a readable region
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

                print "%x - %x %s\n" % (start, end, library_name),  # dump contents to standard output

        #close maps files        
        maps_file.close()
        return True
        
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


#TODO: only parse symbol when it is in the text section
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

def get_symb_with_offset(library_name, offset):

    if(offset%4 != 0) :
        raise Exception("offset address not aligned!")

    objdumpPopen = subprocess.Popen(args='objdump -d %s'%(library_name) , shell=True , stdout=subprocess.PIPE)
    out=objdumpPopen.stdout.readlines()
    
    function_symbol = None

    for line in out:        
        # print line.rstrip()
        m = re.match(r'(^[0-9A-Fa-f]+) (<.*>:)' , line.rstrip())
        if m is not None:
            # print m.group(1), m.group(2)
            symbol = m.group(2)
            base_addr = int(m.group(1), 16)
            new_function_symbol = (symbol, base_addr)
            # print "%s, %x, offset:%x" %(symbol, base_addr, offset)

            if( offset < base_addr ) :
                # print  "%s %x %x" %(symbol, base_addr, offset)
                break
            else :
                # print "renew function symbol" 
                function_symbol = new_function_symbol
    # print "end of for loop"            
    return function_symbol        
                

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
        # try :
        func_sym = get_symb_with_offset( ret[0], ret[1])
        if func_sym is not None:
            print func_sym
        # except :

    else :
        print "%x is not a valid address" %(vaddr,)    

    # ret = get_symb_with_offset('/lib/arm-linux-gnueabihf/libtinfo.so.5.9', 1212)    
    # print ret

if __name__ == "__main__":
    main()
    sys.exit(0)    
