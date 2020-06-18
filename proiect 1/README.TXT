
Documentatie etapa I RIW
Student: Bradu Veronica, grupa 1408B

[Porter]: Am ales Stemmer-ul Porter deoarece acesta foloseste 'Suffix Stripping' pentru a returna radacina unui cuvand.
Practic, acesta nu urmareste reguli lingvistice, ci un set de reguli pentru stergerea sufixelor(ex s din cats => cat, -ing, -ed).Acest lucru il face usor de utiliozat si rapid, fiind utilizat deseori in probleme de 'Information Retrieval'.

[Mongo]:
Conexiunea la mongo :
try:
    db_connection = pymongo.MongoClient('localhost', 27017)
    db = db_connection.riwproject
    print("Connected!!")
except:
    print("Try again!!")

[inserare index direct]:
is_in_db = False
        for element in db.direct_index.find():
            if element['doc'] == str(input_file):
                is_in_db = True

        if not is_in_db:
            db.direct_index.insert_one({
                'doc': input_file,
                'terms': self.words_dict
            })
[inserare index indirect] - incarcare din fisier json
 if 'indirect_index' not in db.list_collection_names():
            db.indirect_index.insert_one(json_dict)

Abordarile alese pt cele 2 inserari determina inserari elemente unice(la insert nu exista conditie de verificare duplicate)

[Cautare booleana]

[functie]
Cautare booleana operatii: AND, OR, NOT

def execute_operation(operand1, operation, operand2):
    if operation == 'AND':
        return operand1.intersection(operand2)
    elif operation == 'OR':
        return operand1.union(operand2)
    elif operation == 'NOT':
        return operand1.difference(operand2)

Queryul citit din consola este spart in cuvinte si pt fiecare cuvant se determina fisierul 
/fisierele din care face parte(folosind indexul indirect) si se insereaza in set.
Seturile sunt appenduite intr-o lista si face cautarea booleana intre fiecare 2 seturi.

[PathClass] : Obtinerea cailor spre fisiere se face in clasa PathClass.

[TextParser] : Se obtin dictionarele(dupa verificarea fiecarui cuvant pt is_stopword, is_not_special_character, is_exception) si se salveaza in fisier si in mongo.
get_indirect_index transforma indexul direct in index indirect.
Se foloseste stemmerul Porter.

[HtmlParser] : pentru a prelua continutul documentului html curent si pt procesare folosim continutul din body.
[Cautare Vectoriala] S-a facut preprocesare TF, IDF, TF*IDF pt fisiere, insa nu am realizat si cautarea vectoriala pe query


Referinte bibliografice:
1.Laboratoare RIW MOODLE
2.https://www.datacamp.com/community/tutorials/stemming-lemmatization-python
