
# command line for turingmachine

import turingmachine as turing
from turingmachine import turingmachineversion
from importlib.metadata import version as versio
import sys, os

mac = turing.machine()

version = sys.version_info

program = ""

def chtoinst(foo):
    th = hex(ord(foo))
    th = th.replace("0x","")
    return "1{};2".format(th)

def asm():
  program = []
  while True:
    inp = input("=> ")
    inps = inp.split(" ")
    if inps[0] == "exit": return ";".join(program)
    elif inps[0] == "pchr": program.append("00;1{};2".format(inps[1])) # my first macro!
    elif inps[0] == "addr": program.append("0{}".format(inps[1]))
    elif inps[0] == "addr+": program.append("4")
    elif inps[0] == "addr-": program.append("8")
    elif inps[0] == "cta": program.append("c")
    elif inps[0] == "set": program.append("1{}".format(inps[1]))
    elif inps[0] == "cel+": program.append("5")
    elif inps[0] == "cel-": program.append("9")
    elif inps[0] == "atc": program.append("d")
    elif inps[0] == "oascii": program.append("2")
    elif inps[0] == "oint": program.append("6")
    elif inps[0] == "iascii": program.append("a")
    elif inps[0] == "iint": program.append("e")
    elif inps[0] == "restart": program.append("3")
    elif inps[0] == "jnz": program.append("7")
    elif inps[0] == "lbl": program.append("b{}".format(inps[1]))
    elif inps[0] == "goto": program.append("f{}".format(inps[1]))
    elif inps[0] == "pstr": program.append(";".join(list(map(chtoinst,list(inps[1])))))
    else: print("error")

print("TuringMachine Command Line (0.3.1)\nPython {}.{}.{}\nTuringMachine {}".format(version.major,version.minor,version.micro,turingmachineversion.version))

while True:
    inp = input("> ")
    if "run" == inp:
        mac.program(program,sys.stdout)
    elif "exit" == inp:
        exit()
    elif "printstr" == inp:
        print(";".join(list(map(chtoinst,list(input("string:"))))))
    elif "load" == inp:
        program = open(input("Program ID: ") + ".tg").read()
    elif "save" == inp:
      inp = input("Program ID: ") + ".tg"
      try: open(inp,"w").write(program)
      except: open(inp,"x").write(program)
    elif "remove" == inp:
      try:os.remove(input("Program ID: ") + ".tg")
      except:print("PROGRAM NOT FOUND")
    elif "asm" == inp:
      progra = asm()
      if program == "": program = progra
      else: program += ";" + progra
    elif "list" == inp: print(program)
    elif "clear" == inp: program = ""
    else: program = inp
