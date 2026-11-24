from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Title slide
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid()
slide.background.fill.fore_color.rgb = RGBColor(0xF8, 0xFA, 0xFC)

shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(0.6), Inches(0.55), Inches(12.1), Inches(1.2))
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0x0F, 0x76, 0x6E)
shape.line.color.rgb = RGBColor(0x0F, 0x76, 0x6E)

text_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.8), Inches(0.8))
text_frame = text_box.text_frame
p = text_frame.paragraphs[0]
p.text = 'AI Travel Planner'
p.font.size = Pt(28)
p.font.bold = True
p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
p.alignment = PP_ALIGN.LEFT

text_box2 = slide.shapes.add_textbox(Inches(0.8), Inches(1.9), Inches(11.8), Inches(1.2))
text_frame2 = text_box2.text_frame
p2 = text_frame2.paragraphs[0]
p2.text = 'An AI-powered travel planning system for generating personalized itineraries'
p2.font.size = Pt(20)
p2.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)

cards = [
    ('Project Type', 'Academic full-stack web application'),
    ('Main Goal', 'Help users plan trips and generate day-by-day itineraries using AI'),
    ('Tech Stack', 'FastAPI, React, TypeScript, PostgreSQL, Gemini AI'),
]
for i, (title, desc) in enumerate(cards):
    x = Inches(0.8 + (i * 4.1))
    shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, x, Inches(3.2), Inches(3.6), Inches(2.3))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0xEA, 0xF7, 0xF6)
    shape.line.color.rgb = RGBColor(0x0F, 0x76, 0x6E)
    tb = slide.shapes.add_textbox(x + Inches(0.2), Inches(3.35), Inches(3.2), Inches(1.4))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0x0F, 0x76, 0x6E)
    p = tf.add_paragraph()
    p.text = desc
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(0x4B, 0x55, 0x63)

text_box3 = slide.shapes.add_textbox(Inches(0.8), Inches(6.6), Inches(11.8), Inches(0.4))
text_frame3 = text_box3.text_frame
p3 = text_frame3.paragraphs[0]
p3.text = 'Presented by: Your Name | College Project Presentation'
p3.font.size = Pt(12)
p3.font.color.rgb = RGBColor(0x6B, 0x72, 0x7D)

# slide 2
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = 'Problem Statement'
body = slide.shapes.placeholders[1].text_frame
body.clear()
p = body.paragraphs[0]
p.text = 'Travel planning is often time-consuming, scattered across multiple apps, and difficult to customize.\n\nOur solution brings trip details, budgeting, and itinerary generation into one intelligent platform.'
p.font.size = Pt(24)

# slide 3
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = 'Objectives'
body = slide.shapes.placeholders[1].text_frame
body.clear()
p = body.paragraphs[0]
p.text = 'Create a full-stack travel planner\nBuild secure user authentication\nAllow users to create and manage trips\nGenerate AI-based day-by-day itineraries\nProvide a clean and simple web interface'
p.font.size = Pt(24)

# slide 4
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = 'Key Features'
body = slide.shapes.placeholders[1].text_frame
body.clear()
p = body.paragraphs[0]
p.text = 'User registration and login\nTrip creation and management\nSaved itineraries and trip history\nAI-generated recommendations via Gemini\nResponsive dashboard and modern UI'
p.font.size = Pt(24)

# slide 5
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = 'Technology Stack'
body = slide.shapes.placeholders[1].text_frame
body.clear()
p = body.paragraphs[0]
p.text = 'Backend: FastAPI, Python, SQLAlchemy, Alembic\nFrontend: React, TypeScript, Vite, Tailwind CSS\nDatabase: PostgreSQL\nAI: Google Gemini API\nDeployment: Docker support'
p.font.size = Pt(24)

# slide 6
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = 'Project Workflow'
body = slide.shapes.placeholders[1].text_frame
body.clear()
p = body.paragraphs[0]
p.text = '1. User registers and logs in\n2. User creates a trip with destination, dates, and budget\n3. System stores trip details in the database\n4. AI provider generates a personalized itinerary\n5. User views and manages their saved itinerary'
p.font.size = Pt(24)

# slide 7
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = 'Benefits and Impact'
body = slide.shapes.placeholders[1].text_frame
body.clear()
p = body.paragraphs[0]
p.text = 'Saves time compared to manual planning\nProvides structured travel suggestions\nMakes travel organization easier for students and travelers\nShows how AI can be applied in real-world applications'
p.font.size = Pt(24)

# slide 8
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = 'Conclusion'
body = slide.shapes.placeholders[1].text_frame
body.clear()
p = body.paragraphs[0]
p.text = 'This project demonstrates a practical AI-powered travel assistant built using modern full-stack technologies.\n\nIt combines web development, backend services, and AI integration into one complete solution.'
p.font.size = Pt(24)

out = 'presentation_ai_travel_planner.pptx'
prs.save(out)
print(out)
