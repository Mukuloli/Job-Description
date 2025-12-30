import json
import os
import google.generativeai as genai

def generate_with_gemini(prompt, api_key=None):
    if not api_key:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in your .env file or pass --api-key parameter")
    
    genai.configure(api_key=api_key)
    model = None
    for model_name in ['gemini-1.5-flash']:
        try:
            model = genai.GenerativeModel(model_name)
            break
        except: continue
    
    if not model:
        raise Exception("No available Gemini models found. Please check your API key and available models.")
    
    enhanced_prompt = f"""You are a professional HR specialist who writes job descriptions with accuracy and clarity for ALL industries.
Create a comprehensive job description based STRICTLY on this user prompt: "{prompt}"
CRITICAL INSTRUCTION: DO NOT include any placeholder information, fake details, or generic website references in the output. If specific company information is not provided in the prompt, leave those fields empty.
Generate a detailed JSON response with this structure (keep fields flat, avoid deep nesting). The company_overview must appear right after experience_required:

{{
    "company_name": "{{Extract company name from prompt; if not provided return ''}}",
    "job_title": "{{Extract job title from prompt; if not provided, infer from skills/role mentioned}}",
    "job_code": "{{Generate only if mentioned in prompt, otherwise return ''}}",
    "location": "{{Extract location from prompt; if not mentioned return ''}}",
    "department": "{{Extract department from prompt; if not mentioned return ''}}",
    "team": "{{Extract team info from prompt; if not mentioned return ''}}",
    "reporting_to": "{{Extract reporting structure from prompt; if not mentioned return ''}}",
    "employment_type": "{{Extract employment type from prompt; if not mentioned return ''}}",
    "experience_required": "{{Extract exact experience from prompt example Fresher, Entry Level, Mid Level, Senior Level,Trainee; if not mentioned return ''}}",
    "office_timings": "{{Extract office hours, work timings, shift timings from prompt; if not mentioned return ''}}",
    "working_days": "{{Extract working days, work week schedule from prompt; if not mentioned return ''}}",
    "industry_type": "{{Identify industry: IT/Technology, Healthcare/Medical, Manufacturing, Finance/Banking, Education, Retail, Construction, Government, Non-Profit, Other}}",
    
    "company_overview": "{{If company_name is provided, generate a tailored overview. If not, return a generic 50-word overview matching the industry type. Do not display this instruction in the output. Do not provide fake or incorrect information about the company}}",

    "role_overview": "{{Generate comprehensive 100-120 word overview based on role responsibilities and industry context mentioned in prompt}}",
    "salary_range": "{{Extract salary from the prompt exactly as written; do not use any currency symbols; if the user enters '3.5 LPA', keep it as '3.5 LPA' (do not convert to 350000); if salary is not mentioned, return ''}}"

    "key_responsibilities": [
        "Primary Role Focus: {{30-50 word detailed description of main responsibility related to core function mentioned in prompt, including specific tasks and expected outcomes}}",
        "{{Industry-Specific }}: {{30-50 word explanation of key industry-specific duties, processes, and deliverables}}",
        "Quality & Standards Compliance: {{30-50 word description covering industry standards, quality control, safety protocols, and regulatory compliance}}",
        "{{Process/Project Management}}: {{30-50 word explanation of workflow management, project coordination, and performance monitoring}}",
        "Documentation & Reporting: {{30-50 word description of record keeping, reporting standards, data management, and communication protocols}}",
        "Team Collaboration: {{30-50 word explanation of cross-functional collaboration, stakeholder communication, and team coordination}}"
    ],
    
    "technical_requirements": [
        "{{Core Skill 1 from prompt}}: {{Detailed explanation of proficiency level, tools, equipment, software, or techniques required}}",
        "{{Core Skill 2 from prompt}}: {{Comprehensive description of expertise level, related knowledge, and practical application experience}}",
        "{{Core Skill 3 from prompt}}: {{Detailed explanation of mastery level, specialized knowledge, and operational skills}}",
        "{{Additional relevant skill/certification}}: {{Description of supporting professional knowledge, licenses, or certifications}}"
    ],
    

    "who_you_are": [
        "Professional Excellence: {{30-50 word description of professional attitude, work ethic, reliability, and commitment with industry-specific examples}}",
        "Industry Expertise: {{30-50 word explanation of domain knowledge, learning ability, innovation mindset, and adaptation skills}}",
        "Communication Skills: {{30-50 word description of interpersonal abilities, client/patient interaction, and stakeholder management}}",
        "Problem-Solving Mindset: {{30-50 word explanation of analytical thinking, troubleshooting methodology, and solution-oriented approach}}"
    ],
    
    "experience_skills": [  
        "Professional Experience: {{50-70 word description of required experience level, role progression, achievements, and relevant background based on user prompt}}",
        "Industry Expertise: {{30-50 word explanation of domain-specific knowledge, practical applications, and specialized skills mentioned in prompt}}",
        "Functional Knowledge: {{30-40 word description of operational expertise, cross-functional experience, and process understanding}}"
    ],
    
    "qualifications": [
        "Educational Background: {{30-50 word description of academic requirements, relevant degrees, diplomas, or educational qualifications}}",
        "Professional Experience: {{30-50 word explanation of work experience requirements and career progression based on user prompt}}",
        "{{Industry-Specific Requirements}}: {{30-50 word description of licenses, certifications, registrations, or specialized qualifications}}"
    ],
    
    "preferred_qualifications": [
        "Advanced {{Industry}} Skills: {{30-50 word description of additional specialized knowledge and advanced competencies}}",
        "Professional Certifications: {{30-50 word explanation of industry certifications, continuing education, and professional development}}",
        "Leadership Experience: {{30-50 word description of supervisory experience, team management, and project leadership capabilities}}"
    ],
    
    "what_we_offer": [
        "Career Growth Opportunities: {{40-50 word description of advancement paths, skill development, training programs, and learning opportunities}}",
        "{{Industry-Appropriate}} Work Environment: {{40-50 word explanation of workplace culture, modern facilities, safety standards, and support systems}}",
        "Competitive Compensation: {{40-50 word description of salary structure, bonuses, incentives, and performance-based rewards}}",
        "Work-Life Balance: {{40-50 word explanation of flexible arrangements, leave policies, and employee wellness programs}}",
        "Professional Development: {{40-50 word description of training opportunities, skill enhancement, and career advancement support}}"
    ],
    
    "benefits": [
        "Health & Wellness Coverage: {{30-55 word description of medical insurance, health benefits, wellness programs, and healthcare support}}",
        "Learning & Development Support: {{30-55 word explanation of training allowances, certification support, and professional growth programs}}",
        "{{Work Arrangement Benefits}}: {{30-55 word description of flexible work options, location benefits, and work-life integration}}",
        "{{Industry-Specific Allowances}}: {{30-55 word explanation of relevant allowances, equipment support, or specialized benefits}}",
        "Team Culture & Engagement: {{30-55 word description of team activities, company culture, recognition programs, and employee engagement}}"
    ],
    
    "application_process": "{{Generate professional application process suitable for the industry and role level. Mention typical steps: application review, screening, assessment/interview rounds, reference checks, decision. Timeline 2-4 weeks. Avoid fake contact details.}}",
    
    "company_website": "{{ONLY include if user explicitly mentions a website URL in their prompt, otherwise leave empty}}"
}}

INDUSTRY-SPECIFIC ADAPTATIONS:
- For IT/Tech roles: Focus on technical skills, coding, software, frameworks
- For Healthcare/Medical: Emphasize patient care, medical procedures, certifications, compliance
- For Manufacturing: Highlight production processes, safety, quality control, equipment operation
- For Finance/Banking: Focus on financial analysis, regulations, risk management, client services
- For Education: Emphasize teaching methods, curriculum, student development, educational technology
- For Retail: Focus on customer service, sales, inventory, merchandising
- For Construction: Highlight safety protocols, technical skills, project management, regulations
- For Non-Profit: Emphasize mission alignment, community impact, fundraising, program management

Return ONLY the JSON object, no markdown formatting or additional text."""
    
    response = model.generate_content(enhanced_prompt)
    response_text = response.text.strip()
    if response_text.startswith('```json'): response_text = response_text[7:]
    if response_text.endswith('```'): response_text = response_text[:-3]
    response_text = response_text.strip()
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse Gemini response as JSON: {e}")