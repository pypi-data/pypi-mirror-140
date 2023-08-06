import math
import cv2
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))


def case_vol(df, index, img):
    fin08_length = math.hypot(df[index][1][1] - df[index][0][1], df[index][1][2] - df[index][0][2])
    vol = np.interp(fin08_length, [10, 110], [-65.25, 0])
    volume.SetMasterVolumeLevel(vol, None)
    current_vol = round(volume.GetMasterVolumeLevelScalar(), 2) * 100
    cv2.putText(img, str(f"Volume: {current_vol}"), (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 102), 3)
    return img
