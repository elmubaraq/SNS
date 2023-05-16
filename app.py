from flask import Flask,redirect,url_for,render_template,request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField, FileField, DateField
from wtforms.validators import Length, EqualTo, DataRequired, Email, ValidationError
from python_graphql_client import GraphqlClient

import asyncio
from dotenv import load_dotenv
import os

class message(FlaskForm):
    Topic = StringField(label='Topic:', validators=[DataRequired()])
    Body = TextAreaField(label='Message Body', validators=[Length(max=160),DataRequired()])
    PhoneNumber = StringField(label='Phone Number', validators=[DataRequired()])
    Submit = SubmitField(label='Send Message')


load_dotenv()
ENDPOINT= os.environ['API_ENDPOINT']
API_EMAIL= os.environ['API_AUTH_EMAIL']
API_PASSWORD= os.environ['API_AUTH_PASSWORD']
           
app=Flask(__name__)
@app.route('/',methods=['GET','POST'])
def home():
    client = GraphqlClient(endpoint=ENDPOINT)
    query= """mutation($email: String! $password: String!){
    vendorAuthenticationAlt(
    email: $email
    password: $password
     ){
    token
    refreshToken
    error
    message
        }
    }"""
    variables = {"email":API_EMAIL ,
            "password":API_PASSWORD}
    

    data = asyncio.run(client.execute_async(query = query, variables=variables))
    token = data["data"]["vendorAuthenticationAlt"]["token"]
    
    form = message()
    if form.validate_on_submit():
        query = """
        mutation($ficsmessageinput: FicsMessageInput! $token: String!)
        {
        ficsSMSOut(
            ficsmessageinput:$ficsmessageinput
            token : $token
            
        ){
            error
            successMsg
            responseCat
            
            

        }
        }
        """

        variables = {"ficsmessageinput":{"destinations":form.PhoneNumber.data,
        "messageSubject":form.Topic.data,
        "messageBody":form.Body.data},
        "token": token}
        

        data = asyncio.run(client.execute_async(query = query, variables=variables))
        print(data)  # => {'data': {'country': {'code': 'CA', 'name': 'Canada'}}}
        flash(data['data']['ficsSMSOut']['responseCat'], category="info")
        #PhoneList=form.PhoneNumber.data.split(',')
        #print(PhoneList)

        # Handle POST Request here
        return render_template('index.html', form=form)
    return render_template('index.html',form =form)

app.config["SECRET_KEY"]='bdfbcdc502722bc56058y1d0'
if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(port=5000,debug=True)