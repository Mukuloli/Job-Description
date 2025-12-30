import os
from dotenv import load_dotenv
from utils.pdf_generator import create_job_description_pdf
from utils.gemini_generator import generate_with_gemini
load_dotenv()
def interactive_mode():

    job_prompt = input("Enter job description prompt: ").strip()
    if not job_prompt: 
        return
    
    output_file = input("Output PDF filename (default: job_description.pdf): ").strip()
    if not output_file: 
        output_file = "job_description.pdf"
    if not output_file.lower().endswith('.pdf'): 
        output_file += '.pdf'
    
    logo_path = input("Logo path (optional, press Enter to skip): ").strip()
    if logo_path and not os.path.exists(logo_path): 
        logo_path = None
    
    try:
        job_data = generate_with_gemini(job_prompt)
        create_job_description_pdf(output_file, job_data, logo_path)
        print(f"\n🎉 Success! Generated PDF: {output_file}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    interactive_mode()

if __name__ == "__main__":
    main()

