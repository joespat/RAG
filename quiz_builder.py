from llama_index.core import load_index_from_storage, StorageContext
from llama_index.program.evaporate.df import DFRowsProgram
from llama_index.program.openai import OpenAIPydanticProgram
from global_settings import INDEX_STORAGE, QUIZ_SIZE, QUIZ_FILE
import pandas as pd

# Crea un quiz basato sui file caricati.


def build_quiz(topic):
    print("### build_quiz(topic)")

    # Crea un DataFrame vuoto con colonne specifiche per le domande del quiz, le opzioni
    # di risposta, la risposta corretta e la spiegazione (Rationale).
    # L'uso di un DataFrame Pandas agevola la gestione dei dati del quiz.
    df = pd.DataFrame(
        {
            "Question_no": pd.Series(dtype="int"),
            "Question_text": pd.Series(dtype="str"),
            "Option1": pd.Series(dtype="str"),
            "Option2": pd.Series(dtype="str"),
            "Option3": pd.Series(dtype="str"),
            "Option4": pd.Series(dtype="str"),
            "Correct_answer": pd.Series(dtype="str"),
            "Rationale": pd.Series(dtype="str"),
        }
    )

    # Carica il contesto di archiviazione e l'indice vettoriale "vector"
    # dalla directory di persistenza specificata (INDEX_STORAGE)
    storage_context = StorageContext.from_defaults(persist_dir=INDEX_STORAGE)
    vector_index = load_index_from_storage(storage_context, index_id="vector")

    # Inizializza l'estrattore DataFrame, utilizzando i valori predefiniti.

    # DFRowsProgram è un parser che analizza e gestisce le righe del DataFrame,
    # interagendo con i dati strutturati nel DataFrame per generare le domande del quiz
    # sulla base dei dati forniti.
    # Al parametro pydantic_program_cls viene assegnata la classe del programma Pydantic da utilizzare:
    # OpenAIPydanticProgram è una classe che definisce in che modo il programma interagisce con
    # i modelli di OpenAI per generare o elaborare i dati.
    # L'estrattore DataFrame Pydantic è progettato per estrarre DataFrame tabulari dal testo grezzo.
    df_rows_program = DFRowsProgram.from_defaults(
        pydantic_program_cls=OpenAIPydanticProgram, df=df
    )

    # Definisce il motore di query a cui passare il prompt (query_string) che genererà le domande del quiz.
    # vector_index.as_query_engine() trasforma l'indice vettoriale in un motore di query.
    # Un motore di query è un'interfaccia che permette di eseguire ricerche e recuperare informazioni
    # dall'indice vettoriale in modo efficiente, partendo da query espresse in linguaggio naturale.
    # Le ricerche sono basate sulla somiglianza semantica e consentono di ottenere risultati rilevanti
    # in base alle rappresentazioni vettoriali dei nodi.
    query_engine = vector_index.as_query_engine()

    query_string = (f"Create {QUIZ_SIZE} different quiz questions relevant for testing "
                    "a candidate's knowledge about {topic}. You must use Italian language. "
                    "Each question will have 4 answer options. Each question will have different answers. "
                    "No more than 3 questions should be specific to the provided text: "
                    "in this case they should concern characters and stories. "
                    "Questions and answers must not refer to websites or URL. "
                    "For each question, provide also the correct answer and the answer rationale. "
                    "Only one answer option should be correct.")

    # Il metodo query del query engine prende query_string come input e la confronta
    # con i vettori nel vector_index per trovare i contenuti più rilevanti, utilizzando
    # la similarità. Il query engine quindi produce un prompt esteso, combinando query_string
    # con il contesto estratto dal vector_index. Questo prompt viene poi inoltrato al LLM
    # per ottenere una risposta accurata e contestualizzata
    response = query_engine.query(query_string)

    # La risposta viene elaborata da DFRowsProgram che la converte
    # in un formato DataFrame strutturato.
    result_obj = df_rows_program(input_str=response)
    # Crea un nuovo DataFrame con le domande del quiz generate dalla query.
    new_df = result_obj.to_df(existing_df=df)

    # Salva il DataFrame contenente le domande del quiz in un file .csv
    # (QUIZ_FILE) e restituisce il nuovo DataFrame.
    new_df.to_csv(QUIZ_FILE, index=False)
    return new_df
