import matplotlib.pyplot as plt
import numpy as np
import cv2
import os

def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def image_exif_data(image_path):
    data = dict();
    # Initialize with 0 values
    data["lat"] = 0
    data["long"] = 0
    data["creation_time"] = ""
    from exif import Image
    try:
        with open(image_path, 'rb') as src:
            img = Image(src)
            if img.has_exif:
                try:
                    lat = decimal_coords(img.gps_latitude, img.gps_latitude_ref)
                    long = decimal_coords(img.gps_longitude, img.gps_longitude_ref)
                    # coords = (lat, long)
                    data["lat"] = round(lat, 19)
                    data["long"] = round(long, 19)
                    data["creation_time"] = img.datetime_original
                    # print("  coordinates are: ", data)
                    # print("  photo datetime_original :", img.datetime_original)
                except AttributeError:
                    coords = (0, 0)
                    # print("  No Coordinates")
            else:
                print()
                # print("  The Image has no EXIF information - ", image_path)
    except ValueError:
        print("  ERROR occured while opening %s for exif data extraction", image_path)
    return data


# function to calculate distance between two GPS coordinates
def calc_distance(coords1, coords2):
    lat1, lon1 = coords1
    lat2, lon2 = coords2
    radius = 6371  # radius of Earth in km
    dlat = np.radians(lat2-lat1)
    dlon = np.radians(lon2-lon1)
    a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(np.radians(lat1)) \
        * np.cos(np.radians(lat2)) * np.sin(dlon/2) * np.sin(dlon/2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    distance = radius * c
    return distance

# function to display the closest images

def show_closest_images(event):
    title = event.inaxes.title.get_text()
    print("title : ", title)
    numbers = res = [int(i) for i in title.split() if i.isdigit()]
    print("string :", numbers)
    image_index = numbers[0]
    print("index :", image_index)
    selected_image = images[image_index]
    selected_coords = gps_coords[image_index]
    print("-- selected_coords :", selected_coords)

    distances = [calc_distance(selected_coords, coords) for coords in gps_coords]
    print("--distances: ", distances)

    #selected_image_timestamp = image_exif_data(image[image_index])['Original Creation Time']

    # calculate the distances between the selected image and all other images
    #distances1 = [calc_distance(selected_coords, gps_coords[i]) for i in range(len(gps_coords))]
    #print("--distances1:", distances1)

    # find the indices of the closest images
    closest_image_indices = [i for i in range(len(distances)) if distances[i] == min(distances)]

    # loop through the closest image indices to compare timestamps
    #closest_images_with_timestamp = []
    #for index in closest_image_indices:
    #    closest_image_timestamp = image_exif_data(image[index])['Original Creation Time']
    #    time_difference = abs((selected_image_timestamp - closest_image_timestamp).total_seconds())
    #    if time_difference < 360:  # within 1 hour
    #        closest_images_with_timestamp.append(index)

    # use the closest image indices to show the closest images
    #closest_images = [image[i] for i in closest_images_with_timestamp]


    # exit if no images found in the directory
    import os, datetime

    # filenames.append(file_name)
    timestamp = os.path.getctime(file_name_full)
    dt = datetime.datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y, %H:%M:%S")
    #creation_date = dt.split()[0]
    #creation_time = dt.split()[1]

    import pandas as pd
    # Create a dataFrame using dictionary
    df = pd.DataFrame({"Image": [file_name], "date and time": [dt]})
    # print(df)
    exif_data = image_exif_data(file_name_full)
    # if exif data has original file creation time then use it instead of datatime using os.path.getcttime

    if exif_data["creation_time"]:
        creation_date = exif_data["creation_time"].split()[0]
        creation_time = exif_data["creation_time"].split()[1]
    # find the closest time of creation.
    dt = datetime.datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y,%H:%M:%S")
    print(dt)

    # find the indices of the closest images
    sorted_distances= np.argsort(distances)
    print("sorted distances:", sorted_distances)
    closest_indices = sorted_distances[1:9]  # exclude the selected image
    closest_indices = [int(i) for i in closest_indices]

    #closest_indices = int('sorted_distances')
    print("--closest distances", closest_indices)

    # plot the selected image and the closest images
    fig, ax = plt.subplots(1, len(closest_indices) + 1, figsize=(20, 20))

    print("--fig in show_closest_images: ", fig)
    print("--ax in show_closest_images: ", ax)
    ax[0].imshow(selected_image)
    ax[0].set_title("Selected Image")
    for i, closest_index in enumerate(closest_indices):
        print("i, closest_index: ", i, closest_index)
        #ax[i + 1].imshow(images[closest_indices])
        ax[i + 1].imshow(images[closest_index])
        ax[i + 1].set_title(f"Closest Image {i + 1}")
    plt.show()


directory = 'images'
gps_coords = []  # load the GPS coordinates for each image
images = []

for file_name in os.listdir(directory):
    file_name_full = os.path.join(directory, file_name)
    if not os.path.isfile(file_name_full):
        continue
    if file_name.endswith('.jpg'):
        img = cv2.imread(os.path.join(directory, file_name), cv2.IMREAD_GRAYSCALE)
        if img is not None:
            images.append(img)
    exif_data = image_exif_data(file_name_full)

    # append a row with filename, date, time and lat, long values
    print("-- image %s coords : ", file_name, [exif_data["lat"], exif_data["long"]])
    gps_coords.append([exif_data["lat"], exif_data["long"]])

if not images:
    print("No images found in the directory.")
    exit()

# plot the images and allow user to click on an image
fig, ax = plt.subplots(1, len(images), figsize=(35, 30))
for i, image in enumerate(images):
    ax[i].imshow(image)
    ax[i].set_title(f" {i + 1}")

# connect the click event to the show_closest_images function
cid = fig.canvas.mpl_connect('button_press_event', lambda event: show_closest_images(event))
plt.show()

