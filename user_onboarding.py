import streamlit as st
import os
from session_functions import save_session
from global_settings import STORAGE_PATH
from document_uploader import ingest_documents
from index_builder import build_index
from summary_builder import build_summary

# Chiede ad un nuovo studente l'argomento di studio, acquisisce i materiali e crea l'indice.
# Aggiorna alcune chiavi di sessione.


def user_onboarding():
    print("### user_onboarding()")
    user_name = st.text_input('Come ti chiami?')
    if not user_name:
        return

    st.session_state['user_name'] = user_name
    st.write(f"Ciao {user_name}. Piacere di conoscerti!")
    study_subject = st.text_input('Che argomento vorresti studiare?')

    if not study_subject:
        return

    st.session_state['study_subject'] = study_subject
    st.write(f"Va bene {user_name}, concentriamoci su: '{study_subject}'.")

    if study_subject:
        st.write("Vuoi caricare dei materiali di studio?")
        uploaded_files = st.file_uploader(
            "Scegli i tuoi files:", accept_multiple_files=True)
        finish_upload = st.button('ESEGUI L\'UPLOAD')

        if finish_upload and uploaded_files:
            saved_file_names = []
            for uploaded_file in uploaded_files:
                file_path = os.path.join(STORAGE_PATH, uploaded_file.name)

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_file_names.append(uploaded_file.name)
                st.write(f"Hai caricato {uploaded_file.name}")

            st.session_state['uploaded_files'] = saved_file_names
            st.session_state['finish_upload'] = True
            st.info('Caricamento dei files...')

    if 'finish_upload' in st.session_state:
        # Avvia l'acquisizione dei materiali di studio.
        nodes = ingest_documents()

        # Prepara un sommario e lo salva in u file Pdf
        st.info('Materiali caricati. Preparo il sommario...')
        summary_text = ''
        for node in nodes:
            summary = node.metadata['section_summary']
            summary_text += summary + '\n\n'

        build_summary(summary_text)

        st.info('Sommario generato. Preparo l\'indice...')
        # Avvia l'indicizzazione.
        vector_index = build_index(nodes)
        st.info('Indicizzazione completata.')
        # Attende che l'utente clicchi sul pulsante 'Procedi' per proseguire.
        proceed_button = st.button('Procedi')

        if proceed_button:
            save_session(st.session_state)
            st.session_state['show_quiz'] = True
            st.rerun()
