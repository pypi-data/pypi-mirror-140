import time
import cv2
import pandas as pd
import mediapipe as mp


class VisionFi:
    # Tracking Configuration
    def __init__(self, static_image_mode=False, max_num_hands=2, min_detection_confidence=1,
                 min_tracking_confidence=0.95, seconds_sleep=0.25):
        self.seconds_sleep = seconds_sleep
        self.static_image_mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        # Initializing required functions and objects
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.static_image_mode, self.max_num_hands,
                                        self.min_detection_confidence, self.min_tracking_confidence)
        self.mpDraw = mp.solutions.drawing_utils

    # Checking for valid input for all passed attributes
    @staticmethod
    def valid_input(for_hands="All", clm_no="None", llm_no="None", ilm_no="None"):
        inp = {"for_hands": for_hands, "clm_no": clm_no, "llm_no": llm_no, "ilm_no": ilm_no}
        valid = {}
        for key, val in inp.items():
            if type(val) is str:
                if key == "for_hands":
                    if val == "All" or val == "all":
                        valid[key] = [0, 1]
                    else:
                        raise Exception(f"{key}: Invalid input is given")
                else:
                    if val == "All" or val == "all":
                        valid[key] = [k for k in range(0, 21)]
                    elif val == "None" or val == "none":
                        valid[key] = "None"
                    else:
                        raise Exception(f"{key}: Invalid String is given")

            elif type(val) is int:
                if key == "for_hands":
                    if 0 <= val <= 1:
                        valid[key] = [val]
                    else:
                        raise Exception(f"{key} can only be [0] or [1], where it stands for left hand or right hand")
                else:
                    if 0 <= val <= 20:
                        val = [val]
                        valid[key] = val
                    else:
                        raise Exception(f"{key} can be a positive integer between 0-20")

            elif type(val) is list:
                val = sorted(list(set(val)))
                if key == "for_hands":
                    for s in val:
                        if 0 <= s <= 1:
                            pass
                        else:
                            raise Exception(
                                f"{key} can only be [0, 1] or [1, 0], where [0, 1] is for left and right hand")
                    valid[key] = val
                else:
                    for s in val:
                        if 0 <= s <= 20:
                            pass
                        else:
                            raise Exception(f"{key} can be only list of positive integers between 0-20")
                    valid[key] = val

            else:
                raise Exception(f"{key}: Wrong input type, please recheck the passed arguments")

        return valid

    # Hand Detection Module
    def hand_detection(self, cap, valid):
        for_hands, clm_no, llm_no, ilm_no = valid['for_hands'], valid['clm_no'], valid['llm_no'], valid['ilm_no']
        # Capture the video frame by fps
        success, img = cap.read()

        # Check if their in no no webcam, if image or input file is not found.
        if not success:
            raise Exception("Camera is not found or accessible")

        # Flip the image (mirror the webcam input)
        img = cv2.flip(img, 1)

        # Dimension or shape of image
        height, width, channel = img.shape

        # Convert image to RGB Format
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Defining dataframe to hold landmark values
        # df = pd.DataFrame({"Hand0": [], "Hand1": []})
        df = pd.DataFrame()

        # Detecting No of hands in the source image/video
        results = self.hands.process(rgb_img)
        # if there is at least one or more hand founds we will return the hands and their landmarks
        if results.multi_handedness:
            # All hands Detected in the image
            # hands: Index of hand[0:Left, 1:Right]-[0:Any] If only one hand is identified or given in image
            hands = results.multi_handedness
            # Working for each hand requested
            for i in range(len(hands)):
                # coordinates_list: List of landmarks(0-20) coordinates(X,Y,Z) of each hand in the source image
                coordinates_list = results.multi_hand_landmarks
                # for hn_lms in coordinates_list:
                #     # Drawing lines between landmarks(20-dots) of each hand identified in the image/results
                #     self.mpDraw.draw_landmarks(img, hn_lms, self.mpHands.HAND_CONNECTIONS)
                index = hands[i].classification[0].index
                if index in for_hands:
                    if len(hands) >= 2:
                        coordinates_list = [coordinates_list[i]]

                    # Drawing requested circles on image
                    if clm_no != "None":
                        for circle_position in clm_no:
                            x = int(coordinates_list[0].landmark[circle_position].x * width)
                            y = int(coordinates_list[0].landmark[circle_position].y * height)
                            # Drawing circle on each given landmarkNo
                            cv2.circle(img, (x, y), 6, (255, 0, 255), cv2.FILLED)

                    # Drawing requested lines on image
                    if llm_no != "None":
                        x, y, counter = 0, 0, 0
                        for line_position in llm_no:
                            # Drawing line between each given landmarkNo
                            x1 = int(coordinates_list[0].landmark[line_position].x * width)
                            y1 = int(coordinates_list[0].landmark[line_position].y * height)
                            if counter == 0:
                                x, y = x1, y1
                                counter = 1
                            else:
                                cv2.line(img, (x, y), (x1, y1), (255, 0, 0), 4)
                                x, y = x1, y1

                    # Checking for requested landmarks
                    if ilm_no != "None":
                        # Returning df([j X, Y]) of requested ilmNo and their coordinates of each hand in image
                        landmark_list = []
                        for j in ilm_no:
                            # Converting 3D coordinate of lm in pixel distance of each landmarkNo
                            x = int(coordinates_list[0].landmark[j].x * width)
                            y = int(coordinates_list[0].landmark[j].y * height)
                            landmark_list.append([j, x, y])
                        df[f"Hand{index}"] = landmark_list

            time.sleep(self.seconds_sleep)
        else:
            time.sleep(self.seconds_sleep*2)

        return img, df
