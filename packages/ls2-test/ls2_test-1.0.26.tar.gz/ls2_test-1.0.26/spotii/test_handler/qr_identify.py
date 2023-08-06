import cv2

def qrIdentify(image):
    try:
        decoder = cv2.QRCodeDetector()
        value, points, _ = decoder.detectAndDecode(image)
        print('qrIdentify, value:',value)
        if points.any() == None:
            print('qr')
    except Exception as e:
        print(e)
        return None

    if value !='':
        return value
    return None
