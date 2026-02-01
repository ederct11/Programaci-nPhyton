
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import laptopItem

# Create your views here.
@api_view(['GET'])
def get_laptops(request):
    RAM = request.GET.get("RAM",0)
    portatiles  = list(laptopItem.objects(RAM__gte=RAM).order_by('-creation_date'))
    portatiles_seriazable = list(map(lambda f_item: f_item.as_dic(),portatiles))
    return Response(portatiles_seriazable, status=200)


@api_view(['POST'])
def post_laptop(request):
    body = request.data
    new_laptop = laptopItem(
        name = body['name'],
        RAM = body['RAM'],
        SSD = body['SSD'],
        Price = body['Price'],
        material = body['material'])
    new_laptop.save()    
    return Response(new_laptop.as_dic(), status=201)


def get_laptop(_,id):
    try:
        laptop =  laptopItem.objects.get(id=id)
        return Response(laptop.as_dic(), status= 200)
    except laptopItem.DoesNotExist:
        return Response({"message": f"laptop {id} not exist"}, status= 404)
    

def delete_laptop(_,id):
    try:
        laptop =  laptopItem.objects.get(id=id)
        data = laptop.as_dic()
        laptop.delete()
        return Response(data, status= 200)
    except laptopItem.DoesNotExist:
        return Response({"message": f"laptop {id} not exist"}, status= 204)

 
def patch_laptop(_, id, body):
    price = body.get("price")
    name = body.get("name")
    found = laptopItem.objects(id=id).first()
    if found is not None:
        if price is not None:
            found.Price = price
        if name is not None:
            found.name = name
        found.save()
        found.reload()
        return Response(found.as_dic(), status=200)
    else:
        return Response({"message": "laptop with " + id + " not found"}, status=404)

    
@api_view(["GET","DELETE","PATCH"])
def handle_one_laptop(request,id):
    if request.method== "GET":
        return get_laptop(request,id)
    elif request.method== "PATCH":
        return patch_laptop(request,id, request.data)
    else:
        return delete_laptop(request,id)
    

@api_view(["GET"])
def v2(_,id):
    laptop =  laptopItem.objects.get(id=id)
    data = laptop.as_dic()
    data["version"] = "V2"
    return Response(data, status= 200)