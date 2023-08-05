
# turing machine

import sys

class machine():
    def __init__(self):
        def program(s,std):
            parsed = s.split(";")
            addr = 0
            data = {0:0}
            lbl = {}
            def out(st):
                std.write(st)
                std.flush()
            n = -1
            
            while n+1 != len(parsed):
                n += 1
                x = parsed[n]
                # instruction parser
                arg = x[slice(1,len(x))]
                ins = x[0]
                
                if (arg != ""): arg = int(arg,base=16)
                
                # instruction processor
                if (not addr in data): data[addr] = 0
                if ins == "0": addr = hex(arg) # MemSlot
                elif ins == "4": addr += 1
                elif ins == "8": addr -= 1
                elif ins == "c": addr = data[addr]
                elif ins == "1": data[addr] = arg # DatSlot
                elif ins == "5": data[addr] += 1
                elif ins == "9": data[addr] -= 1
                elif ins == "d": data[addr] = addr
                elif ins == "2": out(chr(data[addr])) # I/O
                elif ins == "6": out(data[addr])
                elif ins == "a": data[addr] = ord(input("#")[0])
                elif ins == "e": data[addr] = int(input("%"))
                elif ins == "3": n = -1
                elif ins == "7" and data[addr] != 0: n += 1
                elif ins == "b": lbl[arg] = n
                elif ins == "f": n = lbl[arg]
        self.program = program

