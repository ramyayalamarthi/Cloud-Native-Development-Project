import os
import time
from flask import Flask, redirect, request, render_template_string,send_file
from genai import upload_to_gemini
import json
from storage import download_file, get_list_of_files

ui_background_colour = "blue"
os.makedirs('files', exist_ok = True)
bucket_name = "cnd_images"

app = Flask(__name__)

@app.route('/')
def index():
    index_html = f"""
    <html>
    <head>
        <style>
            body {{
                background-color: {ui_background_colour};
                color: white;
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
            }}
            form {{
                padding: 20px;
                border-radius: 10px;
                background-color: {ui_background_colour};
            }}
            button {{
                background-color: white;
                color: {ui_background_colour};
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
            ul {{
                list-style-type: none;
                padding: 0;
            }}
            li {{
                margin: 5px 0;
            }}
        </style>
    </head>
    <body>
        <form method="post" enctype="multipart/form-data" action="/upload">
            <div>
                <label for="file">Choose file to upload</label>
                <input type="file" id="file" name="form_file" accept="image/jpeg"/>
            </div>
            <div>
                <button type="submit">Submit</button>
            </div>
        </form>
        <ul>
    """
    for file in list_files():
        index_html += f'<li><a href="/files/{file}" style="color: white;">{file}</a></li>'
    index_html += "</ul></body></html>"

    return index_html

@app.route('/upload', methods=["POST"])
def upload():
    file = request.files['form_file'] 
    time_stamp = int(time.time())
    filename = f"{time_stamp}_{file.filename}"
    file.save(os.path.join("./files", filename))
    image_path = "files/"+filename
    upload_to_gemini(bucket_name,image_path)
    return redirect("/")

@app.route('/files')
def list_files():
    cloud_files = get_list_of_files(bucket_name)
    files = os.listdir("./files")
    paths_files = ["files/" + item for item in files]
    downloads =list(set(cloud_files) - set(paths_files))
    for i in downloads:
      download_file(bucket_name,i)

    files = os.listdir("./files")  
    jpegs = []
    for file in files:
        if file.lower().endswith((".jpeg", ".jpg")):
            jpegs.append(file)
    
    return jpegs

@app.route('/files/<filename>')
def get_file(filename):
    files_name = filename.split('.')[0]
    time_stamp = str(files_name.split('_')[0])
    json_file  = "./files/"+ files_name + ".json"
    file_name_without_ts = files_name.replace(time_stamp+"_","")
    with open(json_file, 'r') as file:
        data = json.load(file)

    title = data.get("title")
    description = data.get("description")
    html_content = f"""
    <html>
    <head>
        <title>{file_name_without_ts}</title>
        <style>
            body {{
                background-color: {ui_background_colour};
                color: white;
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                text-align: center;
            }}
            img {{
                width: 25%;
                border-radius: 10px;
                margin: 10px 0;
            }}
            h1 {{
                color: white;
            }}
            p {{
                font-size: 18px;
            }}
        </style>
    </head>
    <body>
        <h1>{file_name_without_ts}</h1>
        <img src='/image/{filename}' alt="{file_name_without_ts}">
        <p><strong>Title:</strong> {title}</p>
        <p><strong>Description:</strong> {description}</p>
    </body>
</html>
"""
    return render_template_string(html_content)

@app.route('/image/<filename>')
def image_file(filename):
    file_path = os.path.join('./files', filename)

    if not os.path.exists(file_path):
        return "File not found", 404
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
