import streamlit as st
import pandas as pd
from global_settings import QUIZ_FILE

# Questo modulo gestisce l'interfaccia utente per lo svolgimento del quiz.


# Evidenzia le risposte corrette/errate
def evidenzia_risposte(df, answers):
    for index, row in df.iterrows():
        question = row["Question_text"]
        options = [row["Option1"], row["Option2"],
                   row["Option3"], row["Option4"]]
        correct_answer = row["Correct_answer"]
        user_answer = answers.get(row["Question_no"], None)
        spiegazione = row["Rationale"]

        # st.markdown(f"\n**{question}**")
        st.markdown(f"<b><h3>{question}</h3></b>", unsafe_allow_html=True)
        # st.markdown(f"**{spiegazione}**")
        st.markdown(f"<i>{spiegazione}</i>", unsafe_allow_html=True)
        for option in options:
            if option in correct_answer:
                st.markdown(f"- **{option}** :white_check_mark:")
            elif option == user_answer:
                st.markdown(f"- {option} :x:")
            else:
                st.markdown(f"- {option}")


# Mostra l'interfaccia per il quiz
def show_quiz(topic):
    print("### show_quiz()")
    st.markdown(f"### Verifichiamo le tue conoscenze su {topic} con un quiz:")
    # Legge il file CSV contenente le domande del quiz e le risposte corrette, e lo carica nel DataFrame df
    df = pd.read_csv(QUIZ_FILE)

    # Inizializza un dizionario vuoto per memorizzare le risposte degli utenti.
    answers = {}

    # Itera attraverso ogni riga del DataFrame
    for index, row in df.iterrows():
        # Estrae il testo della domanda dalla colonna "Question_text".
        question = row["Question_text"]
        # Estrae le opzioni di risposta dalle colonne "Option1", "Option2", "Option3" e "Option4".
        options = [row["Option1"], row["Option2"],
                   row["Option3"], row["Option4"]]
        # Crea un radio-button per ogni domanda, utilizzando il testo della domanda e le opzioni estratte.
        # La risposta selezionata dall'utente viene memorizzata nel dizionario answers
        # con la chiave corrispondente al numero della domanda.
        answers[row["Question_no"]] = st.radio(
            question, options, index=None, key=row["Question_no"])

    # Verifica se tutte le domande hanno una risposta selezionata
    all_answered = all(answer is not None for answer in answers.values())
    if all_answered:
        print("All answered")
        if st.button("INVIA RISPOSTE"):
            score = 0
            for q_no in answers:
                user_answer_text = answers[q_no]
                print(f"Risposta fornita: {user_answer_text}")
                # Estrae la risposta corretta dal DataFrame.
                # Utilizza loc per filtrare il DataFrame in base al numero della domanda e seleziona
                # la colonna "Correct_answer". iloc[0] viene utilizzato per ottenere il primo
                # (e presumibilmente unico) valore corrispondente.
                correct_answer_text = df.loc[df['Question_no']
                                             == q_no, "Correct_answer"].iloc[0]
                print(f"Risposta corretta: {correct_answer_text}")
                if user_answer_text in correct_answer_text:
                    score += 1
                    print("Risposta azzeccata!")
                    print("-------------------")
                else:
                    print("Risposta errata!")
                    print("-------------------")

            max_score = len(df)
            third_of_max = max_score / 3
            level = ""
            if score <= third_of_max:
                level = "Base"
            elif third_of_max < score <= 2 * third_of_max:
                level = "Intermedio"
            else:
                level = "Avanzato"

            st.write(f"Il tuo punteggio è: {score}/{max_score}")
            st.write(f"Il tuo livello di conoscenza è: {level}")
            st.session_state['quiz_running'] = False

            # Evidenzia le risposte corrette
            evidenzia_risposte(df, answers)
            return level, score
