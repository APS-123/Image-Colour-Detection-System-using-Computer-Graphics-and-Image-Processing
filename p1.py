import cv2

img = cv2.imread(r"C:\Users\HP\Desktop\s5\CGIP\image.jpg")
cv2.imshow("Test", img)
cv2.waitKey(0)
cv2.destroyAllWindows()