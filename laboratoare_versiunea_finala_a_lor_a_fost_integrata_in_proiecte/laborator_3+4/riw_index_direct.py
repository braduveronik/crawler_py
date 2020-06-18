import os
import json
from nltk.stem import PorterStemmer
from queue import Queue
from pprint import pprint
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def get_indirect_index(file_name,words_directory):
    for key, value in words_directory.items():
      dict_key = {file_name: value}

      if key not in list_of_dict:
        list_of_dict[key]= dict_key
      else:
        list_of_dict[key].update(dict_key)

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
        if character not in [',', '.', '!', '?', ';', '\'', '', '[', ']', '-', '/', '\\', '<', '>', '=',':', '"','(', ')', '%', '$', '_', '#', '@', '$', '%', '{', '}', '&', '*', '|'] and character.isspace() == False:
            return True

    def get_dictionaries(self, input_file):

          input = open(str(input_file), mode='r', encoding='utf-8-sig')
          input_text = input.read()

          for index, character in enumerate(input_text):
              if self.is_not_special_character(character) == True and character.isdigit() == False:
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
          self.output_file.write('\n\n\t'+str(input_file)+': ' + str(self.words_dict).replace("{","[").replace("}", "]"))
          #self.output_file.write('\n\n\texceptions: ' + str(self.exceptions_dict))
          get_indirect_index(input_file,self.words_dict)
          self.words_dict = {}
          self.exceptions_dict = {}

class HtmlParser():

  def __init__(self, file_path, base_url):
        self.fp = open(file_path)
        self.soup = BeautifulSoup(self.fp.read(), "lxml")
        self.url = base_url
        
  def extract_content(self):
         title = self.soup.find('title')
         if title:
             title = title.text

         description = keywords = robots =  None
         meta_tags = self.soup.find_all('meta')
         for item in meta_tags:
             attr = item.attrs.get('name')
             if attr:
                 if attr.lower() == 'keywords':
                     keywords = item.attrs.get('content')
                 elif attr.lower() == 'description':
                     description = item.attrs.get('content')
                 elif attr.lower() == 'robots':
                     robots = item.attrs.get('content')
         return title, keywords, description, robots

  def extract_links(self):
        all_links = []
        for link in self.soup.findAll('a'):
            all_links.append(link.get('href'))
        return [x for x in all_links if x]

  def extract_link_absolute(self, all_links):
        for link in all_links:
            if link.find('/') == -1 or './' in link or '../' in link:
                full_link = urljoin(self.url, link)
                # full_link = link
                index = links.index(link)
                all_links[index] = full_link
        return all_links
        
  def extract_text(self):
      return self.soup.body.text

def execute_operation(operand1, operation, operand2):
    if operation == 'AND':
        return operand1.intersection(operand2)
    elif operation == 'OR':
        return operand1.union(operand2)
    elif operation == 'NOT':
        return operand1.difference(operand2)

if __name__== "__main__":

          if os.path.exists("index_direct_cantitativ.txt"):
            os.remove("index_direct_cantitativ.txt")
          
          if os.path.exists("index_invers_cantitativ.txt"):
            os.remove("index_invers_cantitativ.txt")
          
          list_of_dict = {} #indirect index
          input_directory = 'input_files'
          output_writing_paths = 'output_files_path.txt'
          path_queue = Queue()
          find_path = PathClass(input_directory,output_writing_paths, path_queue,path_queue)
          find_path.get_path()
          
          exceptions_list = open('text_exceptions.txt', 'r').read()
          stopword_list = open('text_stopwords.txt', 'r').read()
          
          parsing_output = open('index_direct_cantitativ.txt', 'a')
          parsing_text = TextParser(output_writing_paths,exceptions_list,stopword_list,parsing_output,'',{},{},PorterStemmer())
          
          
          listFiles=open(output_writing_paths, 'r')
          line = listFiles.readline()
          while line:
              new_file = line.replace('\n', '')
              # print("Parsing content from: " + new_file)
              soup = HtmlParser(new_file, 'guru99.com.html')
              soup = soup.extract_text()
              parsing_text.get_dictionaries(new_file)

              line = listFiles.readline()

          listFiles.close()
          parsing_text.output_file.close()
          
          with open("index_invers_cantitativ.json", "w") as index_indirect_all:
            index_indirect_all.write('{\n')
            for key, values in list_of_dict.items():
              index_indirect_all.write('\t"' + str(key) + '": [\n')
              for path,count in values.items():
                if path != list(values.keys())[-1]:
                    index_indirect_all.write('\t\t["' + str(path) +'", ' + str(count) + '],\n')
                else:
                  index_indirect_all.write('\t\t["' + str(path) +'", ' + str(count) + ']\n')
              if key != list(list_of_dict.items())[-1][0]:
                index_indirect_all.write('\t],\n')
              else:
                index_indirect_all.write('\t]\n')
            index_indirect_all.write('}')

          with open("index_invers_cantitativ.json") as fp:
            indirect_json = fp.read()
            json_dict = json.loads(indirect_json)
            and_op = 'fork AND panda'
            or_op = 'cluster OR stanford'
            not_op = 'matrix NOT frame OR anaconda'
            operations = [and_op, or_op, not_op]
            operands_list = []

            for op in operations:
                sets_lists = []
                valid_query = True
                items = op.split(' ')
                for i in range(1, len(items), 2):
                    if items[i] not in ['AND', 'OR', 'NOT']:
                        print("Invalid query")
                        valid_query = False
                        break
                if valid_query:
                    for i in range(0, len(items), 2):
                        temp = set()
                        if json_dict.get(items[i]):
                            for x in json_dict[items[i]]:
                                temp.add(x[0])
                            sets_lists.append(temp.copy())
                        else:
                            sets_lists.append(set())

                    operand1 = sets_lists[0]
                    operation = items[1]
                    operand2 = sets_lists[1]
                    result = execute_operation(operand1, operation, operand2)
                    if result:
                        print(str(items) + ' = ' + str(result).replace('{', '[').replace('}',']'))

                    if len(items) > 3:
                        set_index = 2
                        ops = []
                        for i in range(3, len(items), 2):
                            ops.append(items[i])
                        for current_op in ops:
                            operand2 = sets_lists[set_index]
                            result = execute_operation(result, current_op, operand2)
                        print(str(items) + ' = ' + str(result).replace('{', '[').replace('}',']'))
