from os import listdir
from re import search
from os.path import join, isfile
from tqdm import tqdm
from threading import Thread
from traceback import format_exc
from logging import getLogger
import pickle

index = None
regex_string = '<meta name="Microsoft.Help.Id" content="(.*?)" />'
threads = 8
logger = getLogger("MshcHost")


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
    except Exception:
        ind["error" + path] = Exception(format_exc())


def initialize(path):
    global index, threads, logger
    logger.info("Indexing...")
    if index is not None:
        raise RuntimeError("Index was already initialized.")
    pickle_file = join(path, "index.pickle")
    if isfile(pickle_file):
        index = pickle.load(open(pickle_file, "rb"))
        logger.info("Found pickled index. Returning.")
        return
    logger.info("No pickled index found.")
    index = {}
    htmlfiles = [x for x in listdir(path) if x[-5:] == ".html"]
    tq = tqdm(total=len(htmlfiles))
    chunks = _chunks(htmlfiles, len(htmlfiles) // threads)
    threadList = []
    for chunk in chunks:
        threadList.append(Thread(target=_index_extracts, args=(
            path, regex_string, chunk, tq, index)))
    for thread in threadList:
        thread.start()
    for thread in threadList:
        thread.join()
    tq.close()
    logger.info("Indexing finished. Pickling index for later.")
    pickle.dump(index, open(pickle_file, "wb"))
    if any(filter(lambda x: x.startswith("error"), index.keys())):
        logger.warn("Logging errors generated from indexing.")
        for errorkey in index.keys():
            if errorkey.startswith("error"):
                logger.warn(
                    f"Error Key: '{errorkey}' \
                    Error Value: '{index[errorkey]}'")


# https://stackoverflow.com/a/312464
def _chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
