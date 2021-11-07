from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from caesarcipher import CaesarCipher
import pprint
import os
from twilio.rest import Client
import pymongo
import shortuuid

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/cipherIt", methods=['GET', 'POST'])
@cross_origin()
def cipherIt():
    if request.method == 'POST':
        data = request.json
        pprint.pprint(data)
        #print(data["messages"])
        try:
            for ele in data["messages"]:
                print(ele["text"])
                ele["text"] = CaesarCipher(ele["text"],offset=14).encoded
                print(ele["text"])
            return jsonify(data)
        except Exception as e:
            print(e)
            return jsonify({"error": "Invalid JSON"})
    return {"status":"ok"}

@app.route("/verify",methods=['GET','POST'])
@cross_origin()
def verify():
    client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.wonbr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client['Agent']
    collection = db["AgentEmail"]
    if request.method == 'POST':
        data = request.json
        x=collection.find_one({"user":data["email"]})
        account_sid = 'AC9807e8964cc05794c3de4f37c190247b'
        auth_token = 'c7406246fbcfd184414bb374919946cf'
        client = Client(account_sid, auth_token)
        otp = shortuuid.ShortUUID().random(length=4)

        message = client.messages.create(
                                    body=f'Your OTP is *{otp}* Please enter to verify',
                                    from_='whatsapp:+14155238886',
                                    to=f'whatsapp:{x["mobile"]}'
                                )
        print(message.sid)
    return {"otp":otp}


@app.route("/updatePh",methods=['GET','POST'])
@cross_origin()
def updatePh():
    client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.wonbr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client['Agent']
    collection = db["AgentEmail"]
    if request.method == 'POST':
        data=request.json
        print(data["mobile"])
        print(data["user"])
        x=collection.find_one({"user":data["user"]})
        if x is None:
            collection.insert_one({
                "user":data["user"],
                "mobile":data["mobile"]
            })
        else:
            collection.update_one({"user":data["user"]},{"$set":{"mobile":data["mobile"]}})

    return {"status":200}

if __name__ == "__main__":
    app.run(debug=True)