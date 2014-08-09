#!/usr/bin/python
# -*- coding: UTF-8 -*-  
# Description: utility to caculate the mapped share library and offset of vaddr
# Author: lancebai@gmial.com
#

import re
import sys, subprocess  
import argparse    

# library_name, attributes, start, end
# TODO: move into const.py
INDEX_NAME=0
INDEX_ATTR=1
INDEX_START=2
INDEX_END=3

mem_map_list = []



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

            if m is not None :
                attributes = m.group(3) 
                start = int(m.group(1), 16)
                end = int(m.group(2), 16)
                library_name = m.group(8).strip()
                # mem_file.seek(start)  # seek to region start
                # chunk = mem_file.read(end - start)  # read region contents

                #ignore the program data mmap
                if library_name == "" :
                    continue


                # print library_name, "is not in the list"
                mem_map_list.append((library_name, attributes, start, end))

                print "%x - %x  %s %s\n" % (start, end, attributes, library_name,),   # dump contents to standard output

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
    for list_entry in mem_map_list:
        if list_entry[INDEX_START] <=  vaddr <=  list_entry[INDEX_END] :
            return (list_entry[INDEX_NAME], list_entry[INDEX_ATTR] , vaddr - list_entry[INDEX_START])
    return None        


def iterate_mmap():
    print "======================"
    for list_entry in mem_map_list:
        print "%x - %x, %s %s" %(list_entry[INDEX_START], list_entry[INDEX_END], list_entry[INDEX_ATTR], list_entry[INDEX_NAME]),
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
                
# attr: rwxp 
def isRODataSection(attr):
    if attr is None or attr < 4:
        raise ValueError ('not a valid attribute')
    if attr[0] is 'r' and attr[1] is not 'w' :
        return True
    else:
        return False


def isRWDataSection(attr):
    if attr is None or attr < 4:
        raise ValueError ('not a valid attribute')
    if attr[0] is 'r' and attr[1] is 'w' :
        return True
    else:
        return False

def isTextSection(attr):
    if attr is None or attr < 4:
        raise ValueError ('not a valid attribute')
    if attr[2] is 'x':
        return True
    else:
        return False    

def main():
    print "main function"
    pid = parse_param().pid
    vaddr = int(parse_param().vaddr, 16);

    print "the parsing pid is:", pid  
    
    if not analyse_memory_of_process(pid) :
        sys.exit(0)

    # iterate_mmap()
        
    ret = lookup_mapped_library(vaddr)
    print "the address we are looking for:%x" %(vaddr, )

    if ret != None :
        print "library:%s, attr:%s, offset:%x" %( ret[0], ret[1] ,ret[2], )

        
        if  ret[0] in ["[heap]", "[stack]", "[vectors]" ] :
            print "is in %s section" %(ret[0],)

        elif  isTextSection(ret[1]) is True:
            print "it is Text section"
            func_sym = get_symb_with_offset( ret[0], ret[2])
            if func_sym is not None:
                print func_sym

        elif isRWDataSection(ret[1]) is True: 
            print "it is RW Data section"
        elif isRODataSection(ret[1]) is True:
            print "it is Read Only Data Section"

        
        

    else :
        print "%x is not a valid address" %(vaddr,)    

    # ret = get_symb_with_offset('/lib/arm-linux-gnueabihf/libtinfo.so.5.9', 1212)    
    # print ret

if __name__ == "__main__":
    main()
    sys.exit(0)    
