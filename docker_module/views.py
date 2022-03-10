from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
import docker as dock
import logging

from utils.error import error_msg

logger = logging.getLogger(__name__)

try:
    docker = dock.from_env()
    print(docker)
except Exception as e:
    logger.error("can't connect to docker host")
    # exit(5)


@api_view(['GET'])
def list_of_images(request):
    queryset = docker.images.list()
    data = []
    for query in queryset:
        data.append(query.attrs)
    return JsonResponse(data=data, safe=False)


@api_view(['GET'])
@parser_classes([JSONParser])
def get_an_image(request):
    data = request.data
    try:
        image = docker.images.get(data["name"])
        attributes = image.attrs
        return JsonResponse(data=attributes, safe=False)
    except Exception as e:
        logger.error(e)
        return error_msg(str(e))


@api_view(['DELETE'])
@parser_classes([JSONParser])
def delete_an_image(request):
    data = request.data
    try:
        docker.images.remove(data["name"])
        return JsonResponse(data={"status": "deleted", "image name": data})
    except Exception as err:
        logger.error(data)
        return error_msg({"image_name": data["name"], "error": str(err)})
