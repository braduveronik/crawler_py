from queue import Queue
import os

def find_path():
	dir_list = Queue()
	file_list = Queue()

	def crawl_dir(dir_path):
		for obj in os.scandir(dir_path):
			if obj.is_dir():
				dir_list.put(obj.path)
			elif obj.is_file():
				file_list.put(obj.path)
	def crawl(dir_path):
		dir_list.put(dir_path)
		while not dir_list.empty():
			scan_dir = dir_list.get()
			crawl_dir(scan_dir)
		return file_list.queue
if __name__== "__main__":
	output = open('output_files_path.txt','w')
	input = 'input_files'
	myPathQueue = crawl(input)
	#output.write(str(myPathQueue))
	while True:
	    try:
	        output.write(str(myPathQueue.pop()) + '\n')
	    except IndexError:
	        break
	output.close()


