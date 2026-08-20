from flask_restful import Resource, Api
from flask import request, jsonify
from .models import *

api=Api()

class SubjectApi(Resource):

    #Reading of data
    def get(self):
        subjects = Subject.query.all()
        subjects_json=[]
        for subject in subjects:
            subjects_json.append({'s_id':subject.s_id,'sname':subject.sname,'s_description':subject.s_description})
        
        return {"subjects":subjects_json}, 200
    
    #Creating data
    def post(self):
        if not request.is_json:
            return {"error": "Invalid content type"}, 415
        
        data = request.get_json()
        sname = data.get("sname")
        s_description = data.get("s_description")
        
        if not sname or not s_description:
            return {"error": "Missing required fields: 'sname' and 's_description'"}, 400
        
        new_subject = Subject(sname = sname, s_description = s_description)
        db.session.add(new_subject)
        db.session.commit()
        
        return {"message":"New subject added!"},201

    #Updating
    def put(self,s_id):
        if not request.is_json:
            return {"error": "Invalid content type"}, 415
        
        subject = Subject.query.filter_by(s_id = s_id).first()
        if subject:
            subject.sname = request.json.get("sname")
            subject.s_description = request.json.get("s_description")
            db.session.commit()
            return {"message":"Show updated!"},200
        
        return {"message":"Subject id not found!"},404

    #Delete data
    def delete(self,s_id):
        subject = Subject.query.filter_by(s_id = s_id).first()
        if subject:
            db.session.delete(subject)
            db.session.commit()
            return {"message":"Subject deleted!"},200
        
        return {"message":"Subject id not found!"},404
    

api.add_resource(SubjectApi,"/api/subjects","/api/subject","/api/edit_subject/<int:s_id>","/api/delete_subject/<int:s_id>")