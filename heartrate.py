import cv2
import os
from scipy.signal import butter, filtfilt
import heartpy as hp
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import shutil
import json

def signaltonoise(a, axis=0, ddof=0): 
    a = np.asanyarray(a) 
    m = a.mean(axis) 
    sd = a.std(axis = axis, ddof = ddof) 
    return m/sd

# Function to extract frames from the video and find the sampling rate
def extract_frames_and_sampling_rate(video_filename, output_directory):
   
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory)

    os.makedirs(output_directory)

    # Open the video file
    cap = cv2.VideoCapture(video_filename)

    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) 
    fps = cap.get(cv2.CAP_PROP_FPS) 
  
#    calculate duration of the video 
 
    dur = round(frames / fps)
    # Initialize frame count
    frame_count = 0

    # Read until video is completed
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            break

        # Save the frame
        frame_filename = os.path.join(output_directory, f'frame_{frame_count}.jpg')
        cv2.imwrite(frame_filename, frame)

        # Increment frame count
        frame_count += 1

    # Release the video capture object
    cap.release()

    return dur



def get_image(image_path):
    '''
    Return a numpy array of red image values so that we can access values[x][y]
    '''
    image = Image.open(image_path)
    width, height = image.size
    red, green, blue = image.split()
    red_values = list(red.getdata())
    return np.array(red_values).reshape((width, height))

def get_mean_intensity(image_path):
    '''
    Return mean intensity of an image values
    '''
    image = get_image(image_path)
    return np.mean(image)

def plot(x,title,xaxis,yaxis,filename):
    '''
    Plot the signal
    TODO: Vertical flip and plot a normal PPG signal instead of an inverted one
    '''
    fig = plt.figure(figsize=(13, 6))
    ax = plt.axes()
    ax.plot(list(range(len(x))), x)

    plt.title(title)
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)  # Save the figure before showing it
    plt.show()


def get_signal_from():
    '''
    Return PPG signal as a sequence of mean intensities from the sequence of
    images that were captured by a device (NoIR camera or iphone camera)
    '''
 
    dir = 'frames/'
    length = len(os.listdir(dir))
    x = []
    for j in range(length):
        image_path = dir+'frame_'+str(j)+'.jpg'
        print('reading image: ' + image_path)
        x.append(get_mean_intensity(image_path))
    return x


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def getHR(filename):

    output_directory = 'frames/'
    dur = extract_frames_and_sampling_rate(filename, output_directory)

    x = get_signal_from()
# Define the cutoff frequencies and order of the filter
    lowcut = 0.5  # Lower cutoff frequency in Hz
    highcut = 10.0  # Upper cutoff frequency in Hz
    order = 4  # Filter order

    plot(x,'PPG signal','Time', 'Amplitude','Unfiltered.jpg')

    # plt.figure(figsize=(12, 4))
    # plt.plot(x, label='PPG Signal')
    # plt.title('PPG Signal')
    # plt.xlabel('Sample')
    # plt.ylabel('Amplitude')
    # plt.legend()
    # plt.grid(True)
    # plt.show()
    # plt.savefig("ppg.jpg")
# Apply the bandpass filter to the PPG signal
    filtered_ppg_signal = butter_bandpass_filter(x, lowcut, highcut, len(x)/dur, order)

    plot(filtered_ppg_signal,'PPG signal','Time', 'Amplitude','filtered.jpg')

# Process the filtered PPG signal with HeartPy
   
    wd_filtered, m_filtered = hp.process(filtered_ppg_signal, sample_rate=len(x)/dur)

# Plot the filtered PPG signal
    # plt.figure(figsize=(12, 4))
    # plt.plot(filtered_ppg_signal, label='Filtered PPG Signal')
    # plt.title('Filtered PPG Signal')
    # plt.xlabel('Sample')
    # plt.ylabel('Amplitude')
    # plt.legend()
    # plt.grid(True)
    # plt.show()
    # plt.savefig("Filtered_PPG.jpg")

# Plot HeartPy's processing results on the filtered signal
    plot_obj = hp.plotter(wd_filtered, m_filtered,show=False)
    plot_obj.savefig('HR_.jpg')
 


    # for measure in m_filtered.keys():
    #     print('%s: %f' %(measure, m_filtered[measure]))

    snr = signaltonoise(filtered_ppg_signal)
    print(f"bpm : {m_filtered['bpm']} snr : {snr}")

    return m_filtered['bpm'],snr

if __name__ == "__main__":
    # Have an end point here
    data = { }
    print(getHR("test/kanchana_maam_incorrect_position.mp4"))
    # files = os.listdir('test')
    # print(files)
    # for file in files:
    #     data[file] = { }
    #     data[file]['hr'], data[file]['snr'] = getHR('test/'+file)
    #     print(data)

    # with open('heartrate_test.json', 'w') as json_file:
    #     json.dump(data, json_file)

    # print("JSON data saved locally.")









    