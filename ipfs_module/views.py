import json
import shutil
from sqlite3 import converters
import django
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from django.core import serializers

from utils.error import error_msg
from .models import Images
import tempfile
import ipfshttpclient
import docker as dock
import logging
import os
import hashlib

logger = logging.getLogger(__name__)

host = "/dns/localhost/tcp/5001/http" if not os.getenv(
    "IPFS_HOST") else os.getenv("IPFS_HOST")
timeout = 3600 if not os.getenv(
    'IPFS_TIMEOUT') else int(os.getenv('IPFS_TIMEOUT'))

try:
    docker = dock.from_env()
except Exception as e:
    logging.warning("can't connect to docker host")
    exit(5)


@api_view(['POST'])
@parser_classes([JSONParser])
def all_images(request):
    try:
        all = Images.objects.all()
        converted = serializers.serialize('json', all)
    except Exception as e:
        return error_msg(str(e))
    return JsonResponse(data={"status": "success", "all": json.loads(converted)}, safe=False)


@api_view(['POST'])
@parser_classes([JSONParser])
def pull_an_image_by_hash(request):
    data = request.data
    path = tempfile.gettempdir()
    try:
        with ipfshttpclient.connect(addr=host, timeout=timeout) as ipfs:
            ipfs.get(data["hash"], target=path, compress=True)
    except Exception as e:
        return error_msg(str(e))
    load(data["hash"])
    return JsonResponse(data={"status": "success"}, safe=True)


def load(hash):
    path = os.path.join(tempfile.gettempdir(), hash)
    with open(path, mode="rb") as reader:
        docker.images.load(reader)
        logging.info(f"successfully read from file: {path}")
    remove_temp_file(path)


@api_view(['POST'])
@parser_classes([JSONParser])
def push_an_image(request):
    response = {}
    data = request.data
    try:
        image = docker.images.get("{}:{}".format(data["name"], data["tag"]))
    except Exception as e:
        logger.error(e)
        return error_msg(str(e))
    hashobject = hashlib.sha256()
    with tempfile.NamedTemporaryFile(mode="w+b", prefix="docker_", suffix=".tar", delete=False) as tmp:
        for chunk in image.save(chunk_size=2097152, named=True):
            tmp.write(chunk)
            hashobject.update(chunk)
    if not Images.objects.find_image_by_file_hash(file_hash=hashobject.hexdigest()).exists():
        try:
            with ipfshttpclient.connect(addr=host, timeout=timeout) as ipfs:
                res = ipfs.add(tmp.name, pin=True)
                pin_hash(data['name'], data['tag'])
                logger.info(ipfs.repo)
        except Exception as e:
            logger.error(e)
            return error_msg(str(e))
        try:
            Images.objects.create_image(name=data["name"], tag=data["tag"], ipfs_hash=res["Hash"], image_id=image.id,
                                        file_hash=hashobject.hexdigest(), pin=True, size=res["Size"])
            response = {"image": data["name"], "tag": data["tag"], "image_id": image.id, "ipfs_hash": res["Hash"],
                        "file": res["Name"], "size": res["Size"]}
        except django.db.utils.IntegrityError as e:
            logger.error(e)
            response["message"] = "you are already pushed this image"
        except Exception as e:
            logger.error(e)
            return error_msg(str(e))
    else:
        response["message"] = "you are already pushed this image"
    remove_temp_file(tmp.name)
    return JsonResponse(data=response, safe=True)


def pin_hash(imagename, tag):
    old_image = Images.objects.find_image_by_imagename_tag(imagename, tag)
    if old_image.exists():
        old_hash = Images.objects.get_ipfs_hash_by_imagename_tag(
            imagename, tag)
        try:
            with ipfshttpclient.connect(addr=host, timeout=timeout) as ipfs:
                ipfs.pin.rm(old_hash)
            Images.objects.delete_image_id(old_image.get().id)
        except Exception as e:
            logger.error(e)
            return error_msg(str(e))
    else:
        pass


def remove_temp_file(path):
    try:
        os.remove(path)
    except Exception as e:
        logger.error(e)
