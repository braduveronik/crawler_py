import collections
import nltk
from nltk.stem import PorterStemmer #https://www.datacamp.com/community/tutorials/stemming-lemmatization-python
from queue import Queue
import os

class PathClass():

    def __init__(self, dir_path, output_file, dir_list, file_list):
      self.dir_path = dir_path
      self.output_file = output_file
      self.dir_list = Queue()
      self.file_list = Queue()

    def crawl_dir(self, dir_path):
        for obj in os.scandir(str(dir_path)):
            if obj.is_dir():
                self.dir_list.put(obj.path)
            elif obj.is_file():
                self.file_list.put(obj.path)

    def crawl(self):
        self.dir_list.put(self.dir_path)
        while not self.dir_list.empty():
            scan_dir = self.dir_list.get()
            self.crawl_dir(scan_dir)
        return self.file_list.queue

    def get_path(self):
        output = open(str(self.output_file), 'w')
        myPathQueue = self.crawl()
        while True:
            try:
                output.write(str(myPathQueue.pop()) + '\n')
            except IndexError:
                break
        output.close()

class TextParser():

    def __init__(self, input_file, exceptions_list, stopwords_list, output_file, word,words_dict, exceptions_dict, porter):
        self.input_file = input_file
        self.exceptions_list = exceptions_list
        self.stopwords_list = stopwords_list
        self.output_file  = output_file

        self.word = word
        self.words_dict = words_dict
        self.exceptions_dict = exceptions_dict
        self.porter = porter

    def get_cf_w_porter(self,word):
        return self.porter.stem(word.lower())

    def add_word_in_dict(self,word, words_dict):
        words_dict[word] = 1

    def update_value_of_key(self,word, words_dict):
        words_dict[word] += 1

    def is_exception(self,word):
        try:
            if word in exceptions_list and word != '' and word.lower() not in self.stopwords_list and self.exceptions_list[self.exceptions_list.find((word))-1]=='\n' and self.exceptions_list[self.exceptions_list.find((word))+len(self.word)]=='\n':
                return True
        except:
            return False

    def is_stopword(self,word):
        if word in self.stopwords_list:
            return True

    def is_not_special_character(self,character):
        if character not in [',', '.', '!', '?', ';', '\'', '', '[', ']', '-', '/', '\\'] and character.isspace() == False:
            return True

    def get_dictionaries(self, input_file):

          input = open(str(input_file), mode='r', encoding='utf-8-sig')
          input_text = input.read()

          for index, character in enumerate(input_text):
              if self.is_not_special_character(character) == True:
                  self.word += str(character)
              else:
                  if self.is_exception(self.word):
                      if self.word not in self.exceptions_dict:
                          self.add_word_in_dict(self.word,self.exceptions_dict)
                      else:
                          self.update_value_of_key(self.word,self.exceptions_dict)
                      self.word = ''
                  elif self.is_stopword(self.word.lower()):
                      self.word = ''
                  else:
                      self.word = self.get_cf_w_porter(self.word)
                      if self.word not in self.words_dict:
                         self. words_dict[self.word] = 1
                      else:
                          self.update_value_of_key(self.word,self.words_dict)
                      self.word= ''
          self.output_file.write('\n\n\t'+str(input_file)+': ' + str(self.words_dict))
          self.output_file.write('\n\n\texceptions: ' + str(self.exceptions_dict))
          self.words_dict = {}
          self.exceptions_dict = {}
if __name__ == "__main__":

  if os.path.exists("text_output.txt"):
        os.remove("text_output.txt")

  input_directory = 'input_files'
  output_writing_paths = 'find_path_with_Qs/output_files_path.txt'
  path_queue = Queue()
  find_path = PathClass(input_directory,output_writing_paths, path_queue,path_queue)
  find_path.get_path()

  exceptions_list = open('text_exceptions.txt', 'r').read()
  stopword_list = open('text_stopwords.txt', 'r').read()
  parsing_output = open('text_output.txt', 'a')
  parsing_text = TextParser(output_writing_paths,exceptions_list,stopword_list,parsing_output,'',{},{},PorterStemmer())

  listFiles=open(output_writing_paths, 'r')
  line = listFiles.readline()
  while line:
    new_file = line.replace('\n', '')
    print("Parsing content from: " + new_file)
    parsing_text.get_dictionaries(new_file)
    line = listFiles.readline()
  listFiles.close()
  parsing_text.output_file.close()

