import os
import time
from flask import Flask, redirect, request, send_file
from genai import upload_to_gemini
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
</form>"""    

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
        if file.lower().endswith((".jpeg", ".jpg", ".json")):
            jpegs.append(file)
    
    return jpegs

@app.route('/files/<filename>')
def get_file(filename):
  return send_file('./files/'+filename)

if __name__ == '__main__':
    app.run(debug=True)