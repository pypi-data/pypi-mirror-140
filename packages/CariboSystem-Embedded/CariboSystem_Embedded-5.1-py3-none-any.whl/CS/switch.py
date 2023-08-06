command = ""
while command != "quit":
	#Update new changes to both core.py and switch.py
	command = input("@CariboOS:~> ")
	if command == "about":
		print("CariboOS")
		print("Version: 5.01")
		print("Copyright 2021 @ Zanvok Corporation")
	elif command == "command --list":
		print("\n Help \n About \n Status \n Exit \n Calc \n cls or cls or Clr \n")
	elif "release" in command:
		release =""
		while release != "quit":
			print("Release Details: ")
			print(" type --name to view name")
			print(" type --history to view history")
			release = input("release ")
			if release == "--name":
				print("Version: 5.01")
				print(colored('Code name: Buggy Bug', 'red'))
			elif release == "--history":
				print("Created on 1st Nov 2021")
				print("This is named Buggy Bug because it has many bugs!!")
			elif release == "exit":
				break
			else:
				print("Invalid release command!")
	elif command == "help":
		print("Commands for using CariboOS")
		from help import *
	elif command == "cmd":
                                     from cmd8 import *
	elif command == "status":
		print(colored("Under Development!" , 'red' , 'on_cyan'))
	elif command == "exit":
		break
	elif command == "calc":
		from calc import *
	elif command == "bsod":
		from bsod import *
		break
	elif command == "cls" or command == "clr" or command == "cls":
		import multiprocessing
		import time
		import os
		# bar
		def bar():
			for i in range(100):
				print(" ")
				time.sleep(1)

		if __name__ == '__main__':
			# Start bar as a process
			p = multiprocessing.Process(target=bar)
			p.start()

			# Wait for 2 seconds or until process finishes
			p.join(0)

			# If thread is still active
			if p.is_alive():
				print("")

				# Terminate - may not work if process is stuck for good
				p.terminate()
				# OR Kill - will work for sure, no chance for process to finish nicely however
				# p.kill()

				p.join()
		os.system('cls')
	elif command == "":
		print("")
	else:
		print("Invalid Command")
		print("Suggest more commands at https://sites.google.com/view/zanvokcorporation/ ")
