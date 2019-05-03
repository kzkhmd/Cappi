import cameracontroller

class AppRunner():
    
    def run( self ):
        ''' Run application '''
        
        controller = cameracontroller.CameraController()
        controller.control_recording()