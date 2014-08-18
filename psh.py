import os, shlex, sys, subprocess

"""Hugo Bateman - 5602043"""

"""The psh class will interprent commands and return output"""
class psh():

	hist = []
	directory = ""
	currentJobs = []
	amper = False
	STATES = { "R":"Running", "S":"Sleeping", "Z":"Zombie", "D":"Done", "T":"Stopped", "W":"Paging", "X":"Dead"}

	def __init__(self):
		 """retrieve current directory upon startup of shell"""
		 self.directory = os.getcwd()

	"""Interpret a line of code, decide how to execute"""
	def interpret(self, input):
		self.amper = False
		if not input:
			return
		line = input.strip()
		self.hist.append(line)
		if (line[len(line)-1] == "&"):
			self.amper = True
			line = line.replace('&', '')
		commands = line.split('|')
		if (self.checkPipes(commands)):
			print("Invalid use of pipe '|'.")
			return
		elif (len(commands) == 1 and self.amper == False):
			self.executeSingle(commands)
		else:
			pid = os.fork()
			if (pid == 0):
				self.execute(commands)
			else:
				if (self.amper == True):
					self.currentJobs.append(Job(input, pid, (len(self.currentJobs))+1))
					print("[" + str(len(self.currentJobs)) + "]" + " " + str(pid))
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

	"""Detrmine which single command was called"""
	def executeSingle(self, command):
		cmd = self.parseCommand(command[0])
		if(cmd[0] == "cd"):
			self.executeCd(cmd, True)
		elif(cmd[0] == "history" or cmd[0] == "h"):
			self.executeHistory(cmd, True)
		elif(cmd[0] == "jobs"):
			self.executeJobs(command)
		else:
			pid = os.fork()
			if (pid == 0):
				self.execute(command)
			else:
				if (self.amper == True):
					self.currentJobs.append(Job(line, pid, (len(self.currentJobs))+1))
					print("[" + str(len(self.currentJobs)) + "]" + " " + str(pid))
					return
				else:
					os.waitpid(pid, 0)
		return

	"""detirmine which command was called"""
	def executeCommand(self, command):
		if(command[0] == "cd"):
			self.executeCd(command, False)
		elif(command[0] == "history" or command[0] == "h"):
			self.executeHistory(command, False)
		elif(command[0] == "jobs"):
			self.executeJobs(command)
		else:
			self.executeNorm(command)
		return

	"""Check the current status of the running processes"""
	def checkJobs(self):
		for j in self.currentJobs:
			ps = subprocess.Popen(['ps', '-p', str(j.pid), '-o', 'state='], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			result, error = ps.communicate()
			if (result.decode()[0] == "Z"):
				os.waitpid(j.pid, 0)
				self.currentJobs.remove(j)

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
			self.executeCommand(self.parseCommand(command))

	"""execute a normal function"""
	def executeNorm(self, arg):
		try:
			os.execvp(arg[0], arg)
		except FileNotFoundError:
			print("command not found")

	"""print the current working directory"""
	def executePwd(self):
		print(os.getcwd())
		return

	"""execute the cd command"""
	def executeCd(self, arg, isSingle):
		if (len(arg) == 1):
			self.executeCd(['cd', self.directory], isSingle)
		else:
			try:
				os.chdir(arg[1])
			except OSError:
				print("cd: '", arg[1], "': No such file or directory", sep = "")
		if (isSingle):
			return
		else:
			os.kill(os.getpid(), 1)


	"""execute the history command"""
	def executeHistory(self, arg, isSingle):
		if (len(arg) > 1):
			self.hist.remove(self.hist[len(self.hist)-1])
			self.interpret(self.hist[int(arg[1])-1])
		else:
			i=1;
			for line in self.hist:
				sys.stdout.write(str(i) + ": " + line + '\n')
				i = i + 1
			sys.stdout.flush()
		if (isSingle):
			return
		else:
			os.kill(os.getpid(), 1)

	"""execute the jobs command"""
	def executeJobs(self, arg):
		for j in self.currentJobs:
			ps = subprocess.Popen(['ps', '-p', str(j.pid), '-o', 'state='], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			result, error = ps.communicate()
			if result.decode() != '':
				print('[{}] <{}> {}'.format(j.number, self.STATES[result.decode()[0]], j.command))

"""Job objects are used to keep track of the currently running jobs"""
class Job():
	command = ""
	status = ""
	pid = 0
	number = 0

	def __init__(self, jCommand, jPid, jNumber):
		self.command = jCommand
		self.pid = jPid
		self. status = "Running"
		self.number = jNumber


def main():
	interpreter = psh()
	while(True):
		interpreter.checkJobs()
		try:
			line = input('py> ')
		except EOFError:
			sys.exit(0)
		interpreter.interpret(line)

if __name__ == main():
	main()