import cv2
import numpy as np
from datetime import datetime
from pynput.mouse import Button, Controller
import wx
mouse=Controller()

#app=wx.App(False)
#(sx,sy)=wx.GetDisplaySize()
sx,sy=1366,768
#(camx,camy)=(320,240)
(camx,camy)=(480, 640)

lowerBound=np.array([33,80,40])
upperBound=np.array([102,255,255])


lowblue=np.array([110,130,50],dtype=np.uint8)
highblue=np.array([130,255,255],dtype=np.uint8)


font=cv2.FONT_HERSHEY_SIMPLEX
cam= cv2.VideoCapture(0)

kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))
mLocOld=np.array([0,0])
mouseLoc=np.array([0,0])
d=5
#mouseLoc=mLocOld+(targetLoc-mLocOld)/d
pinchFlag=0
cpm=0
eg=[]

def trans(img,maskFinal,cptotal):
    
    hull = cv2.convexHull(np.array(cptotal),returnPoints = True)    
    mask=np.zeros(img.shape,dtype=np.uint8)
    mask1=np.zeros(img.shape,dtype=np.uint8)
    mask1[:,:,:]=255

    cv2.fillPoly(mask1,[hull],0)
    m2=cv2.add(mask1,img)

    eg2=[j for i in hull for j in i]
    xco=[i for i,j in eg2]
    yco=[j for i,j in eg2]

    xlow,xhigh,ylow,yhigh=xco[0],xco[0],yco[0],yco[0]
    for i in xco[1:]:
        if xlow>i:
            xlow=i
        
    for i in xco[1:]:
        if xhigh<i:
            xhigh=i

    for i in yco[1:]:
        if ylow>i:
            ylow=i
        
    for i in yco[1:]:
        if yhigh<i:
            yhigh=i

    
    m2=m2[ylow:yhigh,xlow:xhigh,:]
    cv2.imshow("Image",m2)
    cv2.waitKey(0)

    
while True:
    ret, img=cam.read()
    #img=cv2.resize(img,(340,220))

    #convert BGR to HSV
    imgHSV= cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    # create the Mask
    mask=cv2.inRange(imgHSV,lowerBound,upperBound)
    cg=cv2.countNonZero(mask)
    maskb = cv2.inRange(imgHSV, lowblue,highblue)
    cb=cv2.countNonZero(maskb)
    print 'cb',cb

    if cb>500:
        from datetime import datetime
        a=datetime.time(datetime.now())
        a=str(a)
        t=a.split(':')
        t=t[:2]
        t[0]=str(int(t[0])-12)
    
        
        maskOpen1=cv2.morphologyEx(maskb,cv2.MORPH_OPEN,kernelOpen)
        maskClose1=cv2.morphologyEx(maskOpen1,cv2.MORPH_CLOSE,kernelClose)
        
        maskFinal1=maskClose1
        conts1,h=cv2.findContours(maskFinal1.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        cptotal1=[]
    
        for c in conts1:
            M = cv2.moments(c)
            if M["m00"]!=0:
                cX1 = int(M["m10"] / M["m00"])
                cY1 = int(M["m01"] / M["m00"])
                cptotal1.append([cX1,cY1])
            else:
                cX1,cY1=0,0
            
        cv2.putText(img,'{0}:{1}'.format(str(t[0]),str(t[1])),(cX1,cY1),font,0.8,(0,0,255),2,255)                        
    
    #morphology
    maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
    maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)
    
    maskFinal=maskClose
    conts,h=cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    cptotal=[]
    
    for c in conts:
        M = cv2.moments(c)
        if M["m00"]!=0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            try:
                cptotal.append([cX,cY])
            except:
                
                pass
        else:
            cX,cY=0,0
    
            
   
    if(len(conts)==2):
        cpm=0
        if(pinchFlag==1):
            pinchFlag=0
            mouse.release(Button.left)
        #hull = cv2.convexHull(np.array(cptotal),returnPoints = True)
        try:
            cx1,cy1=cptotal[0]
        except:
            pass
        if len(cptotal)>1:
            cx2,cy2=cptotal[1]
        else:
            cx2,cy2=0,0
        cx=(cx1+cx2)/2
        cy=(cy1+cy2)/2
        cv2.circle(img, (cx,cy),2,(0,0,255),2)
        mouseLoc=mLocOld+((cx,cy)-mLocOld)/d
        mouse.position=(sx-(mouseLoc[0]*sx/camx),mouseLoc[1]*sy/camy)
        while mouse.position!=(sx-(mouseLoc[0]*sx/camx),mouseLoc[1]*sy/camy):
            pass
        mLocOld=mouseLoc
    elif(len(conts)==1):
        x,y,w,h=cv2.boundingRect(conts[0])
        if(pinchFlag==0):
            pinchFlag=1
            mouse.press(Button.left)
        else:
            try:
                cx,cy=cptotal[0]
            except:
                pass
            cv2.circle(img,(cx,cy),(w+h)/4,(0,0,255),2)
            mouseLoc=mLocOld+((cx,cy)-mLocOld)/d
            mouse.position=(sx-(mouseLoc[0]*sx/camx),mouseLoc[1]*sy/camy)
            while mouse.position!=(sx-(mouseLoc[0]*sx/camx),mouseLoc[1]*sy/camy):
                pass
        mLocOld=mouseLoc
    elif(len(conts)==4):
        print cg
        if cpm==0 and cg>5000:
            trans(img,maskFinal,cptotal)
            cpm=1
       
        
    
    cv2.imshow("cam",img)
    cv2.waitKey(1)
    if cv2.waitKey(1) & 0xff==ord('q'):
        
        break




    
cam.release()
cv2.destroyAllWindows()
