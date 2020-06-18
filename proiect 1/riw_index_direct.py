import os, json, math, numpy
from nltk.stem import PorterStemmer
from queue import Queue
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pymongo

def get_norm(vector):
    sum = 0
    for element in vector:
        sum += element**2
    return math.sqrt(sum)

def get_TF_query(query):
    tfQuery = {}
    for word in query:
        tfQuery[word] = round(count / float(len(query)), 4)
    return  tfQuery

def get_TF(dict):
    tfDict = {}
    dict_total_words = len(dict)
    for word, count in dict.items():
        tfDict[word] = round(count / float(dict_total_words), 4)
    return tfDict


def get_IDF(indirect_index_file, words, docList):
    idfDict = {}
    # number of documents that contains words
    for word, value in words.items():
        idfDict[word] = len(value)
    # formula
    for word, value in idfDict.items():
        idfDict[word] = round(math.log(docList/float(value)), 3)
    return idfDict


def get_TF_IDF(tfDict, idfDict):
    tfidf = {}
    for word, value in tfDict.items():
        tfidf[word] = round(value * idfDict[word],4)
    return tfidf


# 2nd
# getting the file's path with 2 Qes
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


# 2nd
# Porter stemmer applied
# words added to dictionary
# direct_index: dictionaries had been written into file("index_direct_cantitativ")
# indirect_index:
class TextParser():

    def __init__(self, input_file, exceptions_list, stopwords_list, output_file, word, words_dict, exceptions_dict,
                 porter):
        self.input_file = input_file
        self.exceptions_list = exceptions_list
        self.stopwords_list = stopwords_list
        self.output_file = output_file

        self.word = word
        self.words_dict = words_dict
        self.exceptions_dict = exceptions_dict
        self.porter = porter


    def get_cf_w_porter(self, word):
        return self.porter.stem(word.lower())

    def add_word_in_dict(self, word, words_dict):
        words_dict[word] = 1

    def update_value_of_key(self, word, words_dict):
        words_dict[word] += 1

    def is_exception(self, word):
        try:
            if word in exceptions_list and word != '' and word.lower() not in self.stopwords_list and \
                    self.exceptions_list[self.exceptions_list.find((word)) - 1] == '\n' and self.exceptions_list[
                self.exceptions_list.find((word)) + len(self.word)] == '\n':
                return True
        except:
            return False

    def is_stopword(self, word):
        if word in self.stopwords_list:
            return True

    def is_not_special_character(self, character):
        if character not in [',', '.', '!', '?', ';', '\'', '', '[', ']', '-', '/', '\\', '<', '>', '=', ':', '"', '(',
                             ')', '%', '$', '_', '#', '@', '$', '%', '{', '}', '&', '*',
                             '|'] and character.isspace() == False:
            return True

    def get_dictionaries(self, input_file):

        f_in = HtmlParser(input_file, 'guru99.com.html')
        input_text = f_in.extract_text()
        i = 0

        # character by character, no tokenizers used
        for index, character in enumerate(input_text):
            if self.is_not_special_character(character) == True and character.isdigit() == False:
                self.word += str(character)
            else:
                if self.is_exception(self.word):
                    if self.word not in self.exceptions_dict:
                        self.add_word_in_dict(self.word, self.exceptions_dict)
                    else:
                        self.update_value_of_key(self.word, self.exceptions_dict)
                    self.word = ''
                elif self.is_stopword(self.word.lower()):
                    self.word = ''
                else:
                    self.word = self.get_cf_w_porter(self.word)
                    if self.word not in self.words_dict:
                        self.words_dict[self.word] = 1
                    else:
                        self.update_value_of_key(self.word, self.words_dict)
                    self.word = ''

        self.output_file.write('\n' + str(input_file) + ' : ' + str(self.words_dict).replace("{", "[").replace("}", "]"))
        # self.output_file.write('\n\n\texceptions: ' + str(self.exceptions_dict))


        is_in_db = False
        for element in db.direct_index.find():
            if element['doc'] == str(input_file):
                is_in_db = True

        if not is_in_db:
            db.direct_index.insert_one({
                'doc': input_file,
                'terms': self.words_dict
            })

        #indirect index
        self.get_indirect_index(input_file, self.words_dict)

        #tf-direct index
        tf = get_TF(self.words_dict)
        tf_dict.append({input_file:tf})
        # print(tf_dict)
        i += 1

        self.words_dict = {}
        self.exceptions_dict = {}

    def get_indirect_index(self, file_name, words_directory):
        for key, value in words_directory.items():
            dict_key = {file_name: value}

            if key not in list_of_dict:
                list_of_dict[key] = dict_key
            else:
                list_of_dict[key].update(dict_key)

