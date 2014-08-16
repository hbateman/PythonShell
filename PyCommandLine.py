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
		elif (len(commands) == 1):
			pid = os.fork()
			if (pid == 0):
				self.executeCommand(self.parseCommand(commands[0]))
			else:
				os.waitpid(pid, 0)
		else:
			pid = os.fork()
			if (pid == 0):
				self.execute(commands)
			else:
				os.waitpid(pid, 0)
		return

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
			self.executeCd(command)
		elif(command[0] == "ls"):
			self.executeLs(command)
		elif(command[0] == "ps"):
			self.executePs(command)
		else:
			print("command not found")
		return

	def execute(self, commands):
		if (len(commands) > 1):
			r, w = os.pipe()
			pid = os.fork()
			if (pid == 0):
				os.close(1)
				os.dup2(w, 1)
				os.close(r)
				os.close(w)
				command = commands[0]
				self.executeCommand(self.parseCommand(command))
			else:
				os.close(1)
				os.dup2(w, 1)
				os.close(r)
				os.close(w)
				os.waitpid(pid, 0)
				out = sys.stdin.read()
				commands.remove(commands[0])
				nextIn = " " + out
				commands[0] += nextIn
				self.execute(commands)
		else:
			command = commands[0]
			self.executeCommand(self.parseCommand(command))

	def executeEcho(self, arg):
		os.execvp('/bin/echo', ['echo', arg])

	def executePwd(self):
		os.execvp('/bin/pwd', ['/bin/pwd'])

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
		if (len(arg) > 1):
			os.execvp('/bin/ls', ['ls', arg[1]])
		else:
		 os.execvp('/bin/ls', ['ls'])

	def executePs(self, arg):
		if (len(arg) > 1):
			os.execvp('/bin/ps', ['ps', arg[1]])
		else:
		 os.execvp('/bin/ps', ['ps'])



def main():
	interpreter = CmdInterpreter()
	while(True):
		line = input('py> ')
		interpreter.interpret(line)

if __name__ == main():
	main()