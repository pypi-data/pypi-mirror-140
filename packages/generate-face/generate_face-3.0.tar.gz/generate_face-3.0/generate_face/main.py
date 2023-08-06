from requests import get
from os import getcwd, path, makedirs
from time import sleep
dir = getcwd()
# create class


class FaceGenerator:
    def __init__(self, total):
        self.total = total

    def gen_face(self):
        path_complete = dir+"\\dataset"
        isExist = path.exists(path_complete)
        if (isExist):
            print("[INFO] Downloading", self.total, "face images...")
            # loop to download all
            for i in range(int(self.total)):
                response = get("https://thispersondoesnotexist.com/image")
                with open(dir+"\\dataset\\"+str(i)+".png", "wb") as f:
                    f.write(response.content)
                #print("Downloaded photo {}".format(i))
                sleep(0.1)
            print("[INFO] Done downloading", self.total,
                  "face images, images is sourced from https://thispersondoesnotexist.com/image")
            print("[INFO] downloaded to", path_complete)
        else:
            makedirs(path_complete)
            print("[INFO] Downloading", self.total, "face images...")
            # loop to download all
            for i in range(int(self.total)):
                response = get("https://thispersondoesnotexist.com/image")
                with open(dir+"\\dataset\\"+str(i)+".png", "wb") as f:
                    f.write(response.content)
                #print("Downloaded photo {}".format(i))
                sleep(0.5)
            print("[INFO] Done downloading", self.total,
                  "face images, images is sourced from https://thispersondoesnotexist.com/image")
            print("[INFO] downloaded to", path_complete)


""" test = FaceGenerator(1)
test.gen_face() """