#1
#html parsing
class HtmlParser():

    def __init__(self, file_path, base_url):
        self.fp = open(file_path)
        self.soup = BeautifulSoup(self.fp.read(), "lxml")
        self.url = base_url

    def extract_content(self):
        title = self.soup.find('title')
        if title:
            title = title.text

        description = keywords = robots = None
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
                index = full_link.index(link)
                all_links[index] = full_link
        return all_links

    def extract_text(self):
        return self.soup.body.text


# union, intersaction, difference
def execute_operation(operand1, operation, operand2):
    if operation == 'AND':
        return operand1.intersection(operand2)
    elif operation == 'OR':
        return operand1.union(operand2)
    elif operation == 'NOT':
        return operand1.difference(operand2)

if __name__ == "__main__":

    try:
        db_connection = pymongo.MongoClient('localhost', 27017)
        db = db_connection.riwproject
        print("Connected!!")
    except:
        print("Try again!!")

    tf_dict = []
    idf_dict = {}
    tf_idf = []

    if os.path.exists("output/index_direct_cantitativ.txt"):
        os.remove("output/index_direct_cantitativ.txt")

    list_of_dict = {}  # indirect index
    input_directory = 'input_files'
    output_writing_paths = 'output/output_files_path.txt'

    path_queue = Queue()
    find_path = PathClass(input_directory, output_writing_paths, path_queue, path_queue)
    find_path.get_path()

    exceptions_list = open('text_exceptions_stopwords/text_exceptions.txt', 'r').read()
    stopword_list = open('text_exceptions_stopwords/text_stopwords.txt', 'r').read()

    parsing_output = open('output/index_direct_cantitativ.txt', 'a')
    parsing_text = TextParser(output_writing_paths, exceptions_list, stopword_list, parsing_output, '', {}, {},
                              PorterStemmer())

    listFiles = open(output_writing_paths, 'r', encoding='utf-8')
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

    with open("output/index_invers_cantitativ.json", "w") as index_indirect_all:
        index_indirect_all.write('{\n')
        for key, values in list_of_dict.items():
            index_indirect_all.write('\t"' + str(key) + '": [\n')
            for path, count in values.items():
                if path != list(values.keys())[-1]:
                    index_indirect_all.write('\t\t["' + str(path) + '", ' + str(count) + '],\n')
                else:
                    index_indirect_all.write('\t\t["' + str(path) + '", ' + str(count) + ']\n')
            if key != list(list_of_dict.items())[-1][0]:
                index_indirect_all.write('\t],\n')
            else:
                index_indirect_all.write('\t]\n')
        index_indirect_all.write('}')


        print("\ngetting tf")
        print(tf_dict)

        idf_dict = get_IDF(index_indirect_all, list_of_dict, 3)
        print("\ngetting idf")
        print(idf_dict)

        for tf in tf_dict:
            for link in tf:
                tf_idf.append(get_TF_IDF(tf[link],idf_dict))
        print("\ngetting tf_idf")
        print(tf_idf)

    with open("output/index_invers_cantitativ.json") as fp:
        indirect_json = fp.read()
        json_dict = json.loads(indirect_json)

        if 'indirect_index' not in db.list_collection_names():
            db.indirect_index.insert_one(json_dict)

        query = ['random forest vs pattern rail']
        # print('What are you interested in?')
        # query = input()
        for op in query:
            sets_lists = []
            valid_query = True
            items = op.split(' ')

            if valid_query:
                for i in range(0, len(items)):
                    temp = set()
                    if json_dict.get(items[i]):
                        for x, value in json_dict[items[i]]:
                            # idf_doc = get_idf_document(x,value)
                            # print("frecventa de aparitie a lui {0} in {1} este {2}", items[i], x, idf_doc)
                            if x not in temp:
                                temp.add(x)
                        sets_lists.append(temp.copy())
                    else:
                        sets_lists.append(set())

                print('\n**list of sets, each set contains all links for each word**')
                print(sets_lists)
                result = []
                for link in sets_lists:
                    result = execute_operation(link, 'OR', result)

                print('\nUnion between sets')
                print(result)

            queryTF = {}
            print("\nTF querry")
            print(get_TF_query(items))

