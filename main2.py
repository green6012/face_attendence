from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import tkinter
import cv2
import PIL.Image, PIL.ImageTk
from PIL import Image
from threading import Thread
# import face_recognition
import os
import sqlite3
import numpy as np
from datetime import datetime

window = Tk()
window.title("Tkinter OpenCv")
window.geometry("2560x1600")
faceDetect=cv2.CascadeClassifier('haarcascade_frontalface_default.xml');
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer1 = cv2.face.LBPHFaceRecognizer_create()
recognizer1.read('recognizer/trainner.yml')
#set text style
fontface = cv2.FONT_HERSHEY_SIMPLEX
fontscale = 1
fontcolor = (0,255,0)
fontcolor1 = (0,0,255)

# Update video for app
video = cv2.VideoCapture(0)
canvas_w = video.get(cv2.CAP_PROP_FRAME_WIDTH)
canvas_h = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

canvas = Canvas(window, width = canvas_w, height = canvas_h)
canvas.place(x=0,y=0)

photo = None
tt = 0;
num = 0

def update_frame():
    global canvas, photo, tt, num
    ret, frame = video.read()
    frame = cv2.flip(frame, 1)
    # frame = cv2.resize(frame, dsize=None, fx=0.5, fy=0.5)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, 1.3, 5);
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    if (tt == 1):
        msv = entryMSV.get()
        for (x, y, w, h) in faces:
            cv2.imwrite("dataSet/User." + msv + '.' + str(num) + ".jpg", gray[y:y + h, x:x + w])
            num += 1
            if(num == 50):
                tt = 0;
                lblKetQua.configure(text = "Đã chụp xong")
                clearTable(tbDSSV)
                showSinhVien()
    if (tt == 2):
        thread = Thread(target=train())
        thread.start()
    if (tt == 3):
        for (x, y, w, h) in faces:
            msv, dist = recognizer1.predict(gray[y:y + h, x:x + w])
            if (dist<=62):
                conn = sqlite3.connect('btl.db')
                c = conn.cursor()
                c.execute("SELECT * FROM sinhvien WHERE msv = '" + str(msv) + "'")
                rows = c.fetchall()
                conn.commit()
                conn.close()
                if(rows != None):
                    for row in rows:
                        cv2.putText(frame, "Name: " + str(row[1]) + "MSV: " + str(row[0]), (x, y + h + 30), fontface,
                                    fontscale, fontcolor, 2)
                        if(row[3] == 0):
                            now = datetime.now()
                            current_time = now.strftime("%H:%M %d/%m/%Y")
                            conn = sqlite3.connect('btl.db')
                            c = conn.cursor()
                            c.execute("UPDATE sinhvien SET diemdanh = 1, time = '" + str(current_time) + "' WHERE msv = " + str(row[0]))
                            conn.commit()
                            conn.close()
                            lblDiemDanh.configure(text = "Đã điểm danh: " + str(row[1]))
                            clearTable(tbDD)
                            showSVDiemDanh()

            else:
                cv2.putText(frame, "Name: Unknown", (x, y + h + 30), fontface, fontscale, fontcolor1, 2)

    photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
    canvas.create_image(0,0, image = photo, anchor=tkinter.NW)

    window.after(15, update_frame)

# Function
# Hàm cập nhật tên và ID vào CSDL
def insertOrUpdate(msv, ten, lop):
    conn=sqlite3.connect("btl.db")
    cursor=conn.execute('SELECT * FROM sinhvien WHERE msv='+str(msv))
    isRecordExist=0
    for row in cursor:
        isRecordExist = 1
        break

    if isRecordExist==1:
        cmd="UPDATE sinhvien SET ten=' "+str(ten)+" ', lop=' "+str(lop)+" ' WHERE msv="+str(msv)
    else:
        cmd="INSERT INTO sinhvien Values("+str(msv)+",' "+str(ten)+" ', ' "+str(lop)+" ','0','None')"

    conn.execute(cmd)
    conn.commit()
    conn.close()

def themSinhVien():
    global tt,num
    msv = entryMSV.get()
    ten = entryName.get()
    lop = entryLop.get()
    if (msv == "" or ten == "" or lop == ""):
        tkinter.messagebox.showerror(title="Error", message="Bạn chưa nhập đủ dữ liệu!")
    else:
        insertOrUpdate(msv, ten, lop)
        tt = 1
        lblKetQua.configure(text="Đang chụp ảnh sinh viên")
        num = 0
def resetDiemDanh():
    conn = sqlite3.connect('btl.db')
    c = conn.cursor()
    c.execute("UPDATE sinhvien SET diemdanh = 0")
    conn.commit()
    conn.close()
def diemDanh():
    global tt
    tt = 2
    lblKetQua.configure(text="Đang train dữ liệu, Vui lòng chờ!")
def endDiemDanh():
    global tt
    tt = 0
    lblKetQua.configure(text="Kết thúc điểm danh")
    clearTable(tbDD)
    showSVDiemDanh()

