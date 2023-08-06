def vision():
    import cv2
    import time
    import VisionFi as vF
    import Volume
    import Drag_Drop
    
    # Initialising object for model
    model = vF.VisionFi(seconds_sleep=0)
    
    # Define a video capture object - default source integrated web camera(0)
    cap = cv2.VideoCapture(0)
    
    
    def cv_show(img, previous_time):
        # Resizing frame and display the resulting frame
        cv2.namedWindow("VisionFi", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("VisionFi", 640, 480)
    
        # Calculating the Frame Per Second Captured
        current_time = time.time()
        fps = 1 / (current_time - previous_time)
        previous_time = current_time
    
        # Printing the FPS Information on image
        cv2.putText(img, str(f"FPS: {round(fps, 2)}"), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 102), 3)
    
        # Displaying the output
        cv2.imshow("VisionFi", img)
        return previous_time
    
    
    def fingers_len():
        previous_time = 0
        fingers_count = []
    
        # Check for valid inputs
        valid = model.valid_input(for_hands=[1], clm_no=[0], ilm_no=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
    
        while True:
            # Getting img and coordinates
            img, df = model.hand_detection(cap, valid)
    
            # Calculating numbers of finger
            if not df.empty:
                k = "Hand1"
                cv2.rectangle(img, (200, 135), (400, 345), (255, 0, 0), 2)
                if (200 < df[k][0][1] < 400) and (135 < df[k][0][2] < 345):
                    fingers_detected = [df[k][2][1] < df[k][1][1], df[k][4][2] < df[k][3][2], df[k][6][2] < df[k][5][2],
                                        df[k][8][2] < df[k][7][2], df[k][10][2] < df[k][9][2]]
    
                    # Counting the length of fingers_detected
                    fingers_count = [i for i in fingers_detected if str(i) == "True"]
    
            # Displaying the output
            previous_time = cv_show(img, previous_time)
            cv2.waitKey(1)
            if len(fingers_count) > 0:
                # Creating inputs for hand detection for each case
                if len(fingers_count) == 1:
                    valid = model.valid_input(for_hands=[0, 1], clm_no=[4, 8], ilm_no=[4, 8], llm_no=[4, 8])
                elif len(fingers_count) == 2:
                    valid = model.valid_input(for_hands=[0, 1], clm_no=[8, 12], ilm_no=[8, 12], llm_no=[8, 12])
                elif len(fingers_count) == 3:
                    pass
                elif len(fingers_count) == 4:
                    pass
                elif len(fingers_count) == 5:
                    pass
    
                # Loop END
                break
    
        return len(fingers_count), valid
    
    
    def vision_fi_cases():
        # Case No:
        case_no, valid = fingers_len()
    
        previous_time = 0
        hold_time = 0.2
    
        # Start time
        start_time = time.time()
    
        # Start Capturing the image from the source
        while True:
            img, df = model.hand_detection(cap, valid)
            if not df.empty:
                for index in df.columns:
                    # Case:
                    if case_no == 1:
                        img = Volume.case_vol(df, index, img)
                        hold_time = 8
                    elif case_no == 2:
                        img = Drag_Drop.drag(df, index, img)
                        hold_time = 8
                    elif case_no == 3:
                        print(f"No of Fingers: {case_no}")
                    elif case_no == 4:
                        print(f"No of Fingers: {case_no}")
                    elif case_no == 5:
                        print(f"No of Fingers: {case_no}")
                    else:
                        print(f"No of Fingers: {case_no}")
    
            # Displaying the output
            previous_time = cv_show(img, previous_time)
    
            # Waiting till 5 sec only, default destroy windows
            current_time = time.time()
            elapsed_time = current_time - start_time
    
            # Press "q" to close the window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
            elif elapsed_time > hold_time:
                print("Finished iterating in: " + str(int(elapsed_time)) + " seconds")
                break
    
    
    # Start
    while True:
        vision_fi_cases()
