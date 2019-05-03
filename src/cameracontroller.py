import datetime
import multiprocessing
import picamera
import picamera.array
import cv2
import numpy as np

# Define
MOTION_DETECTION_TH = 0
BINARIZE_TH         = 30
PIXEL_VAL_MAX       = 255

RESOLUTION          = ( 1920, 1080 )
FRAMERATE           = 30


class CameraController():
    ''' Camera Controller Class '''
    
    def __init__( self ):
        self.camera            = picamera.PiCamera( resolution=RESOLUTION, framerate=FRAMERATE )
        self.detection_ctrlr   = DetectionController( self.camera )
    
    
    def control_recording( self ):
        try:
            self.detection_ctrlr.set_detection( 'frame subtraction' )
            self.detection_ctrlr.init_detection()
            
            while True:
                if self.detection_ctrlr.detection_is_enabled == True:
                    is_detected = self.detection_ctrlr.detect()
                    
                    if is_detected == True:
                        if self.camera.recording == False:
                            self.camera.start_recording( 'video'+datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')+'.h264')
                            print( 'Start recording' )
                        else:
                            pass
                    else:
                        if self.camera.recording == True:
                            self.camera.stop_recording()
                            print( 'Stop recording' )
                        else:
                            pass
        
        finally:
            if self.camera.recording == True:
                self.camera.stop_recording()
            
            self.detection_ctrlr.fin_detection()
            self.camera.close()
            print( 'Done closing' )
            


class DetectionController():
    ''' Detection Controller Class '''
    
    def __init__( self, camera ):
        self.camera               = camera
        self.detection_is_enabled = True
    
    
    def set_detection( self, detection_algorithm ):
        ''' Set up detection '''
        
        if detection_algorithm == None:
            print( 'Please select detection algorithm' )
            return
        
        if detection_algorithm == 'frame subtraction':
            self.detection_algorithm = detection_algorithm
            self.detection_init      = self._init_frame_subtraction
            self.detection_fin       = self._fin_frame_subtraction
            self.detection_func      = self._func_frame_subtraction
        
        print( 'Done setting up detection' )
    
    
    def init_detection( self ):
        ''' Initialize detection '''
        
        self.detection_init()
        print( 'Initialized detection' )
    
    
    def fin_detection( self ):
        ''' Finalize detection '''
        
        self.detection_fin()
        print( 'Finalized detection' )
    
    
    def detect( self ):
        ''' Detect '''
        # return True/False
        
        return self.detection_func()
    
    
    def _init_frame_subtraction( self ):
        ''' Initializer of frame subtraction '''
        
        self.frame1 = picamera.array.PiRGBArray( self.camera )
        self.frame2 = picamera.array.PiRGBArray( self.camera )
        self.frame3 = picamera.array.PiRGBArray( self.camera )
    
    
    def _fin_frame_subtraction( self ):
        ''' Finalizer of frame subtraction '''
        
        self.frame1.close()
        self.frame2.close()
        self.frame3.close()
    
    
    def _func_frame_subtraction( self ):
        ''' Frame subtraction algorithm for motion detection '''
        
        # Capture frame
        self.camera.capture( self.frame1, 'bgr', use_video_port=True )
        self.camera.capture( self.frame2, 'bgr', use_video_port=True )
        self.camera.capture( self.frame3, 'bgr', use_video_port=True )
        
        # Convert RGB to Gray
        frame1_gray = cv2.cvtColor( self.frame1.array, cv2.COLOR_BGR2GRAY )
        frame2_gray = cv2.cvtColor( self.frame2.array, cv2.COLOR_BGR2GRAY )
        frame3_gray = cv2.cvtColor( self.frame3.array, cv2.COLOR_BGR2GRAY )
        
        # Frame subtraction
        dif_img1 = cv2.absdiff( frame1_gray, frame2_gray )
        dif_img2 = cv2.absdiff( frame2_gray, frame3_gray )
        
        dif_imga = cv2.bitwise_and( dif_img1, dif_img2 )
        
        # Binarize
        ret, bin_img = cv2.threshold( dif_imga, BINARIZE_TH, PIXEL_VAL_MAX, cv2.THRESH_BINARY)
        bin_img = cv2.medianBlur( bin_img, 7 )
        
        if np.sum(bin_img) > MOTION_DETECTION_TH:
            is_detected = True
            print( 'Detected' )
        else:
            is_detected = False
            print( 'Not Detected' )
        
        # It is necessary to use 'truncate(0)' before reuse frame1, frame2, frame3
        self.frame1.truncate( 0 )
        self.frame2.truncate( 0 )
        self.frame3.truncate( 0 )
        
        return is_detected
    
