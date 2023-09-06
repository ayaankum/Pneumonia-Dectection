from flask import Flask
from flask import render_template, request
from fpdf import FPDF
from keras_preprocessing import image
from keras.models import load_model
from keras.applications.vgg16 import preprocess_input
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pymongo
import hashlib

model = load_model('chest_xray.h5')

app = Flask(__name__, template_folder='static')
global new

def databaseInsert(name, emailId, age, contact,has,result):
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client['Pneumonia']
    collection = db['Pneumonia']
    dictionary = {"Name": name, "Email-ID": emailId,
                  "Age": age, "Contact": contact, "Hashed Prediction": has , "Actual Prediction" : result}
    collection.insert_one(dictionary)

def hashing(to_hash):
    h = hashlib.new("SHA256")
    h.update(to_hash.encode())
    hashed_string = h.hexdigest()
    return hashed_string
def predict_new(path,name, emailId, age, contact):
    predictions = ["has_Pneumonia", "doesn't_have_PNEUMONIA"]
    img = image.load_img(path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    img_data = preprocess_input(x)
    classes = model.predict(img_data)
    print(classes)
    result = int(classes[0][0])
    print(result)
    if result == 0:
        a = predictions[0]
        has = hashing(a)
        print(has)
        print("Person is Affected By PNEUMONIA")
    else:
        a = predictions[1]
        has=hashing(a)
        print("Result is Normal")

    print(a)
    mm = f"""
                             PNEUMONIA report by i-Lung
           Patient name:{name}
           Age: {age}
           Email id:{emailId}
           Contact no:{contact}
           
           Diagnosis:
           1.chest scan shows {a}.
           Further advice for treatment: 
           1. Maintain proper fluid intake to prevent dehydration.
           2. Get ample rest to aid the body's recovery process.
           3. use techniques to assist breathing and clear airways.
           4. Regular medical check-ups to monitor progress.
          """
    file1 = open("baseFile.txt", "w")
    file1.writelines(mm)
    file1.close()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    f = open("baseFile.txt", "r")
    print(f)
    for x in f:
        pdf.cell(200, 8, txt=x, ln=1, align='L')
    print("Done with pdf")
    pdf.output('report.pdf')
    databaseInsert(name, emailId, age, contact, has , a)
    smtp_port = 587
    smtp_server = "smtp.gmail.com"

    email_from = "ayaankumary@gmail.com"
    email_to = emailId
    pswd = "sowfubtibgtjdvnk"

    subject = "This email has Attacthment"
    body = f"""
        LUNG TEST REPORT
         this email has attachnment
        """
    msg = MIMEMultipart()
    msg['from'] = email_from
    msg['to'] = email_to
    msg['subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    filename = "report.pdf"

    attachment = open(filename, 'rb')

    attachment_package = MIMEBase('application', 'octet-stream')
    attachment_package.set_payload((attachment).read())
    encoders.encode_base64(attachment_package)
    attachment_package.add_header('content-Disposition', "attachment; filename= " + filename)
    msg.attach(attachment_package)

    text = msg.as_string()

    print("connecting to the server")
    ay_server = smtplib.SMTP(smtp_server, smtp_port)
    ay_server.starttls()
    ay_server.login(email_from, pswd)
    print("connected to server")
    print()

    print("sending email")
    ay_server.sendmail(email_from, email_to, text)
    print("email sent")
    print()
    ay_server.quit()



@app.route("/", methods=['GET'])
def hello():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def predict():
    name = request.form['name']
    emailId = request.form['emailId']
    contact = request.form['contact']
    age = request.form['username']
    print(name, emailId, contact, age)
    imagefile = request.files['imagefile']
    image_path = "images/" + imagefile.filename
    imagefile.save(image_path)
    predict_new(image_path, name, emailId, age, contact)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=3000, debug=True)

