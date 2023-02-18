import cv2, imutils
import numpy as np

# 模板放缩范围
min_scale, max_scale, num_step = (0.5, 3, 150)

def show_image(img, title="image", close = True):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    if close:
        cv2.destroyWindow(title)

def draw_rectangle(img, shape:tuple, Loc:tuple, ratio:float):
    """图上绘制识别的红框

    Args:
        img (numpy.ndarray): 目标图
        shape (tuple): 模板尺寸
        Loc (tuple): 矩形左上位置
        ratio (float): 放缩比例

    Returns:
        numpy.ndarray: 绘制了红框的图片（新建图片）
    """
    startX, startY = int(Loc[0] * ratio), int(Loc[1] * ratio)
    endX, endY = int((Loc[0] + shape[1]) * ratio), int((Loc[1] + shape[0]) * ratio)
    return cv2.rectangle(img.copy(), (startX, startY), (endX, endY), (0, 0, 255), 2)

def detect_image(image, template, num_step = num_step, frames = False):
    """带比例的模板匹配

    Args:
        image (numpy.ndarray): 目标图片
        template (numpy.ndarray): 模板图片
        show (bool, optional): 是否显示图片和匹配过程. Defaults to True.
        frames (bool, optional): 是否返回匹配过程的图片. Defaults to False.

    Returns:
        tuple: 最佳匹配值，最佳匹配位置，放缩比例
    """
    # 收集匹配过程的图片
    images = [(0., image)]

    # 模板尺寸
    (tH, tW) = template.shape[:2]
    
    # 模板图边缘检测
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    template = cv2.Canny(template, 50, 200)

    # 目标图的边缘检测
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edged = cv2.Canny(gray, 50, 200)
    
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
        img = draw_rectangle(image, (tH, tW), maxLoc, 1/scale)
        images.append((maxVal, img))
            
        # 更新最优位置
        if best_match is None or maxVal > best_match[0]:
            best_match = (maxVal, maxLoc, 1/scale)
    img = draw_rectangle(image, (tH, tW), best_match[1], best_match[2])
    images.append((best_match[0], img))
    return best_match if not frames else images