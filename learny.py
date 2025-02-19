from user_onboarding import user_onboarding
from session_functions import load_session, delete_session
from training_UI import show_training_UI
import streamlit as st
import os
from dotenv import load_dotenv

# Carica la chiave per OpenAI dalle variabili d'ambiente
load_dotenv()


# Questo codice è responsabile della gestione dell'esecuzione dei vari componenti
# che compongono l'applicazione. Funziona come hub centrale, instradando i nuovi
# utenti verso il processo di onboarding, e gestendo la presentazione di quiz e
# della chat in base alle interazioni dell'utente e ai dati della sessione.
def main():
    print("\n### main()")
    st.set_page_config(layout="wide")

    # Carica l'immagine dal file
    with open("Learny.png", "rb") as image_file:
        icona = image_file.read()
        # Aggiunge l'icona alla barra laterale
        st.sidebar.image(icona, width=260)

    st.sidebar.title('Learny')
    st.sidebar.markdown(
        '### Assistente Virtuale per lo studio')

    # Verifica la presenza di determinate chiavi nella sessione di Streamlit (st.session_state).
    # Queste chiavi consentono la gestione dell'interfaccia in base allo stato dell'applicazione
    # e fungono da archiviazione persistente tra successive esecuzioni dell'app.
    if 'OPENAI_API_KEY' not in st.session_state or not st.session_state['OPENAI_API_KEY']:
        api_key = os.environ['OPENAI_API_KEY']
        st.session_state['OPENAI_API_KEY'] = api_key

    # Lo studente ha già indicato l'argomento di studio, caricato i materiali, e scelto di fare un quiz
    if 'show_quiz' in st.session_state and st.session_state['show_quiz']:
        show_training_UI(
            st.session_state['user_name'], st.session_state['study_subject'])
    elif not load_session(st.session_state):
        # Lo studente si presenta per la prima volta all'applicazione:
        # viene mostrata la schermata per l'inserimento del nome, la
        # scelta dell'argomento e il caricamento dei materiali di studio
        user_onboarding()
    else:
        # Per studenti che si sono già presentati all'applicazione, mostra le opzioni
        # (due pulsanti) per riprendere la sessione precedente o avviarne una nuova.
        st.write(f"Bentornato/a {st.session_state['user_name']}!")
        col1, col2 = st.columns(2)
        if col1.button(f"Riprendi a studiare: {st.session_state['study_subject']}"):
            st.session_state['show_quiz'] = True
            st.rerun()
        if col2.button('Avvia una nuova sessione'):
            delete_session(st.session_state)
            st.rerun()


if __name__ == "__main__":
    main()
