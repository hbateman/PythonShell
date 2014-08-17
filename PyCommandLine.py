import os, shlex, sys

"""The CmdInterpreter class will interprent commands and return output"""
class CmdInterpreter():

	hist = []
	directory = ""
	processes = []
	amper = False

	def __init__(self):
		 """retrieve current directory upon startup of shell"""
		 self.directory = os.getcwd()

	"""Interpret a line of code, decide how to execute"""
	def interpret(self, line):
		self.amper = False
		self.hist.append(line)
		if not line:
			return
		if (line[len(line)-1] == "&"):
			self.amper = True
			line = line.replace('&', '')
		commands = line.split('|')
		if (self.checkPipes(commands)):
			print("Invalid use of pipe '|'.")
			return
		else:
			pid = os.fork()
			if (pid == 0):
				self.execute(commands)
			else:
				if (self.amper == True):
					self.processes.append(pid)
					print("[" + str(self.processes.index(pid)+1) + "]" + " " + str(pid))
					return
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
		if(command[0] == "cd"):
			self.executeCd(command)
		elif(command[0] == "history" or command[0] == "h"):
			self.executeHistory(command)
		else:
			self.executeNorm(command)
		return

	"""Recursive function for case when pipes are used"""
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
			if (self.amper == True):
				f = open(os.devnull, 'w')
				os.dup2(f.fileno(), 1)
				os.close(f.fileno())
			self.executeCommand(self.parseCommand(command))

	def executeNorm(self, arg):
		try:
			os.execvp(arg[0], arg)
		except FileNotFoundError:
			print("command not found")

	def executeCd(self, arg):
		if (len(arg) == 1):
			self.executeCd(['cd', self.directory])
		else:
			try:
				os.chdir(arg[1])
			except OSError:
				print("cd: '", arg[1], "': No such file or directory", sep = "")

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