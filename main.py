import os
import time
from flask import Flask, redirect, request, render_template_string,send_file
from genai import upload_to_gemini
import json
from storage import download_file, get_list_of_files


os.makedirs('files', exist_ok = True)
bucket_name = "cnd_images"

app = Flask(__name__)

@app.route('/')
def index():
    index_html="""
                    <form method="post" enctype="multipart/form-data" action="/upload" method="post">
                      <div>
                        <label for="file">Choose file to upload</label>
                        <input type="file" id="file" name="form_file" accept="image/jpeg"/>
                      </div>
                      <div>
                        <button>Submit</button>
                      </div>
                    </form>
                """
    for file in list_files():
        index_html += "<li><a href=\"/files/" + file + "\">" + file + "</a></li>"

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
        </head>
        <body>
            <h1>{file_name_without_ts}</h1>
            <img src='/image/{filename}' width="25%">
            <p><strong>title:</strong> {title}</p>
            <p><strong>description:</strong> {description}</p>
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
