import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///documents.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(message)s')

class DocumentItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(200), nullable=False)
    is_checked = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<DocumentItem {self.item}>'

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    download_link = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<UploadedFile {self.filename}>'

@app.route('/')
def index():
    sections = [
        {
            "title": "Documentos Necesarios para el Canje del Carnet de Conducir Ecuatoriano por el Español",
            "content": [
                {
                    "subtitle": "Requisitos para el Canje",
                    "document_items": [
                        {
                            "item": "Residencia Legal en España",
                            "details": [
                                "N.I.E. (Número de Identificación de Extranjero)",
                                "T.I.E. (Tarjeta de Identificación de Extranjeros)",
                                "D.N.I. (Documento Nacional de Identidad), si ya tienes ciudadanía española."
                            ]
                        },
                        {
                            "item": "Carnet de Conducir Ecuatoriano Vigente",
                            "details": [
                                "El carnet debe estar vigente. Si está caducado, primero debes renovarlo en Ecuador."
                            ]
                        },
                        {
                            "item": "Certificado de Aptitud Psicofísica",
                            "details": [
                                "Informe que demuestre que estás en condiciones de conducir.",
                                "Este certificado se puede obtener en centros autorizados, tiene un costo que varía según la comunidad autónoma y es válido por 90 días."
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "title": "Documentos Necesarios para Presentar la Solicitud de arraigo familiar",
            "content": [
                {
                    "subtitle": "Documentos Generales",
                    "document_items": [
                        {
                            "item": "Impreso de Solicitud",
                            "details": [
                                "Modelo oficial (EX–10) por duplicado, debidamente cumplimentado y firmado por el extranjero."
                            ]
                        },
                        {
                            "item": "Identificación",
                            "details": [
                                "Copia completa del pasaporte, título de viaje o cédula de inscripción con vigencia mínima de cuatro meses."
                            ]
                        },
                        {
                            "item": "Certificado de Antecedentes Penales",
                            "details": [
                                "Certificado expedido por las autoridades del país o países en los que haya residido durante los cinco últimos años anteriores a la entrada en España."
                            ]
                        }
                    ]
                },
                {
                    "subtitle": "Documentos Específicos",
                    "document_items": [
                        {
                            "item": "Para Cónyuge o Pareja de Hecho de Ciudadano Español",
                            "details": [
                                "Existencia del vínculo familiar con el ciudadano español, o de una pareja registrada.",
                                "En su caso, acreditación de encontrarse a cargo del ciudadano español.",
                                "DNI del ciudadano español."
                            ]
                        },
                        {
                            "item": "Para Hijo de Padre o Madre Originariamente Españoles",
                            "details": [
                                "Certificado de Nacimiento del Solicitante",
                                "Certificado de Nacimiento del Padre o Madre",
                                "Que hubieran sido originariamente españoles.",
                                "Certificado del Registro Civil que acredite dicha condición."
                            ]
                        }
                    ]
                },
                {
                    "subtitle": "Notas Importantes",
                    "document_items": [
                        {
                            "item": "Traducción de Documentos",
                            "details": [
                                "Documentos de otros países deben estar traducidos al castellano o lengua cooficial del territorio donde se presente la solicitud por un traductor oficial."
                            ]
                        },
                        {
                            "item": "Legalización de Documentos",
                            "details": [
                                "Documentos públicos extranjeros deben ser legalizados por la Oficina consular de España o por el Ministerio de Asuntos Exteriores, salvo que estén apostillados según el Convenio de la Haya de 1961 o exentos de legalización en virtud de Convenio Internacional."
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "title": "Documentos Necesarios para la Equivalencia de Estudios Universitarios",
            "content": [
                {
                    "document_items": [
                        {
                            "item": "Documento de Identidad",
                            "details": [
                                "Únicamente para las personas que no dispongan de DNI/NIE, copia compulsada del documento que acredite la identidad y nacionalidad del solicitante, expedido por las autoridades competentes del país de origen o de procedencia."
                            ]
                        },
                        {
                            "item": "Título Universitario",
                            "details": [
                                "Copia compulsada del título cuya equivalencia se solicita.",
                                "Traducción oficial, en su caso."
                            ]
                        },
                        {
                            "item": "Certificación Académica",
                            "details": [
                                "Copia compulsada de la certificación académica de los estudios realizados por el solicitante para la obtención del título cuya equivalencia se solicita.",
                                "Traducción oficial, en su caso."
                            ]
                        },
                        {
                            "item": "Pago de la Tasa",
                            "details": [
                                "Acreditación del pago de la tasa, de acuerdo con el artículo 28 de la Ley 53/2002, de 30 de diciembre, de Medidas Fiscales, Administrativas y del Orden Social (BOE del 31).",
                                "**Importante:** Imprescindible para la apertura del trámite."
                            ]
                        },
                        {
                            "item": "Otros Documentos",
                            "details": [
                                "Cualquier otro documento relevante que se considere necesario para el trámite."
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "title": "Otros documentos",
            "content": [
                {
                    "document_items": [
                        {
                            "item": "Acta de nacimiento",
                            "details": [
                                "Acta de nacimiento apostillada."
                            ]
                        },
                        {
                            "item": "Fotos tipo carnet",
                            "details": [
                                "Fotos recientes para diversos trámites y documentos."
                            ]
                        },
                        {
                            "item": "Certificados de vacunas",
                            "details": [
                                "Certificados de vacunas si se requiere para la entrada al país."
                            ]
                        },
                        {
                            "item": "Referencias laborales",
                            "details": [
                                "Cartas de recomendación y referencias laborales anteriores"
                            ]
                        },
                        {
                            "item": "Informe de vida laboral",
                            "details": [
                                "Un informe que detalle el historial laboral en Ecuador."
                            ]
                        }
                    ]
                }
            ]
        }
    ]

    # Insert items into the database if they do not exist
    for section in sections:
        for content in section["content"]:
            for doc_item in content["document_items"]:
                existing_item = DocumentItem.query.filter_by(item=doc_item["item"]).first()
                if not existing_item:
                    new_item = DocumentItem(item=doc_item["item"])
                    db.session.add(new_item)
                    db.session.commit()

    document_items = DocumentItem.query.all()
    return render_template('index.html', sections=sections, document_items=document_items)

@app.route('/update', methods=['POST'])
def update():
    data = request.json
    item = DocumentItem.query.filter_by(item=data['item']).first()
    if item:
        item.is_checked = data['is_checked']
        db.session.commit()
        logging.info(f'Updated item {item.item}: checked={data["is_checked"]}')
    return jsonify(success=True)

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    for item_data in data['items']:
        item = DocumentItem.query.filter_by(item=item_data['item']).first()
        if item:
            item.is_checked = item_data['is_checked']
            db.session.commit()
            logging.info(f'Saved item {item.item}: checked={item_data["is_checked"]}')
    return jsonify(success=True)

@app.route('/upload', methods=['POST'])
def upload():
    item_name = request.form.get('item')
    files_saved = []
    for uploaded_file in request.files.getlist('files'):
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(file_path)
        
        url = f'/uploads/{filename}'
        download_link = f'<a href="{url}" download>{filename}</a>'

        new_uploaded_file = UploadedFile(
            item_name=item_name,
            filename=filename,
            url=url,
            download_link=download_link
        )
        db.session.add(new_uploaded_file)
        db.session.commit()
        
        files_saved.append({
            'filename': filename,
            'url': url,
            'download_link': download_link
        })
        
        logging.info(f'File uploaded for item {item_name}: {filename}')
    
    return jsonify(success=True, files=files_saved)

@app.route('/get_uploaded_files', methods=['GET'])
def get_uploaded_files():
    item_name = request.args.get('item')
    uploaded_files = UploadedFile.query.filter_by(item_name=item_name).all()
    files = [{
        'filename': file.filename,
        'url': file.url,
        'download_link': file.download_link
    } for file in uploaded_files]
    return jsonify(files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Running on http://127.0.0.1:5000/")
    app.run(debug=True)
