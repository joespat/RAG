from llama_index.core import VectorStoreIndex, load_index_from_storage
from llama_index.core import StorageContext
from global_settings import INDEX_STORAGE

# Questo modulo crea e gestisce un indice vettoriale (VectorStoreIndex) per i nodi
# elaborati nella fase di acquisizione (modulo document_uploader.py).
# Un oggetto StorageContext è responsabile della gestione della persistenza dei dati,
# ovvero di salvare e caricare i dati dell'indice da una directory specificata.

# Creare un indice vettoriale è fondamentale per migliorare l'efficienza e
# l'efficacia delle operazioni di ricerca e recupero delle informazioni:

# Ricerca Semantica: Gli indici vettoriali permettono di eseguire ricerche basate
# sulla somiglianza semantica. Questo significa che consentono di trovare documenti o nodi
# che sono concettualmente simili alla query, anche se non contengono esattamente le stesse parole.

# Efficienza: Gli indici vettoriali sono ottimizzati per eseguire ricerche rapide su grandi quantità
# di dati. Utilizzando strutture dati specializzate, come gli alberi di ricerca o le tabelle hash,
# è possibile recuperare informazioni rilevanti in modo molto più veloce rispetto a una semplice scansione lineare dei nodi.

# Scalabilità: Quando si lavora con grandi dataset, un indice vettoriale permette di gestire
# e organizzare i dati in modo più efficiente. Questo è particolarmente utile in applicazioni
# di machine learning e intelligenza artificiale, dove la quantità di dati può essere enorme.

# Precisione: Gli indici vettoriali migliorano la precisione delle ricerche, poiché tengono
# conto delle relazioni semantiche tra i termini. Questo permette di ottenere risultati più
# pertinenti e accurati rispetto a una ricerca basata solo su parole chiave.

# In sintesi, mentre i nodi contengono le informazioni di base, l'indice vettoriale organizza
# e ottimizza queste informazioni per rendere le operazioni di ricerca e recupero più efficienti e precise.


def build_index(nodes):
    print("### build_index(nodes)")

    # Verifica se l'indice sia già stato precedentemente salvato su file, nella cartella INDEX_STORAGE
    try:
        # Cerca di caricare il contesto di archiviazione dalla cartella INDEX_STORAGE (file docstore.jason)

        # IndexStore: Questo componente memorizza le informazioni strutturali dell'indice, come la mappatura
        # dei documenti ai loro rispettivi nodi e altre informazioni di metadati. In pratica, IndexStore
        # tiene traccia di come i dati sono organizzati e indicizzati, permettendo di recuperare rapidamente
        # i nodi associati a un determinato documento o query.

        # VectorStore: Questo componente memorizza le rappresentazioni vettoriali (embedding) dei nodi.
        # Gli embedding sono vettori numerici che catturano il significato semantico del testo. VectorStore
        # consente di eseguire ricerche basate sulla somiglianza semantica, trovando nodi che sono concettualmente simili alla query.

        print("Provo a caricare lo storage context per l'indice")
        storage_context = StorageContext.from_defaults(
            persist_dir=INDEX_STORAGE
        )
        # Tenta di estrarre dal contesto di archiviazione un indice vettoriale esistente (con indice "vector"),
        # In tal modo si evitano i costi da sostenere per la sua ricostruzione.
        print("Provo a caricare l'indice dallo storage context")
        vector_index = load_index_from_storage(
            storage_context, index_id="vector"
        )
        print("Indice caricato dallo storage.")

        # Inserisce i nuovi nodi
        vector_index.insert_nodes(nodes)

        vector_index.set_index_id("vector")
        print("Indice aggiornato con i nuovi nodi.")

        # Salva l'indice aggiornato.
        storage_context.persist(persist_dir=INDEX_STORAGE)
        print("Indice salvato nello storage context.")
    except Exception as e:
        # Se il caricamento dell'indice vettoriale fallisce (ad esempio, se l'indice non esiste),
        # viene creato un nuovo contesto di archiviazione e un nuovo indice vettoriale utilizzando
        # i nodi forniti. L'ID dell'indice viene impostato su "vector" e il contesto di archiviazione
        # viene salvato nella directory di persistenza.
        print(f"{e}\nIndice non trovato: lo ricostruisco dai nodi.")
        storage_context = StorageContext.from_defaults()

        # Associazione del contesto di archiviazione: quando si crea un nuovo indice vettoriale
        # (VectorStoreIndex) e gli si passa storage_context, l'indice viene associato a quel contesto
        # di archiviazione. Questo significa che tutte le operazioni di memorizzazione e recupero
        # dei dati dell'indice verranno gestite da storage_context.
        vector_index = VectorStoreIndex(
            nodes, storage_context=storage_context
        )
        vector_index.set_index_id("vector")
        print("Nuovo indice creato.")

        # Salva il nuovo indice.
        storage_context.persist(persist_dir=INDEX_STORAGE)
        print("Nuovo indice salvato nello storage context.")

    # Restituisce l'indice vettoriale.
    return vector_index
