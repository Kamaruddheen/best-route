from django.shortcuts import render
from django.contrib import messages
from .forms import AddDocumentCSVForm

import requests
import csv
import io


def homepage(request):
    csv_form = AddDocumentCSVForm()
    initial = []
    # print("Entering...")

    context = {
        'csv_form': csv_form,
        'title': [],
        'initial': initial
    }

    if request.method == "POST" and request.POST.get('add_csv_form', False):
        # print("We are in....")
        csv_form = AddDocumentCSVForm(request.POST, request.FILES)
        if csv_form.is_valid():
            csv_file = request.FILES['input_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Not a csv file')
            else:
                # print(csv_file)
                io_string = io.StringIO(csv_file.read().decode())
                csv_reader = csv.DictReader(io_string)
                # print(csv_reader.fieldnames)
                for i, v in enumerate(csv_reader.fieldnames):
                    csv_reader.fieldnames[i] = v.upper()
                    if csv_reader.fieldnames[i] == "DISTANCE":
                        csv_reader.fieldnames[i] += " (km)"
                    if csv_reader.fieldnames[i] == "TIME":
                        csv_reader.fieldnames[i] += " (m)"
                # print(csv_reader.fieldnames)
                for row in csv_reader:
                    # start = list(map(float, row['START'].strip().split(',')))
                    # end = list(map(float, row['END'].strip().split(',')))                    
                    distance, time = send_api_request(row['START'], row['END'])

                    initial.append((row['START'], row['END'],
                                    distance, time))

                    # print(distance, time)

        context = {
            'csv_form': csv_form,
            'title': csv_reader.fieldnames,
            'initial': initial
        }

    return render(request, 'index.html', context=context)


def find_coordinates(str):
    URL = "https://api.mapbox.com/geocoding/v5/mapbox.places/{}.json".format(
        str)

    # defining a pfarams dict for the parameters to be sent to the API
    PARAMS = {
        'limit': 1,
        'worldview': 'in',
        'country': 'in',
        'access_token': 'pk.eyJ1IjoiLS1rYW1hci0tIiwiYSI6ImNrdTN6dDV5NzE5dzkycG8xdHNjbWkxZ2oifQ._Th_HdJY6BcVKrzj-UsebA',
    }

    # Setting verify to False will diable SSL certificate
    r = requests.get(url=URL, params=PARAMS, verify=False)

    raw_data = r.json()

    # Checking wheather any route is availabe or not
    try:
        if raw_data['message'] == "Not Found":
            return "NA"
    except KeyError:
        pass

    # Checking wheather route is empty or not
    try:
        if raw_data['features'] == []:
            return "NA"
    except KeyError:
        pass

    data = raw_data['features'][0]['geometry']['coordinates']

    return data


def send_api_request(start1, end1):

    start = find_coordinates(start1)
    end = find_coordinates(end1)

    print(start[0], start[1], end[0], end[1])

    if start == "NA" or end == "NA":
        return ["NA", "NA"]

    URL = "https://api.mapbox.com/directions/v5/mapbox/driving/{},{};{},{}".format(
        start[0], start[1], end[0], end[1]
    )

    # defining a params dict for the parameters to be sent to the API
    PARAMS = {
        'alternatives': 'true',
        'access_token': 'pk.eyJ1IjoiLS1rYW1hci0tIiwiYSI6ImNrdTN6dDV5NzE5dzkycG8xdHNjbWkxZ2oifQ._Th_HdJY6BcVKrzj-UsebA',
    }

    # Setting verify to False will diable SSL certificate
    r = requests.get(url=URL, params=PARAMS, verify=False)

    raw_data = r.json()

    # Checking wheather any route is availabe or not
    if raw_data['code'] == "NoRoute":
        print(raw_data['message'])
        return [raw_data['message'], raw_data['message']]

    # Initializing distance and time
    distance = raw_data['routes'][0]['distance']
    time = raw_data['routes'][0]['duration']

    count = 1
    while True:
        try:
            if distance > raw_data['routes'][count]['distance']:
                distance = raw_data['routes'][count]['distance']
                time = raw_data['routes'][count]['duration']
            count += 1
        except IndexError:
            break

    return round(distance/1000, 2), int(round(time/60, 0))


# print(send_api_request([80.27652439482927, 13.082065251440497],
#                        [80.14921817663134, 13.11914723702597]))
