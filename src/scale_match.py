import cv2,imutils
import numpy as np

# 模板放缩范围
min_scale, max_scale = (0.8, 3)

def show_image(img, title="image", close = True):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    if close:
        cv2.destroyWindow(title)

def scale_match(image, template, num_step = 20, show = True):
    """带比例的模板匹配

    Args:
        image (numpy.ndarray): 目标图片
        template (numpy.ndarray): 模板图片
        show (bool, optional): 是否显示图片和匹配过程. Defaults to True.

    Returns:
        tuple: 最佳匹配值，最佳匹配位置，放缩比例
    """
    def _show_rectangle(maxLoc, r):
        clone = image.copy()
        startX, startY = int(maxLoc[0] * r), int(maxLoc[1] * r)
        endX, endY = int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r)
        cv2.rectangle(clone, (startX, startY), (endX, endY), (0, 0, 255), 2)
        show_image(clone, close=False)
    
    # 模板尺寸
    (tH, tW) = template.shape[:2]
    
    # 模板图边缘检测
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    template = cv2.Canny(template, 50, 200)
    # 显示图片
    if show:show_image(template, "Template")
    
    # 目标图的边缘检测
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edged = cv2.Canny(gray, 50, 200)
    # 显示图片
    if show:show_image(image)
    
    # 搜索最佳匹配
    best_match = None
    for scale in np.linspace(1/max_scale, 1/min_scale, num_step)[::-1]:
        # 放缩目标图
        resized = imutils.resize(edged, width = int(edged.shape[1] * scale))
        # 目标图小于模板图，跳出
        if resized.shape[0] < tH or resized.shape[1] < tW:
            break
        # 当前最佳匹配
        result = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
        #  print("比例 %.3f\t最佳匹配值%.3f" % (scale, maxVal/ 10**7))
        if show:
            _show_rectangle(maxLoc, 1/scale)
            
        # 更新最优位置
        if best_match is None or maxVal > best_match[0]:
            best_match = (maxVal, maxLoc, 1/scale)
    if show:
        _show_rectangle(best_match[1], 1/best_match[2])
        cv2.destroyAllWindows()
    return best_match
