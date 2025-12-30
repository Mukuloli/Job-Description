import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch

def setup_pdf_styles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(name='CompanyHeaderStyle', parent=styles['Normal'], fontSize=12, leading=14, alignment=TA_CENTER, fontName='Helvetica-Bold', textColor=colors.black, spaceAfter=4))
    styles.add(ParagraphStyle(name='JobTitleStyle', parent=styles['Normal'], fontSize=14, leading=18, alignment=TA_LEFT, fontName='Helvetica-Bold', textColor=colors.black, spaceAfter=6, spaceBefore=4))
    styles.add(ParagraphStyle(name='JobMetaStyle', parent=styles['Normal'], fontSize=11, leading=13, alignment=TA_LEFT, fontName='Helvetica', textColor=colors.black, spaceAfter=1))
    styles.add(ParagraphStyle(name='CompanyFooterStyle', parent=styles['Normal'], fontSize=11, leading=14, alignment=TA_CENTER, fontName='Helvetica-Bold', textColor=colors.black, spaceAfter=8, spaceBefore=12))
    styles.add(ParagraphStyle(name='SectionHeaderStyle', parent=styles['Normal'], fontSize=11, leading=14, alignment=TA_LEFT, fontName='Helvetica-Bold', textColor=colors.black, spaceAfter=6, spaceBefore=10))
    styles.add(ParagraphStyle(name='BodyTextStyle', parent=styles['Normal'], fontSize=11, leading=13, alignment=TA_LEFT, fontName='Helvetica', textColor=colors.black, spaceAfter=6))
    styles.add(ParagraphStyle(name='BulletTitleStyle', parent=styles['Normal'], fontSize=11, leading=13, alignment=TA_LEFT, fontName='Helvetica', textColor=colors.black, leftIndent=0, spaceAfter=2, spaceBefore=4))
    styles.add(ParagraphStyle(name='BulletContentStyle', parent=styles['Normal'], fontSize=11, leading=13, alignment=TA_LEFT, fontName='Helvetica', textColor=colors.black, leftIndent=15, spaceAfter=6, rightIndent=5))
    
    return styles

def has_content(value):
    if value is None: 
        return False
    if isinstance(value, str): 
        return value.strip() != ""
    if isinstance(value, (list, tuple)): 
        return any(has_content(item) for item in value)
    if isinstance(value, dict): 
        return any(has_content(v) for v in value.values())
    return bool(value)

def format_bullet_content(content_list, styles):
    formatted_content = []
    for item in content_list:
        if not has_content(item): 
            continue
        if isinstance(item, str):
            if ':' in item:
                parts = item.split(':', 1)
                title, content = parts[0].strip(), parts[1].strip()
                formatted_content.append(Paragraph(f"● <b>{title}:</b>", styles['BulletTitleStyle']))
                if has_content(content):
                    formatted_content.append(Paragraph(content, styles['BulletContentStyle']))
            else:
                formatted_content.append(Paragraph(f"● {item}", styles['BulletTitleStyle']))
        else:
            formatted_content.append(Paragraph(f"● {str(item)}", styles['BulletTitleStyle']))
    return formatted_content

