import streamlit as st
from llama_index.core import load_index_from_storage
from llama_index.core import StorageContext
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.storage.chat_store import SimpleChatStore
from global_settings import INDEX_STORAGE, CONVERSATION_FILE

# Questo modulo gestisce il pannello per la chat, fornendo le risposte alle domande degli utenti.
# Il "motore di conversazione" è in grado di comprendere l'argomento, è consapevole del contesto attuale e
# tiene traccia dell'intera interazione con lo studente, salvandola su file per poterla riprendere fra sessioni
# differenti avviate dallo stesso utente.

# Il modulo espone 3 funzioni (utilizzate dal modulo training_UI.py) per creare e gestire
# un chatbot utilizzando un contesto di archiviazione, un motore di query e un agente di OpenAI:
# - load_chat_store
# - initialize_chatbot
# - chat_interface


# Questa funzione è responsabile del recupero della conversazione del chatbot dalle
# sessioni precedenti. Viene utilizzata una chiave chat_store_key="0" generica: in
# uno scenario multiutente, questa chiave potrebbe essere utilizzata per archiviare
# conversazioni per diversi utenti nello stesso archivio chat.
# load_chat_store crea (o recupera) un'istanza di SimpleChatStore e la restituisce.
# SimpleChatStore è una classe progettata per memorizzare una conversazione.
def load_chat_store():
    print("### load_chat_store()")
    # Tenta di recuperare la cronologia delle conversazioni dal file di archiviazione locale.
    # Se il file non esiste, viene creato un nuovo chat_store vuoto.
    try:
        chat_store = SimpleChatStore.from_persist_path(CONVERSATION_FILE)
    except FileNotFoundError:
        chat_store = SimpleChatStore()
    return chat_store


# Questa funzione è responsabile della visualizzazione dell'intera cronologia delle
# conversazioni nell'interfaccia Streamlit. Richiede un archivio di chat e un contenitore
# Streamlit come argomenti: estrae tutti i messaggi dall'archivio utilizzando get_messages()
# e li visualizza nel container Streamlit, aggiungendo automaticamente l'icona corrispondente
# a ciascun ruolo (utente o assistente).
def display_messages(chat_store, container):
    print("### display_messages()")
    with container:
        for message in chat_store.get_messages(key="0"):
            if message.role != "tool" and message.content != None:
                with st.chat_message(message.role):
                    st.markdown(message.content)


# Inizializza l'agent OpenAIAgent e lo restituisce.
def initialize_chatbot(user_name, study_subject,
                       chat_store, container, context):
    print("### initialize_chatbot(...)")

    # Utilizzando chat_store, crea un buffer di memoria per la chat (ChatMemoryBuffer)
    # con un limite di 3000 token.
    memory = ChatMemoryBuffer.from_defaults(
        token_limit=3000,
        chat_store=chat_store,
        chat_store_key="0"
    )
    # Carica il contesto di archiviazione dalla cartella INDEX_STORAGE
    storage_context = StorageContext.from_defaults(
        persist_dir=INDEX_STORAGE
    )
    # Carica l'indice vettoriale dallo StorageContext.
    vector_index = load_index_from_storage(
        storage_context, index_id="vector"
    )
    # Crea un motore di query dall'indice caricato.
    # Il motore di query provvederà al recupero dei 3 risultati più simili.
    study_materials_engine = vector_index.as_query_engine(similarity_top_k=3)

    # Crea un Tool (QueryEngineTool), che incapsula il motore di query creato in
    # precedenza e fornisce un accesso in sola lettura ai dati.
    # Viene fornita, nei suoi metadati, una descrizione dettagliata dello strumento,
    # che ne specifica lo scopo, in modo che l'agent comprenda quando utilizzarlo
    # (in caso abbia a disposizione più tools): il tool fornisce informazioni
    # "ufficiali" sui materiali di studio (study_subject) e richiede una domanda
    #  in testo semplice come input.
    study_materials_tool = QueryEngineTool(
        query_engine=study_materials_engine,
        metadata=ToolMetadata(
            name="study_materials",
            description=(
                f"Fornisce informazioni ufficiali su "
                f"{study_subject}. Richiede una domanda dettagliata in "
                f"testo semplice come input."
            ),
        )
    )
    # Inizializza un agente di OpenAI (OpenAIAgent) con il tool precedentemente creato,
    # la memoria per la chat e un prompt di sistema.
    # Il prompt viene utilizzato per fornire al LLM informazioni di base per contestualizzare
    # le sue risposte, garantire che siano pertinenti all’argomento di discussione attuale
    # (study_subject) e alle esigenze di approfondimento dell’utente (context).
    agent = OpenAIAgent.from_tools(
        tools=[study_materials_tool],
        memory=memory,
        system_prompt=(
            f"Ti chiami Learny, sei un assistente virtuale e parli in italiano. Il tuo "
            f"scopo è di aiutare {user_name} a studiare e "
            f"comprendere meglio l'argomento: "
            f"{study_subject}. Stiamo discutendo in "
            f"particolare il seguente contenuto: {context}"
        )
    )
    # Visualizza i messaggi memorizzati nel chat_store (cioè la conversazione).
    display_messages(chat_store, container)
    return agent


# Implementa la conversazione in corso prendendo l'input dell'utente e
# generando una risposta dall'agent. Salva la conversazione dopo ciascuna
# interazione. Se l'utente termina la sessione corrente, la conversazione
# riprenderà da quel punto.
def chat_interface(agent, chat_store, container):
    print("### chat_interface(...)")
    # visualizza un widget di input della chat utilizzando il metodo chat_input() di Streamlit.
    prompt = st.chat_input("Scrivi la tua domanda:")
    if prompt:
        with container:
            # Visualizza il prompt nella chat con il ruolo di "assistant".
            with st.chat_message("user"):
                st.markdown(prompt)
            # Invoca il metodo chat() dell'agent per generare una risposta alla domanda dell'utente.
            response = str(agent.chat(prompt))
            # Visualizza la risposta nella chat con il ruolo di "assistant".
            with st.chat_message("assistant"):
                st.markdown(response)
        print("### chat_interface -> chat_store.persist(CONVERSATION_FILE)")
        chat_store.persist(CONVERSATION_FILE)
