import json

def import_ingredient(path_for_file, model):
    f = open(path_for_file, 'r')
    data = json.load(f)
    for i in data:
        model.objects.create(
            name=i['name'],
            measurement_unit=i['measurement_unit']
        )
    f.close()
