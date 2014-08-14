import os, shlex, sys

"""The CmdInterpreter class will interprent commands and return output"""
class CmdInterpreter():

	hist = []
	directory = ""

	def __init__(self):
		 """retrieve current directory upon startup of shell"""
		 self.directory = os.getcwd()

	def interpret(self, line):
		output = ""
		self.hist.append(line)
		commands = line.split('|')
		if not line:
			output = ""
		elif (self.checkPipes(commands)):
			output = "Invalid use of pipe '|'."
		elif(len(commands) == 1):
			command = self.parseCommand(line)
			output = self.executeCommand(command)
		if(len(output) == 0):
			return
		print(output)

	def checkPipes(self, line):
		for x in line:
			if (len(x) == 0):
				return True
		return False

	def parseCommand(self, line):
		splitLine = shlex.shlex(line, posix=True)
		splitLine.whitespace_split = False
		splitLine.wordchars += '#$+-,./?@^= '
		listCommand = list(splitLine)
		if (len(listCommand) > 1):
			args = listCommand[1]
			for i in range(2, len(listCommand)):
				args += listCommand[i]
				return [listCommand[0], args]
		return listCommand

	def executeCommand(self, command):
		if(command[0] == "echo"):
			output = self.executeEcho(command[1])
		elif(command[0] == "pwd"):
			output = self.executePwd()
		elif(command[0] == "cd"):
			if(len(command) == 1):
				self.executeCd([command[0]])
			else:
				self.executeCd(command)
			output = ""
		elif(command[0] == "ls"):
			if(len(command) == 1):
				output = self.executeLs(['ls'])
			else:
				output = self.executeLs(['ls',command[1]])
		else:
			output = "LIES!"
		return output

	def executeEcho(self, arg):
		pStdin = os.dup(0)
		pStdout = os.dup(1)
		r, w= os.pipe()
		pid = os.fork()
		if (pid == 0):
			os.close(1)
			os.dup2(w, 1)
			os.close(r)
			os.close(w)
			os.execvp('/bin/echo', ['echo', arg])
		else:
			os.close(0)
			os.dup2(r, 0)
			os.close(r)
			os.close(w)
			os.waitpid(pid, 0)
			line = input()
			os.dup2(pStdin, 0)
			os.dup2(pStdout, 1)
			return line

	def executePwd(self):
		pStdin = os.dup(0)
		pStdout = os.dup(1)
		r, w= os.pipe()
		pid = os.fork()
		if (pid == 0):
			os.close(1)
			os.dup2(w, 1)
			os.close(r)
			os.close(w)
			os.execvp('/bin/pwd', ['/bin/pwd'])
		else:
			os.close(0)
			os.dup2(r, 0)
			os.close(r)
			os.close(w)
			os.waitpid(pid, 0)
			line = ""
			for x in input():
				line += x
			os.dup2(pStdin, 0)
			os.dup2(pStdout, 1)
			return line

	def executeCd(self, arg):
		if (len(arg) == 1):
			"""Not Currently Working"""
			self.executeCd(self.directory)
		else:
			try:
				os.chdir(arg[1])
			except OSError:
				print("cd: '", arg, "': No such file or directory", sep='')

	def executeLs(self, arg):
		pStdin = os.dup(0)
		pStdout = os.dup(1)
		r, w= os.pipe()
		print(arg)
		pid = os.fork()
		if (pid == 0):
			os.close(1)
			os.dup2(w, 1)
			os.close(r)
			os.close(w)
			os.execvp('/bin/ls', arg)
		else:
			os.close(0)
			os.dup2(r, 0)
			os.close(r)
			os.close(w)
			os.waitpid(pid, 0)
			line = input()
			os.dup2(pStdin, 0)
			os.dup2(pStdout, 1)
			return line




def main():
	interpreter = CmdInterpreter()
	while(True):
		line = input('py> ')
		interpreter.interpret(line)

if __name__ == main():
	main()