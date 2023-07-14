# import cv2
# import matplotlib.pyplot as plt
# import numpy as np
# from IPython import embed
#
# # 读取图像
# img = cv2.imread("../images/add.png")
#
# # 转换为灰度图
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
# # Canny边缘检测
# edges = cv2.Canny(gray, 100, 200)
#
# # 获取图像轮廓
# contours, hierarchy = cv2.findContours(
#     edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
#
# embed()
# # 获取最大的轮廓
# cnt = max(contours, key=cv2.contourArea)
#
# embed()
# # 拟合轮廓曲线
# x, y = cnt[:, 0, 0], cnt[:, 0, 1]
# coeffs = np.polyfit(x, y, 5)
# poly = np.poly1d(coeffs)
# xp = np.linspace(0, x.max(), 100)
# yp = poly(xp)
#
# # 绘制结果
# plt.imshow(img)
# plt.plot(xp, yp, "-", color="r")
# plt.show()

##################################

import cv2
import numpy as np

img = cv2.imread("../images/game-controller.png")
# rgb->gray
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 50, 150)
contours, hierarchy = cv2.findContours(
    edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS
)

cv2.drawContours(img, contours, -1, (0, 255, 255), 2)

for contour in contours:
    epsilon = 0.0001 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    cv2.drawContours(img, [approx], 0, (0, 0, 255), 1)

cv2.imshow("image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()


###################################################


####################################################

# import cv2
# import numpy as np
#
# # 读取图像,检测边缘,提取轮廓
# img = cv2.imread("../images/start.png")
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# edges = cv2.Canny(gray, 50, 200)
# contours, hierarchy = cv2.findContours(
#     edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# cnt = contours[0]
#
# # 轮廓折线逼近
# epsilon = 0.01 * cv2.arcLength(cnt, True)
# approx = cv2.approxPolyDP(cnt, epsilon, True)
#
# # 获取折线端点坐标
# pts = approx.reshape((-1, 2))
#
# # 分析端点,提取拐点
# dists = np.sqrt(np.sum(np.diff(pts, axis=0) ** 2, axis=1))
# angles = np.concatenate(
#     ([0], np.arctan2(np.diff(pts[:, 1]), np.diff(pts[:, 0]))))
# is_corner = (dists > 50) & (np.abs(np.diff(angles)) > np.pi / 3)
# corners = pts[is_corner]
#
# # 拟合直线和圆弧
# lines = [
#     cv2.fitLine(pts[i: i + 2], cv2.DIST_L2, 0, 0.01, 0.01)
#     for i in range(len(pts) - 1)
#     if not is_corner[i]
# ]
# arcs = [
#     cv2.fitEllipse(corners[i: i + 3])
#     for i in range(len(corners) - 2)
#     if is_corner[i + 1]
# ]
#
# # 绘制结果
# img = cv2.drawContours(img, [approx], -1, (0, 255, 0), 2)
# for l in lines:
#     p1, p2 = l[0], l[0] + l[1]
#     img = cv2.line(
#         img, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (255, 0, 0), 2
#     )
# for a in arcs:
#     img = cv2.ellipse(img, a, (0, 0, 255), 2)
#
# cv2.imshow("contour", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
