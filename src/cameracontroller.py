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
    '''
    カメラ制御クラス
    PiCameraインスタンスとDetectionControllerインスタンスを持ち、
    動体の検出に応じて録画を開始/停止する
    '''
    
    def __init__( self ):
        self.camera            = picamera.PiCamera( resolution=RESOLUTION, framerate=FRAMERATE )
        self.detection_ctrlr   = DetectionController( self.camera )
    
    
    def control_recording( self ):
        '''
        動体の検出に応じて録画の開始/停止を制御する
        '''
        try:
            self.detection_ctrlr.set_detection( 'frame subtraction' )
            
            while True:
                if self.detection_ctrlr.detection_is_enabled == True:
                    is_detected = self.detection_ctrlr.detect()
                    
                    if is_detected == True:
                        if self.camera.recording == False:
                            self.camera.start_recording( 'video'+datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')+'.h264')
                            print( 'Start recording' )
                    else:
                        if self.camera.recording == True:
                            self.camera.stop_recording()
                            print( 'Stop recording' )
        
        finally:
            if self.camera.recording == True:
                self.camera.stop_recording()
            
            self.detection_ctrlr.fin_detection()
            self.camera.close()
            print( 'Done closing' )
            

class DetectionController():
    ''' Detection Controllerクラス（Proxyパターン）'''
    
    def __init__( self, camera ):
        self.camera               = camera
        self.detection_is_enabled = True
    
    
    def set_detection( self, algorithm=None ):
        ''' 動体検出アルゴリズムを設定する '''
        
        if algorithm == None:
            print( 'Please select detection algorithm' )
            return
        
        # フレーム差分法
        if algorithm == 'frame subtraction':
            self.algorithm = FrameSubtraction( self.camera )
            print( 'Initialized detection' )
        
        print( 'Done setting up detection' )
    
    
    def fin_detection( self ):
        ''' Finalize detection '''
        
        self.algorithm.fin()
        print( 'Finalized detection' )
    
    
    def detect( self ):
        ''' Detect '''
        # return True/False
        
        return self.algorithm.func()
    

class FrameSubtraction():
    ''' Frame Subtraction algorithm '''

    def __init__( self, camera ):
        self.camera = camera
        self.frame1 = picamera.array.PiRGBArray( self.camera )
        self.frame2 = picamera.array.PiRGBArray( self.camera )
        self.frame3 = picamera.array.PiRGBArray( self.camera )
    
    
    def fin( self ):
        ''' Finalizer of frame subtraction '''
        
        self.frame1.close()
        self.frame2.close()
        self.frame3.close()
    
    
    def func( self ):
        ''' フレーム差分法による動体検出アルゴリズム '''
        # return True/False

        # フレームを３枚キャプチャ
        self.camera.capture( self.frame1, 'bgr', use_video_port=True )
        self.camera.capture( self.frame2, 'bgr', use_video_port=True )
        self.camera.capture( self.frame3, 'bgr', use_video_port=True )
        
        # RGBからGrayへ変換
        frame1_gray = cv2.cvtColor( self.frame1.array, cv2.COLOR_BGR2GRAY )
        frame2_gray = cv2.cvtColor( self.frame2.array, cv2.COLOR_BGR2GRAY )
        frame3_gray = cv2.cvtColor( self.frame3.array, cv2.COLOR_BGR2GRAY )
        
        # フレーム差分の計算
        dif_img1 = cv2.absdiff( frame1_gray, frame2_gray )
        dif_img2 = cv2.absdiff( frame2_gray, frame3_gray )
        
        dif_imga = cv2.bitwise_and( dif_img1, dif_img2 )
        
        # 2値化
        ret, bin_img = cv2.threshold( dif_imga, BINARIZE_TH, PIXEL_VAL_MAX, cv2.THRESH_BINARY)
        bin_img = cv2.medianBlur( bin_img, 7 )
        
        if np.sum(bin_img) > MOTION_DETECTION_TH:
            is_detected = True
            print( 'Detected' )
        else:
            is_detected = False
            print( 'Not Detected' )
        
        # PiCameraモジュールの決まりで、frame1, frame2, frame3を再利用する前に truncate(0)する必要があるらしい
        self.frame1.truncate( 0 )
        self.frame2.truncate( 0 )
        self.frame3.truncate( 0 )
        
        return is_detected
    
