from global_settings import SESSION_FILE, STORAGE_PATH, CONVERSATION_FILE
import yaml
import os


# Questo modulo contiene funzioni che gestiscono il salvataggio, il caricamento
# e l'eliminazione dello stato della sessione di un utente. YAML è un formato
# per la serializzazione. È leggibile dall'uomo e indipendente dalla piattaforma,
# adatto per l'archiviazione di strutture dati semplici come lo stato della sessione.

def save_session(state):
    print("### save_session()")
    state_to_save = {key: value for key, value in state.items()}
    with open(SESSION_FILE, 'w') as file:
        yaml.dump(state_to_save, file)


def load_session(state):
    print("### load_session()")
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as file:
            try:
                loaded_state = yaml.safe_load(file) or {}
                for key, value in loaded_state.items():
                    state[key] = value
                return True
            except yaml.YAMLError as e:
                return False
    return False


def delete_session(state):
    print("### delete_session()")
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    if os.path.exists(CONVERSATION_FILE):
        os.remove(CONVERSATION_FILE)
    for filename in os.listdir(STORAGE_PATH):
        file_path = os.path.join(STORAGE_PATH, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.remove(file_path)
    for key in list(state.keys()):
        del state[key]
