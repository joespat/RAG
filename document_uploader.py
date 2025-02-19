# ingest uploaded documents
from global_settings import STORAGE_PATH, CACHE_FILE
from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import SummaryExtractor
from llama_index.embeddings.openai import OpenAIEmbedding
# from llama_index.readers.file.docs.base import PDFReader


# Filtro per le frasi da escludere dall'ingestion
def rimuovi_frasi_indesiderate(testo, frasi_da_escludere):
    for frase in frasi_da_escludere:
        testo = testo.replace(frase, "")
    return testo


# ingest_documents() è responsabile della gestione del processo di acquisizione (ingestion):
# carica tutti i documenti leggibili, disponibili nella cartella STORAGE_PATH, ed esegue una
# pipeline di trasformazioni, che effettua la suddivisione del testo in blocchi più piccoli,
# un'estrazione di un breve sommario e l'embedding, restituendo infine i nodi elaborati .
def ingest_documents():
    print("### ingest_documents()")
    # Crea un lettore di directory di tipo SimpleDirectoryReader, che
    # si adatta automaticamente a differenti tipi di files.
    # Utilizza i nomi dei file come identificatori unici per i documenti creati.
    reader = SimpleDirectoryReader(STORAGE_PATH, filename_as_id=True)

    # Carica il contenuto della directory in in una lista di oggetti Document di Llamaindex.
    # La classe Document è un container con diversi attributi, fra cui:
    # text: contiene il contenuto testuale del documento
    # metadata: informazioni addizionali, come il nome del file.
    # id: identificativo univoco per ciascun documento.
    documents = reader.load_data()
    for doc in documents:
        print(doc.id_)

    # Controlla se esiste un file di cache per la pipeline di acquisizione.
    # Se il file di cache esiste, viene utilizzato; altrimenti, viene eseguita l'elaborazione senza cache.
    try:
        cached_hashes = IngestionCache.from_persist_path(CACHE_FILE)
        print("Trovato il file di cache della Pipeline di acquisizione. Continuo con la cache...")
    except:
        cached_hashes = ""
        print("File di cache della Pipeline di acquisizione non trovato. Continuo senza cache...")

    # Definisce la lista delle frasi da non acquisire, utilizzata dal filtro
    frasi_da_escludere = [
        "Ricevi una favola al giorno gratuitamente: iscriviti su https://365favole.com/",
        "365favole.com",
        "3 6 5 f a v o l e",
        "3 6 5 f a v o l e . c o m",
        "i s c r i v i t i\ns u\nh t t p s : / / 3 6 5 f a v o l e . c o m ",
        "R i c e v i\nu n a\nf a v o l a\na l\ng i o r n o\ng r a t u i t a m e n t e"
    ]

    # Applica il filtro ai documenti
    for doc in documents:
        doc.text = rimuovi_frasi_indesiderate(doc.text, frasi_da_escludere)

    # Definisce la pipeline di acquisizione.
    # Se gli hash nel file di cache corrispondono a quelli dei file da acquisire, non è necessaria
    # alcuna elaborazione: i valori verranno caricati direttamente dalla cache.
    pipeline = IngestionPipeline(
        transformations=[
            # 1) Suddivide il testo in blocchi più piccoli (chunk) basati su token (parole, segni di punteggiatura, spazi).
            # TokenTextSplitter suddivide il testo rispettando i limiti della frase.
            # Questi blocchi vengono poi utilizzati per creare nodi. Ogni nodo rappresenta un'unità
            # di informazione più complessa, che può contenere uno o più blocchi di testo.
            # I nodi possono rappresentare concetti, entità o altre strutture semantiche all'interno di un testo.
            # Ad esempio, un nodo potrebbe rappresentare una frase, un paragrafo o un'entità specifica come un nome proprio.
            # I nodi sono utilizzati per organizzare e strutturare le informazioni in modo più significativo e possono
            # includere metadati aggiuntivi, come riassunti o embedding. Sono adatti per ulteriori elaborazioni con un LLM.
            TokenTextSplitter(
                # dimensione massima di ciascun blocco (chunk) in termini di numero di token.
                chunk_size=1024,  # default

                # numero di token che si sovrappongono tra blocchi consecutivi. Aiuta a mantenere la continuità
                # del contesto tra i blocchi, migliorando la coerenza delle risposte generate dal modello.
                chunk_overlap=20  # default
            ),

            # 2) Generazione, tramite un estrattore di metadati, di un breve riassunto per ciascun
            # nodo, basato sul contenuto del nodo stesso. Ciò è utile per fornire una panoramica
            # rapida e concisa del contenuto del nodo senza dover leggere l'intero testo.
            # I riassunti generati possono essere utilizzati durante la fase di recupero (retrieval)
            # in un'architettura RAG (Retrieval-Augmented Generation). Invece di dover elaborare l'intero
            # contenuto dei documenti, il sistema può utilizzare i riassunti per determinare rapidamente
            # quali nodi sono rilevanti per una query specifica.
            SummaryExtractor(
                summaries=['self'],  # riassunto basato sul nodo stesso
                language='it'  # specifica al modello llm quale lingua utilizzare
            ),

            # 3) Embedding.
            # Dopo che il TokenTextSplitter ha suddiviso i documenti in blocchi di testo (chunk)
            # e questi sono stati trasformati in nodi, OpenAIEmbedding genera rappresentazioni
            # vettoriali (embedding) per ciascun nodo. Questi embedding catturano il significato
            # semantico del testo contenuto nei nodi e li rappresentano come vettori numerici.
            # in un sistema RAG (Retrieval-Augmented Generation), gli embedding possono essere
            # utilizzati per trovare nodi rilevanti per una query specifica.
            OpenAIEmbedding()
        ],

        # La cache viene utilizzata per evitare di ripetere elaborazioni costose (tokenizzazione,
        # generazione di embedding, riassunto del testo) su dati che non sono cambiati.
        # Se gli hash dei documenti nella cache corrispondono agli hash dei documenti attuali,
        # la pipeline può utilizzare i risultati memorizzati nella cache invece di rielaborare i documenti.
        # Se ci sono nuovi documenti o documenti modificati, la pipeline eseguirà l'elaborazione
        # solo su quei documenti e aggiornerà la cache di conseguenza.
        cache=cached_hashes
    )

    # Elabora i documenti utilizzando la pipeline di acquisizione
    nodes = pipeline.run(documents=documents)

    # Salva su file i dati della Pipeline di acquisizione
    pipeline.cache.persist(CACHE_FILE)

    # Restituisce i nodi elaborati
    return nodes


if __name__ == "__main__":
    embedded_nodes = ingest_documents()

    for node in embedded_nodes:
        print("--------------------")
        print(node.metadata['section_summary'])
