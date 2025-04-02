"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, json
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# create the jackson family object
jackson_family = FamilyStructure("Jackson")

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/members', methods=['GET'])
def get_members():

    # this is how you can use the Family datastructure by calling its methods
    try:
        members = jackson_family.get_all_members()

        return jsonify(members), 200

    except Exception as e:
        return "This family doesn't exists", 404


@app.route('/member/<int:member_id>', methods=['GET'])
def get_member(member_id):
    try:
        member = jackson_family.get_member(member_id)

        if member is None:
            return jsonify({"error": "Member not found"}), 404

        response_body = {
            "id": member.get('id'),
            "first_name": member.get('first_name'),
            "age": member.get('age'),
            "lucky_numbers": member.get('lucky_numbers'),
        }
        return jsonify(response_body), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/member/<int:id>', methods=['DELETE'])
def delete_member(id):
    if request.method == 'DELETE':
        try:
            member_deleted = jackson_family.delete_member(id)

            if member_deleted:
                return jsonify({"done": True}), 200

            return jsonify({"error": "Member couldn't be deleted"}), 400

        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/member', methods=['POST'])
def add_member():
    if request.method == 'POST':
        try:
            data = request.get_json()

            if not data or "first_name" not in data or data.get("age", 0) <= 0:
                return jsonify({"error": "There is some data missing or wrong, please try again."}), 400

            response_body = jackson_family.add_member(data)

            return jsonify({
                "id": response_body.get("id"),
                "first_name": response_body.get("first_name"),
                "age": response_body.get("age"),
                "lucky_numbers": response_body.get("lucky_numbers"),
            }), 200

        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
