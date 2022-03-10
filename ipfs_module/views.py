import django
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from django.http import JsonResponse

from utils.error import error_msg
from .models import Images
import tempfile
import ipfshttpclient
import docker as dock
import logging
import os

logger = logging.getLogger(__name__)

host = "/dns/localhost/tcp/5001/http" if not os.getenv(
    "IPFS_HOST") else os.getenv("IPFS_HOST")

# try:
#     host = os.getenv("IPFS_HOST") | "/dns/localhost/tcp/5001/http "
#     ipfs = ipfshttpclient.connect(addr=host)
# except ipfshttpclient.exceptions.ConnectionError:
#     logging.warning("can't connect to ipfs host")
#     exit(5)

try:
    docker = dock.from_env()
except Exception as e:
    logging.warning("can't connect to docker host")
    exit(5)


@api_view(['POST'])
@parser_classes([JSONParser])
def pull_an_image_by_name(request):
    data = request.data
    hash = ""
    try:
        hash = Images.objects.get(imagename=data["name"], tag=data["tag"]).hash
        print(hash)
    except Images.DoesNotExist:
        logger.error("image does not exist locally")
        # logic for global search
    except Exception as e:
        logger.error(e)
        return error_msg(str(e))
    path = tempfile.gettempdir()
    if hash:
        try:
            with ipfshttpclient.connect(addr=host) as ipfs:
                ipfs.get(hash, target=path, compress=True)
        except Exception as e:
            return error_msg(str(e))
        load(hash)
        return JsonResponse(data={"status": "success"}, safe=True)
    else:
        return error_msg("can not find image")


@api_view(['POST'])
@parser_classes([JSONParser])
def pull_an_image_by_hash(request):
    data = request.data
    path = tempfile.gettempdir()
    try:
        with ipfshttpclient.connect(addr=host) as ipfs:
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


@api_view(['POST'])
@parser_classes([JSONParser])
def push_an_image(request):
    data = request.data
    try:
        image = docker.images.get("{}:{}".format(data["name"], data["tag"]))
    except Exception as e:
        logger.error(e)
        return JsonResponse({"status": "failed", "message": str(e)})
    with tempfile.NamedTemporaryFile(mode="w+b", prefix="docker_", suffix=".tar", delete=False) as tmp:
        for chunk in image.save(chunk_size=2097152, named=True):
            tmp.write(chunk)
    try:
        with ipfshttpclient.connect(addr=host) as ipfs:
            res = ipfs.add(tmp.name)
            print(ipfs.repo)
    except Exception as e:
        logger.error(e)
        return JsonResponse({"status": "failed", "message": str(e)})
    json_hash = {"image": data["name"], "tag": data["tag"], "hash": res["Hash"],
                 "file": res["Name"], "size": res["Size"]}
    try:
        image = Images.objects.create(
            imagename=data["name"], tag=data["tag"], hash=res["Hash"], size=res["Size"])
        image.save()
    except django.db.utils.IntegrityError as e:
        logger.error(e)
        json_hash["message"] = "you are already pushed this image"
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"status": "failed", "message": str(e)})
    return JsonResponse(data=json_hash, safe=True)
