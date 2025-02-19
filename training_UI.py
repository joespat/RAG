import streamlit as st
from conversation_engine import initialize_chatbot, chat_interface, load_chat_store
from quiz_UI import show_quiz
from quiz_builder import build_quiz

# Genera con streamlit un'interfaccia con 2 colonne: una per il quiz, l'altra per il chatbot


def show_training_UI(user_name, study_subject):
    print("### show_training_UI(user_name, study_subject)")
    # Mostra il titolo nella barra laterale
    st.sidebar.markdown("## " + "Allenati con un quiz o studia con il chatbot")

    # crea due colonne con una proporzione di 0.4 e 0.6
    col1, col2 = st.columns([0.4, 0.6], gap="medium")
    # Mostra il chatbot nella prima colonna
    with col1:
        # Crea un'intestazione per il chatbot e visualizza un messaggio di
        # benvenuto personalizzato per l'utente, indicando l'argomento di studio.
        st.header("💬 Learny chatbot")
        st.success(f"Ciao {user_name}. Sono qui per risponderti su: '{
            study_subject}'")

        # Crea un'istanza di SimpleChatStore, per memorizzare i messaggi della chat.
        chat_store = load_chat_store()
        # crea un contenitore con un'altezza di 550 pixel per visualizzare i messaggi della chat.
        container = st.container(height=550)
        # non utilizzato: volendo, si potrebbe precisare meglio il contesto per l'agent
        context = ""
        # Inizializza il chatbot
        agent = initialize_chatbot(
            user_name, study_subject, chat_store, container, context)
        # Gestisce l'interfaccia della chat
        chat_interface(agent, chat_store, container)

    # Se lo studente non ha ancora optato per lo svolgimento del quiz,
    # mostra il pulsante "Genera un quiz".
    if not 'quiz_running' in st.session_state or not st.session_state['quiz_running']:
        if st.sidebar.button("Genera un quiz"):
            # Genera il quiz e lo mostra nella seconda colonna
            with col2:
                st.session_state['quiz_running'] = True
                quiz = build_quiz(st.session_state['study_subject'])
                show_quiz(st.session_state['study_subject'])
    else:
        # Quiz già generato: lo mostra nella seconda colonna
        with col2:
            show_quiz(st.session_state['study_subject'])
