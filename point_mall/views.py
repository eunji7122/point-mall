from django.http import HttpResponse
from rest_framework.decorators import api_view


@api_view(['GET'])
def image_view(request, file_name):
    image_data = open('media/uploads/item_images/' + file_name, 'rb').read()

    ext = file_name.split('.')[1]
    return HttpResponse(image_data, content_type='image/' + ext)

@api_view(['GET'])
def root_view(request):
    return HttpResponse('Point Mall Django API')