def showSinhVien():
    conn = sqlite3.connect('btl.db')
    c = conn.cursor()
    c.execute("SELECT * FROM sinhvien")
    rows = c.fetchall()
    sinhvien = []
    dem = 1
    for row in rows:
        sinhvien.append((f'{dem}',f'{row[0]}',f'{row[1]}',f'{row[2]}'))
        dem += 1
    conn.commit()
    conn.close()
    for i in sinhvien:
        tbDSSV.insert('', 'end', values = i)

def showSVDiemDanh():
    conn = sqlite3.connect('btl.db')
    c = conn.cursor()
    c.execute("SELECT * FROM sinhvien WHERE diemdanh = 1")
    rows = c.fetchall()
    sinhvien = []
    dem = 1
    for row in rows:
        sinhvien.append((f'{dem}',f'{row[0]}',f'{row[1]}',f'{row[2]}',f'{row[4]}'))
        dem += 1
    conn.commit()
    conn.close()
    for i in sinhvien:
        tbDD.insert('', 'end', values = i)
def clearTable(tree):
    for item in tree.get_children():
        tree.delete(item)
# Train
def getImagesAndLabels(path):
    # Lấy tất cả các file trong thư mục
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)]
    faceSamples=[]
    Ids=[]
    for imagePath in imagePaths:
        if (imagePath[-3:]=="jpg"):
            print(imagePath[-3:])
            pilImage=Image.open(imagePath).convert('L')
            #converting the PIL image into numpy array
            imageNp=np.array(pilImage,'uint8')
            #getting the Id
            Id=int(os.path.split(imagePath)[-1].split(".")[1])
            faces=faceDetect.detectMultiScale(imageNp)
            for (x,y,w,h) in faces:
                faceSamples.append(imageNp[y:y+h,x:x+w])
                Ids.append(Id)
    return faceSamples,Ids

def train():
    global tt
    faceSamples, Ids = getImagesAndLabels('dataSet')
    recognizer.train(faceSamples, np.array(Ids))
    recognizer.save('recognizer/trainner.yml')
    lblKetQua.configure(text="Đã train xong! Bắt đầu điểm danh")
    tt = 3
    resetDiemDanh()
    clearTable(tbDD)
    showSVDiemDanh()

# Tkinter
# Thêm sinh viên
lblName = Label(window, text = "Họ và Tên: ")
lblName.place(x=10,y=500)
entryName = Entry(window, width = 30)
entryName.place(x=100,y=500)
lblMSV = Label(window, text = "Mã sinh viên: ")
lblMSV.place(x=10,y=530)
entryMSV = Entry(window, width = 30)
entryMSV.place(x=100,y=530)
lblLop = Label(window, text = "Lớp: ")
lblLop.place(x=10,y=560)
entryLop = Entry(window, width = 30)
entryLop.place(x=100,y=560)
btnThem = Button(window, text = "Thêm sinh viên",command = themSinhVien)
btnThem.place(x=70,y=590)
lblKetQua = Label(window, text = "", font = "Helvetica 20 bold");
lblKetQua.place(x=70, y=730)

# Bảng danh sách sinh viên
tbDSSV = Treeview(window, columns=(1,2,3,4), show="headings", height="10")
tbDSSV.place(x=800, y=70)
tbDSSV.heading(1, text="STT")
tbDSSV.column(1, width = 50)
tbDSSV.heading(2, text="Mã sinh viên")
tbDSSV.column(2, width = 150)
tbDSSV.heading(3, text="Họ và Tên")
tbDSSV.column(3, width = 350)
tbDSSV.heading(4, text="Lớp")
tbDSSV.column(4, width = 150)
lblDSSV = Label(window, text = "Danh sách sinh viên", font = "Helvetica 16 bold");
lblDSSV.place(x=1060, y=20)
showSinhVien()

# Bảng danh sách sinh viên điểm danh
tbDD = Treeview(window, columns=(1,2,3,4,5), show="headings", height="10")
tbDD.place(x=700, y=570)
tbDD.heading(1, text="STT")
tbDD.column(1, width = 50)
tbDD.heading(2, text="Mã sinh viên")
tbDD.column(2, width = 150)
tbDD.heading(3, text="Họ và Tên")
tbDD.column(3, width = 350)
tbDD.heading(4, text="Lớp")
tbDD.column(4, width = 150)
tbDD.heading(5, text="Thời gian điểm danh")
tbDD.column(5, width = 220)
lblDD = Label(window, text = "Danh sách sinh viên đã điểm danh", font = "Helvetica 16 bold");
lblDD.place(x=1000, y=520)
showSVDiemDanh()

#btn Điểm danh
btnDiemDanh = Button(window, text = "Điểm danh",command = diemDanh)
btnDiemDanh.place(x=120,y=890)
btnEndDiemDanh = Button(window, text = "Kết thúc điểm danh",command = endDiemDanh)
btnEndDiemDanh.place(x=210,y=890)
lblDiemDanh = Label(window, text = "", font = "Helvetica 20 bold");
lblDiemDanh.place(x=1000, y=900)

update_frame()
window.mainloop()