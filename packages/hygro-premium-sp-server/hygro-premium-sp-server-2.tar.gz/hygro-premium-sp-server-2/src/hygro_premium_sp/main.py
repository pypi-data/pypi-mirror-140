#!/usr/bin/env python2
import argparse
import os

from flask import Flask, request, send_from_directory
from hygro_premium_sp import humidity_extractor
from hygro_premium_sp.humidity_extractor import EasyHomeHygroPremiumSP, Products
from flask_cors import CORS

PORT = 21000


app = Flask(__name__, static_folder=None)
CORS(app, resource={r"/*": {"origins": "*"}})
configuration = humidity_extractor.load_configuration()


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def web(path):
    app.logger.info("PATH: {}".format(path))
    return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public'), path)


@app.route("/api/status")
def status():
    current_speed = EasyHomeHygroPremiumSP.by_ratio(configuration.velocity_ratio)

    return {
        'speeds': [speed.name for speed in EasyHomeHygroPremiumSP.all()],
        'available_speeds': [speed.name for speed in EasyHomeHygroPremiumSP.available_speeds()],
        'current': {
            'speed': current_speed.name,
            'ratio': round(configuration.velocity_ratio, ndigits=2),
            'real_ratio': round(EasyHomeHygroPremiumSP.ratio_for(current_speed), ndigits=2)
        }
    }


@app.route("/doc")
def dock():
    return '''
    GET /configuration -> {"velocity_ratio": float}</br>
    POST /configure -> {"velocity_ratio": 0.0 - 1.0}</br>
    POST /configure -> {"velocity_percentage": 0 - 100}</br>
    POST /configure -> {"velocity": ("off" | "quiet" | "very low" | "normal" | "high" | "very high" | "maximum") }</br>
    POST /configure -> {"product": ("default" | "EasyHome Hygro PremiumSP" | "Solid state relay EasyHome Hygro PremiumSP") }</br>
    '''


@app.route("/api/configuration", methods=["GET"])
def get_configuration():
    return {
        'velocity_ratio': configuration.velocity_ratio,
        'product': configuration.product.NAME
    }


@app.route("/api/configure", methods=["POST"])
def configure():
    request_json = request.get_json()

    if request_json is None:
        return '', 400

    if 'velocity_percentage' in request_json:
        request_json['velocity_ratio'] = request_json['velocity_percentage'] / 100.0

    if 'velocity' in request_json:
        speed = EasyHomeHygroPremiumSP.by_name(request_json['velocity'])
        request_json['velocity_ratio'] = EasyHomeHygroPremiumSP.ratio_for(speed)

    if 'product' in request_json:
        configuration.product = Products.by_name(request_json['product']) or Products.Default

    if 'velocity_ratio' not in request_json:
        return '', 200

    velocity_ratio = request_json['velocity_ratio']
    if velocity_ratio > 1:
        velocity_ratio = 1

    if velocity_ratio < 0:
        velocity_ratio = 0

    configuration.velocity_ratio = velocity_ratio
    humidity_extractor.set_velocity(velocity_ratio)
    humidity_extractor.save_configuration(configuration)

    return "", 200


argument_parser = argparse.ArgumentParser()
argument_parser.add_argument('--product', '-p', dest='product', choices=['default', 'solid state'])


def main():
    arguments = argument_parser.parse_args()

    if arguments.product:
        configuration.product = Products.by_name(arguments.product) or Products.Default
        humidity_extractor.save_configuration(configuration)

    print(configuration)
    humidity_extractor.start(configuration)
    app.run('0.0.0.0', port=PORT)


if __name__ == '__main__':
    main()
