import os, shlex, sys

"""The CmdInterpreter class will interprent commands and return output"""
class CmdInterpreter():

	hist = []
	directory = ""

	def __init__(self):
		 """retrieve current directory upon startup of shell"""
		 self.directory = os.getcwd()

	"""Interpret a line of code, decide how to execute"""
	def interpret(self, line):
		self.hist.append(line)
		commands = line.split('|')
		if not line:
			output = ""
		elif (self.checkPipes(commands)):
			print("Invalid use of pipe '|'.")
			return
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

	"""Check valid use of pipes"""
	def checkPipes(self, line):
		for x in line:
			if (len(x) == 0):
				return True
		return False

	"""Parse a command"""
	def parseCommand(self, line):
		splitLine = shlex.shlex(line, posix=True)
		splitLine.whitespace_split = False
		splitLine.wordchars += '#$+-,./?@^= '
		listCommand = list(splitLine)
		return listCommand

	"""detirmine which command"""
	def executeCommand(self, command):
		if(command[0] == "echo"):
			output = self.executeEcho(command)
		elif(command[0] == "pwd"):
			output = self.executePwd(command)
		elif(command[0] == "cd"):
			self.executeCd(command)
		elif(command[0] == "ls"):
			self.executeLs(command)
		elif(command[0] == "ps"):
			self.executePs(command)
		elif(command[0] == "wc"):
			self.executeWc(command)
		elif(command[0] == "grep"):
			self.executeGrep(command)
		elif(command[0] == "diff"):
			self.executeDiff(command)		
		elif(command[0] == "history"):
			self.executeHistory(command)		
		elif(command[0] == "h"):
			self.executeHistory(command)
		else:
			print("command not found")
		return

	"""Recursive function for case whe npipes are used"""
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
				os.close(0)
				os.dup2(r, 0)
				os.close(r)
				os.close(w)
				os.waitpid(pid, 0)
				commands.remove(commands[0])
				self.execute(commands)
		else:
			command = commands[0]
			self.executeCommand(self.parseCommand(command))

	def executeEcho(self, arg):
		os.execvp('/bin/echo', arg)

	def executePwd(self, arg):
		os.execvp('/bin/pwd', arg)

	def executeCd(self, arg):
		if (len(arg) == 1):
			self.executeCd(['cd', self.directory])
		else:
			try:
				os.chdir(arg[1])
			except OSError as e:
				print("cd: '", arg[1], "': No such file or directory", sep = '')
				"""print(e.args)"""

	def executeLs(self, arg):
		os.execvp('/bin/ls', arg)

	def executePs(self, arg):
		os.execvp('/bin/ps', arg)

	def executeWc(self, arg):
		os.execvp('/usr/bin/wc', arg)

	def executeDiff(self, arg):
		os.execvp('/usr/bin/diff', arg)

	def executeGrep(self, arg):
		os.execvp('/bin/grep', arg)

	def executeHistory(self, arg):
		"""If re-executing historic command
		IMPLEMENT: testing for invalid input"""
		if (len(arg) > 1):
			print(self.hist)
			self.hist[len(self.hist)-1] = self.hist[(int(arg[1])-1)]
			print(self.hist)
			self.interpret(self.hist[(int(arg[1])-1)])
		else:
			print(self.hist)
			i=1;
			for line in self.hist:
				sys.stdout.write(str(i) + ": " + line + '\n')
				i = i + 1
			sys.stdout.flush()
		os.kill(os.getpid(), 1)


def main():
	interpreter = CmdInterpreter()
	while(True):
		line = input('py> ')
		interpreter.interpret(line)

if __name__ == main():
	main()