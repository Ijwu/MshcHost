from os import listdir
from regex import search
from os.path import join, isfile
from tqdm import tqdm
from threading import Thread
from traceback import format_exc
import pickle

index = None
regex_string = '<meta name="Microsoft.Help.Id" content="(.*?)" />'
threads = 8

def _index_extracts(path, regex_string, files, tq, ind):
    try:
        for file in files:
            if file[-5:] == ".html":
                with open(join(path, file), "r", encoding="utf-8") as f:
                    matching = search(regex_string, f.read())
                    if matching is not None:
                        id = matching.group(1)
                        ind[id] = file
                        tq.update()
    except Exception as e:
        ind["error"+path] = Exception(format_exc())

def initialize(path):
    global index, threads
    print("indexing")
    if index is not None:
        raise RuntimeError("Index was already initialized.")
    pickle_file = join(path, "index.pickle")
    if isfile(pickle_file):
        index = pickle.load(open(pickle_file, "rb"))
        print("found a pickled index, yummy")
        return
    print("no pickle found, doing it the hard way")
    index = {}
    htmlfiles = [x for x in listdir(path) if x[-5:] == ".html"]
    tq = tqdm(total=len(htmlfiles))
    chunks = _chunks(htmlfiles, threads)
    threadList = []
    for chunk in chunks:
        threadList.append(Thread(target=_index_extracts, args=(path, regex_string, chunk, tq, index)))
    for thread in threadList:
        thread.start()
    for thread in threadList:
        thread.join()
    tq.close()
    print("ok done indexing. gonna pickle this shit")
    pickle.dump(index, open(pickle_file, "wb"))
    for errorkey in index.keys():
        if errorkey.startswith("error"):
            print(errorkey, index[errorkey])

#https://stackoverflow.com/a/312464
def _chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

if __name__ == "__main__":
    index_extracts(r"C:\Users\Hussein\Desktop\Sitefinity API Doc", regex_string)
