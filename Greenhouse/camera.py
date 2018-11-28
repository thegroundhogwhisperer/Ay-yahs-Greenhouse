# Camera.py writes a high resolution image and a low
# resolution image to the web servers root folder
import picamera
import time

cameraImageOutputFilenameLow = '/var/www/html/greenhouselow.jpg'
cameraImageOutputFilenameHigh = '/var/www/html/greenhousehigh.jpg'

# capture camera image subroutine
def captureCameraStillImage():

    camera = picamera.PiCamera()
    camera.resolution = (3280, 2464)
    camera.shutter_speed = 1000000
    camera.iso = 800
    camera.start_preview()
    time.sleep(3)
    camera.exposure_mode = 'off'
    camera.capture(cameraImageOutputFilenameHigh)
    camera.stop_preview()
    camera.capture(cameraImageOutputFilenameLow, resize=(320, 240))
    camera.stop_preview()

captureCameraStillImage()