def create_job_description_pdf(output_filename, data, logo_path=None):
    doc = SimpleDocTemplate(output_filename, pagesize=letter, topMargin=1.4*inch, bottomMargin=1.2*inch, leftMargin=1*inch, rightMargin=1*inch)
    styles = setup_pdf_styles()
    content = []
    company_name = data.get('company_name', '')

    def _draw_page_elements(canvas, doc_local):
        try:
            page_width, page_height = doc_local.pagesize
            margin_left, margin_right, margin_top, margin_bottom = doc_local.leftMargin, doc_local.rightMargin, doc_local.topMargin, doc_local.bottomMargin
            logo_width, logo_height = 1.4*inch, 0.6*inch
            frame_top_y = page_height - margin_top
            padding_right = 0.2*inch
            company_website = data.get('company_website', '')
            
            canvas.saveState()
            
            # Header section - only company name and logo (no website in header)
            if has_content(company_name):
                # Calculate the right-aligned position for company name
                x_right_limit = page_width - margin_right - padding_right
                max_name_width = 3.5*inch
                
                # Company name styling
                name_font_size = 12
                name_width = canvas.stringWidth(company_name, 'Helvetica-Bold', name_font_size)
                while name_width > max_name_width and name_font_size > 8:
                    name_font_size -= 1
                    name_width = canvas.stringWidth(company_name, 'Helvetica-Bold', name_font_size)
                
                # Position company name on the right
                name_y = frame_top_y + logo_height + 15
                name_x = x_right_limit - name_width
                canvas.setFont('Helvetica-Bold', name_font_size)
                canvas.drawString(name_x, name_y, company_name)
                
                # Position logo centered below the company name
                name_center_x = name_x + (name_width / 2)
                logo_x = name_center_x - (logo_width / 2)
                logo_y = frame_top_y + 3
            else:
                # If no company name, center the logo at the top
                logo_x = (page_width / 2) - (logo_width / 2)
                logo_y = frame_top_y

            # Draw logo if available
            if logo_path and os.path.exists(logo_path):
                try:
                    canvas.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
                except: 
                    pass

            # Footer section - only show if BOTH company name and website are provided
            if has_content(company_name) and has_content(company_website):
                footer_base_y = margin_bottom - 40
                footer_name_y = footer_base_y + 15
                footer_website_y = footer_base_y
                x_right_limit_footer = page_width - margin_right - 0.2*inch
                max_footer_width = 3*inch
                
                try:
                    # Calculate footer block dimensions
                    footer_name_size = 11
                    footer_name_width = canvas.stringWidth(company_name, 'Helvetica-Bold', footer_name_size)
                    while footer_name_size >= 8 and footer_name_width > max_footer_width:
                        footer_name_size -= 1
                        footer_name_width = canvas.stringWidth(company_name, 'Helvetica-Bold', footer_name_size)
                    
                    footer_site_size = 9
                    footer_site_width = canvas.stringWidth(company_website, 'Helvetica', footer_site_size)
                    while footer_site_size >= 7 and footer_site_width > max_footer_width:
                        footer_site_size -= 1
                        footer_site_width = canvas.stringWidth(company_website, 'Helvetica', footer_site_size)
                    
                    # Footer block positioning (right-aligned with centered content within block)
                    footer_block_width = max(footer_name_width, footer_site_width)
                    footer_block_right_x = x_right_limit_footer
                    footer_block_left_x = footer_block_right_x - footer_block_width
                    footer_block_center_x = footer_block_left_x + (footer_block_width / 2)
                    
                    # Draw company name in footer
                    canvas.setFont('Helvetica-Bold', footer_name_size)
                    footer_name_x = footer_block_center_x - (footer_name_width / 2)
                    canvas.drawString(footer_name_x, footer_name_y, company_name)
                    
                    # Draw website link in footer
                    canvas.setFont('Helvetica', footer_site_size)
                    canvas.setFillColor(colors.darkblue)
                    footer_site_x = footer_block_center_x - (footer_site_width / 2)
                    canvas.drawString(footer_site_x, footer_website_y, company_website)
                    
                    # Draw underline for website link
                    canvas.setStrokeColor(colors.darkblue)
                    canvas.setLineWidth(0.5)
                    canvas.line(footer_site_x, footer_website_y - 1, footer_site_x + footer_site_width, footer_website_y - 1)
                    canvas.setFillColor(colors.black)
                    canvas.setStrokeColor(colors.black)
                except: 
                    pass
            canvas.restoreState()
        except: 
            pass
    
    # Add job title (only once)
    job_title = data.get('job_title', 'Software Developer')
    content.append(Paragraph(f"<b>{job_title}</b>", styles['JobTitleStyle']))
    
    # Add metadata section with all relevant fields (consolidated, no duplicates)
    metadata_items = [
        ('team', 'Team'),
        ('location', 'Location'),
        ('reporting_to', 'Reporting To'),
        ('employment_type', 'Employment Type'),
        ('experience_required', 'Experience Required'),
        ('salary_range', 'Salary Range'),
        ('office_timings', 'Office Timings'),
        ('working_days', 'Working Days'),
        ('work_schedule', 'Work Schedule')
    ]
    
    for key, label in metadata_items:
        value = data.get(key, '')
        if has_content(value):
            content.append(Paragraph(f"{label}: {value}", styles['JobMetaStyle']))
    
    # Add separator
    content.extend([Spacer(1, 10), HRFlowable(width="100%", thickness=1, color=colors.grey), Spacer(1, 8)])
    
    # Process main content sections
    sections = [
        ('company_overview', 'Company Overview'),
        ('role_overview', 'Role Overview'),
        ('key_responsibilities', 'Key Responsibilities'),
        ('technical_requirements', 'Technical Requirements'),
        ('who_you_are', 'Who You Are'),
        ('experience_skills', 'Experience & Skills'),
        ('qualifications', 'Required Qualifications'),
        ('preferred_qualifications', 'Preferred Qualifications'),
        ('what_we_offer', 'What We Offer'),
        ('benefits', 'Benefits & Perks'),
        ('application_process', 'Application Process')
    ]
    
    for key, title in sections:
        section_data = data.get(key, '')
        
        # Handle special case for benefits fallback
        if key == 'benefits' and not has_content(section_data):
            section_data = data.get('compensation_benefits', {})
        
        if has_content(section_data):
            content.append(Paragraph(f"<b>{title}</b>", styles['SectionHeaderStyle']))
            
            if isinstance(section_data, list):
                content.extend(format_bullet_content(section_data, styles))
            elif isinstance(section_data, dict):
                if key == 'technical_requirements':
                    must_have = section_data.get('must_have_skills', [])
                    nice_to_have = section_data.get('nice_to_have_skills', [])
                    
                    if has_content(must_have):
                        if isinstance(must_have, list):
                            content.extend(format_bullet_content(must_have, styles))
                        else:
                            content.append(Paragraph(str(must_have), styles['BodyTextStyle']))
                    
                    if has_content(nice_to_have):
                        content.append(Paragraph("<b>Nice to have:</b>", styles['BodyTextStyle']))
                        if isinstance(nice_to_have, list):
                            content.extend(format_bullet_content(nice_to_have, styles))
                        else:
                            content.append(Paragraph(str(nice_to_have), styles['BodyTextStyle']))
                            
                elif key in ['qualifications', 'experience_skills']:
                    items_key = 'mandatory_requirements' if key == 'qualifications' else 'professional_experience'
                    items = section_data.get(items_key, [])
                    if has_content(items):
                        if isinstance(items, list):
                            content.extend(format_bullet_content(items, styles))
                        else:
                            content.append(Paragraph(str(items), styles['BodyTextStyle']))
                            
                elif key in ['what_we_offer', 'benefits']:
                    all_items = []
                    for k, v in section_data.items():
                        if has_content(v):
                            if isinstance(v, list):
                                all_items.extend(v)
                            else:
                                all_items.append(str(v))
                    
                    if all_items:
                        # Limit items to prevent overflow
                        max_items = 8 if key == 'benefits' else 5
                        content.extend(format_bullet_content(all_items[:max_items], styles))
                        
                elif key == 'application_process':
                    how_to_apply = section_data.get('how_to_apply', '')
                    if has_content(how_to_apply):
                        content.append(Paragraph(str(how_to_apply), styles['BodyTextStyle']))
                else:
                    # Handle other dictionary structures
                    for k, v in section_data.items():
                        if has_content(v):
                            content.append(Paragraph(f"<b>{k.replace('_', ' ').title()}:</b>", styles['BodyTextStyle']))
                            if isinstance(v, list):
                                content.extend(format_bullet_content(v, styles))
                            else:
                                content.append(Paragraph(str(v), styles['BodyTextStyle']))
            else:
                content.append(Paragraph(str(section_data), styles['BodyTextStyle']))
            
            # Add section separator (except for last section)
            if key != sections[-1][0] or sections.index((key, title)) < len(sections) - 1:
                content.extend([Spacer(1, 8), HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey), Spacer(1, 8)])
    
    def measure_content_height(flowables, available_width):
        """More accurate content height measurement"""
        total_height = 0
        for flowable in flowables:
            try:
                if hasattr(flowable, 'wrap'):
                    _, height = flowable.wrap(available_width, float('inf'))
                    total_height += height
                elif hasattr(flowable, 'height'):
                    total_height += flowable.height
                else:
                    # Default fallback for unknown flowables
                    total_height += 12
            except Exception:
                # Fallback height if wrap fails
                total_height += 12
        return total_height

    def optimize_content_spacing(content_list, target_reduction=0.15):
        """Optimize spacing to fit content better"""
        for flowable in content_list:
            if isinstance(flowable, Spacer) and hasattr(flowable, 'height'):
                try:
                    flowable.height = max(2, flowable.height * (1 - target_reduction))
                except:
                    pass
            elif isinstance(flowable, HRFlowable):
                try:
                    flowable.thickness = max(0.5, getattr(flowable, 'thickness', 1) * 0.8)
                except:
                    pass

    def adjust_font_sizes(styles_dict, reduction=1):
        """Reduce font sizes to fit more content"""
        style_names = ['BodyTextStyle', 'BulletContentStyle', 'BulletTitleStyle', 'JobMetaStyle']
        for name in style_names:
            if name in styles_dict:
                style = styles_dict[name]
                style.fontSize = max(8, style.fontSize - reduction)
                style.leading = max(style.fontSize + 1, style.leading - reduction)
        
        if 'SectionHeaderStyle' in styles_dict:
            header_style = styles_dict['SectionHeaderStyle']
            header_style.fontSize = max(10, header_style.fontSize - reduction)
            header_style.leading = max(header_style.fontSize + 1, header_style.leading - reduction)

    # Check if content fits and optimize if needed
    available_height = doc.height * 2.8  # Allow for reasonable multi-page content
    content_height = measure_content_height(content, doc.width)
    
    if content_height > available_height:
        # First optimization: reduce spacing
        optimize_content_spacing(content, 0.2)
        
        # Re-measure after spacing optimization
        content_height = measure_content_height(content, doc.width)
        
        if content_height > available_height * 1.1:
            # Second optimization: reduce font sizes slightly
            adjust_font_sizes(styles, 1)
            optimize_content_spacing(content, 0.3)
    
    # Build the PDF
    doc.build(content, onFirstPage=_draw_page_elements, onLaterPages=_draw_page_elements)