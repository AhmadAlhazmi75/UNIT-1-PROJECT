from .openai_client import OpenAIClient
from markdown2 import Markdown
from weasyprint import HTML
import tempfile
import os

class ReportGenerator:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.openai_client = OpenAIClient()
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def generate_report(self, prompt: str, output_file: str = "report.pdf"):
        try:
            # Generate markdown report using OpenAI
            markdown_report = self.openai_client.get_report(prompt)

            # Convert markdown to HTML
            markdowner = Markdown()
            html_content = markdowner.convert(markdown_report)

            # Get the absolute path to the logo
            logo_path = os.path.join(self.base_dir, 'Lana.png')

            # Check if the logo file exists
            if os.path.exists(logo_path):
                logo_html = f'<img src="{logo_path}" alt="Lana Logo" class="logo">'
            else:
                print(f"Warning: Logo file not found at {logo_path}")
                logo_html = ''  # Empty string if logo is not found

            # Create a temporary HTML file with enhanced styling
            html_template = f"""
            <html>
            <head>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
                    body {{
                        font-family: 'Poppins', sans-serif;
                        line-height: 1.8;
                        margin: 0;
                        padding: 0;
                        background-color: #f7f9fc;
                        color: #333;
                    }}
                    .container {{
                        max-width: 800px;
                        margin: 40px auto;
                        background-color: #ffffff;
                        padding: 40px;
                        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                        border-radius: 16px;
                    }}
                    .logo {{
                        display: block;
                        width: 150px;
                        height: auto;
                        margin: 0 auto 30px;
                        border-radius: 50%;
                        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
                    }}
                    h1, h2, h3 {{
                        color: #2c3e50;
                        margin-top: 30px;
                    }}
                    h1 {{
                        font-size: 32px;
                        border-bottom: 3px solid #3498db;
                        padding-bottom: 15px;
                        margin-bottom: 30px;
                        text-align: center;
                    }}
                    h2 {{
                        font-size: 26px;
                        color: #2980b9;
                        border-left: 4px solid #2980b9;
                        padding-left: 15px;
                    }}
                    h3 {{
                        font-size: 22px;
                        color: #16a085;
                    }}
                    p {{
                        margin-bottom: 20px;
                        text-align: justify;
                    }}
                    ul, ol {{
                        margin-bottom: 20px;
                        padding-left: 30px;
                    }}
                    li {{
                        margin-bottom: 10px;
                    }}
                    .highlight {{
                        background-color: #e8f4fd;
                        padding: 15px;
                        border-radius: 8px;
                        border-left: 4px solid #3498db;
                    }}
                    .section {{
                        background-color: #ffffff;
                        padding: 25px;
                        margin-bottom: 30px;
                        border-radius: 12px;
                        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
                    }}
                    .btn {{
                        display: inline-block;
                        padding: 10px 20px;
                        background-color: #3498db;
                        color: #ffffff;
                        text-decoration: none;
                        border-radius: 25px;
                        transition: background-color 0.3s ease;
                    }}
                    .btn:hover {{
                        background-color: #2980b9;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    {logo_html}
                    {html_content}
                </div>
            </body>
            </html>
            """
            with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as temp_html:
                temp_html.write(html_template)
                temp_html_path = temp_html.name

            # Convert HTML to PDF
            HTML(filename=temp_html_path).write_pdf(output_file)

            return output_file
        except Exception as e:
            print(f"An error occurred while generating the report: {str(e)}")
            return None
