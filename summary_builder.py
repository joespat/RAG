from global_settings import STORAGE_PATH, SUMMARY_STORAGE
from fpdf import FPDF
import os


# Crea un sommario basato sui file caricati.


def build_summary(summary_text):
    print("### build_summary()")

    # Creazione del PDF di Riassunto
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Riassunto del Documento', 0, 1, 'C')

        def chapter_title(self, title):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, title.encode(
                'latin-1', 'replace').decode('latin-1'), 0, 1, 'L')
            self.ln(10)

        def chapter_body(self, body):
            self.set_font('Arial', '', 12)
            self.multi_cell(0, 10, body.encode(
                'latin-1', 'replace').decode('latin-1'))
            self.ln()

    # Crea la directory se non esiste
    output_dir = SUMMARY_STORAGE
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Crea il PDF
    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title('Riassunto del Documento')
    pdf.chapter_body(summary_text)

    # Salva il PDF
    pdf_output_path = os.path.join(output_dir, 'sommario.pdf')
    # Imposta la modalità 'F' per salvare il file
    pdf.output(pdf_output_path, 'F')

    # Stampa conferma
    print(
        f"Il riassunto è stato generato e salvato come PDF in: {pdf_output_path}")
