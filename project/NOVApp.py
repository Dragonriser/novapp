__author__ = 'emontenegro'

from ImageProcessor import ImageProcessor

if __name__ == "__main__":
    source_file = "./test_case.png"
    try:
        image_processor = ImageProcessor(source_file)
        image_processor.start_processing()
    except Exception, err:
        print "Error: %s\n" %str(err)