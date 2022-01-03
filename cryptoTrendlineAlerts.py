import os
from multiprocessing import Process

pythonVersionCmd = os.popen('python --version').read()

if int(pythonVersionCmd.split(" ")[1][0]) == 3:
	pythonCmd = "python "
elif int(pythonVersionCmd.split(" ")[1][0]) == 2:
	pythonVersionCmd = os.popen('python3 --version').read()
	try:
		pythonVersionCmd = int(pythonVersionCmd.split(" ")[1][0])
		if int(pythonVersionCmd.split(" ")[1][0]) == 3:
			pythonCmd = "python3 "
	except:
		print("You need Python 3.X.X to run this.")
else:
	print("You need Python 3.X.X to run this.")

def trendlineManager():
    os.system(pythonCmd + "trendlineManager.py")     

def alertSender():
    os.system(pythonCmd + "alertSender.py") 

if __name__ == '__main__':
    p = Process(target=trendlineManager)
    q = Process(target=alertSender)
    p.start()
    q.start()
    p.join()
    q.join()