# Import all the needed libraries
import os

import cv2
import numpy as np
import matplotlib.pyplot as plt
import easyocr
from Utility.util import BoxUtil

boxUtil = BoxUtil()

harcascade = "./Model/haarcascade_russian_plate_number.xml"

# Constants
model_cfg_path = 'Utility\Model\cfg\darknet-yolov3.cfg'
model_weights_path = 'Utility\Model\weights\model.weights'


class Detector:
    def __init__(self) -> None:
        pass

    def LP_Image_Detection(self, imagePath):
        # Load model
        yoloModel = cv2.dnn.readNetFromDarknet(
            model_cfg_path, model_weights_path)

        # Load image
        image = cv2.imread(imagePath)

        H, W, _ = image.shape

        # Convert image to 4D Blob
        blob = cv2.dnn.blobFromImage(
            image, 1 / 255, (416, 416), (0, 0, 0), True)

        # Uncomment the code below to the see the rsults of the blob
        # It converts the imagine into a 4D object, so to see it, we then convert it to a 2D object
        """
        image = np.reshape(blob, (blob.shape[2], blob.shape[3], blob.shape[1]))

        # Display the image using cv2.imshow
        cv2.imshow("Blob", image)
        cv2.waitKey(0)
        """

        # Get license plate detections from blob
        yoloModel.setInput(blob)

        # Extract the detections
        detections = boxUtil.get_outputs(yoloModel)

        # bboxes, class_ids, confidences
        bboxes = []
        class_ids = []
        scores = []

        # Goes through and extract the detection with the score
        for detection in detections:
            # [x1, x2, x3, x4, x5, x6, ..., x85]
            bbox = detection[:4]

            xc, yc, w, h = bbox
            bbox = [int(xc * W), int(yc * H), int(w * W), int(h * H)]

            bbox_confidence = detection[4]

            class_id = np.argmax(detection[5:])
            score = np.amax(detection[5:])

            bboxes.append(bbox)
            class_ids.append(class_id)
            scores.append(score)

        # Apply nms
        bboxes, class_ids, scores = boxUtil.NMS(bboxes, class_ids, scores)

        # Plot region of interest
        for bbox_, bbox in enumerate(bboxes):
            xc, yc, w, h = bbox

            cv2.putText(image,
                        "License Plate",
                        (int(xc - (w / 2)) + 30, int(yc + (h / 2) + 55)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        4)

            license_plate = image[int(yc - (h / 2)):int(yc + (h / 2)),
                                  int(xc - (w / 2)):int(xc + (w / 2)), :].copy()

            image = cv2.rectangle(image,
                                  (int(xc - (w / 2)), int(yc - (h / 2))),
                                  (int(xc + (w / 2)), int(yc + (h / 2))),
                                  (0, 255, 0),
                                  thickness=5)

            license_plate_gray = cv2.cvtColor(
                license_plate, cv2.COLOR_BGR2GRAY)

            _, license_plate_edged = cv2.threshold(
                license_plate_gray, 64, 255, cv2.THRESH_BINARY_INV)

            results = self.LP_Reader_Thresh(
                license_plate, license_plate_gray, license_plate_edged)

            print("License Plate: ", results[1])
            print("Confidence Value: %", (results[0] * 100))
            print("Image Used: ", results[2])

            plt.figure()
            plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            plt.figure()
            plt.imshow(cv2.cvtColor(license_plate, cv2.COLOR_BGR2RGB))

            plt.figure()
            plt.imshow(cv2.cvtColor(license_plate_gray, cv2.COLOR_BGR2RGB))

            plt.figure()
            plt.imshow(cv2.cvtColor(license_plate_edged, cv2.COLOR_BGR2RGB))

        plt.show()

    def LP_Video_Detection_2(self, videoPath):

        # Load model
        net = cv2.dnn.readNetFromDarknet(model_cfg_path, model_weights_path)

        cap = cv2.VideoCapture(videoPath)

        if (cap.isOpened() == False):
            print("Error Opening Video File: " + videoPath)
            return

        (success, image) = cap.read()

        while success:

            H, W, _ = image.shape

            # convert image
            blob = cv2.dnn.blobFromImage(
                image, 1 / 255, (416, 416), (0, 0, 0), True)

            # get detections
            net.setInput(blob)

            detections = boxUtil.get_outputs(net)

            # bboxes, class_ids, confidences
            bboxes = []
            class_ids = []
            scores = []

            for detection in detections:
                # [x1, x2, x3, x4, x5, x6, ..., x85]
                bbox = detection[:4]

                xc, yc, w, h = bbox
                bbox = [int(xc * W), int(yc * H), int(w * W), int(h * H)]

                bbox_confidence = detection[4]

                class_id = np.argmax(detection[5:])
                score = np.amax(detection[5:])

                bboxes.append(bbox)
                class_ids.append(class_id)
                scores.append(score)

            # apply nms
            bboxes, class_ids, scores = boxUtil.NMS(bboxes, class_ids, scores)

            for bbox_, bbox in enumerate(bboxes):
                xc, yc, w, h = bbox

                """
                cv2.putText(img,
                            class_names[class_ids[bbox_]],
                            (int(xc - (w / 2)), int(yc + (h / 2) - 20)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            7,
                            (0, 255, 0),
                            15)
                """

                license_plate = image[int(yc - (h / 2)):int(yc + (h / 2)),
                                      int(xc - (w / 2)):int(xc + (w / 2)), :].copy()

                cv2.rectangle(image,
                              (int(xc - (w / 2)), int(yc - (h / 2))),
                              (int(xc + (w / 2)), int(yc + (h / 2))),
                              (0, 255, 0),
                              thickness=1)

                license_plate_gray = cv2.cvtColor(
                    license_plate, cv2.COLOR_BGR2GRAY)

                _, license_plate_edged = cv2.threshold(
                    license_plate_gray, 64, 255, cv2.THRESH_BINARY_INV)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            cv2.imshow("Result", image)

            (success, image) = cap.read()

        cv2.destroyAllWindows()

        return

    def LP_Video_Detection_3(self, videoPath):
        min_area = 500
        count = 0
        cap = cv2.VideoCapture(videoPath)
        plate_cascade = cv2.CascadeClassifier(harcascade)

        if (cap.isOpened() == False):
            print("Error Opening Video File: " + videoPath)
            return

        (success, image) = cap.read()

        while success:

            img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

            for (x, y, w, h) in plates:
                area = w * h

                if area > min_area:
                    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(image, "Number Plate", (x, y-5),
                                cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)

                    img_roi = image[y: y+h, x:x+w]
                    cv2.imshow("License Plate", img_roi)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            cv2.imshow("Result", image)

            (success, image) = cap.read()

        cv2.destroyAllWindows()

        return

    def LP_Reader_Thresh(self, plate, gray, thresh):

        reader = easyocr.Reader(['en'])

        plate_output = reader.readtext(plate)
        gray_output = reader.readtext(gray)
        thresh_output = reader.readtext(thresh)

        highest_score = 0.0
        text = ""
        lp_used = ""

        for out in plate_output:
            text_bbox, text, text_score = out
            highest_score = text_score
            text = text
            lp_used = "License Plate (Colored)"

        for out in gray_output:
            text_bbox, text, text_score = out
            if text_score > highest_score:
                highest_score = text_score
                text = text
                lp_used = "License Plate (Gray)"

        for out in thresh_output:
            text_bbox, text, text_score = out
            if text_score > highest_score:
                highest_score = text_score
                text = text
                lp_used = "License Plate (Edged)"

        return highest_score, text, lp_used
