import cv2
import numpy

class CalculateDistance:
    """
    1.获取滑动的距离
    2.将验证码背景大图和需要滑动的小图进行处理，先在大图中找到类型的小土位置，在获取相对应的像素偏移量
    """
    def __init__(self,background_path,slide_path,offset_px, offset_py,diaplay):
        """
        :background_path:验证码背景大图地址
        :slide_path:需要滑块图片地址
        :offset_px:小图距离在大图上的左边边距(像素偏移量)
        :offset_py:小图距离在大图上的顶部边距(像素偏移量)
        """
        #读入图片
        self.background_img =cv2.imread(background_path)
        self.offset_px = offset_px
        self.offset_py = offset_py
        self.slide_img = cv2.imread(slide_path,cv2.IMREAD_GRAYSCALE)
        #计算X轴缩放因子，以50px为基准
        scake_x = 50 / self.slide_img.shape[1]
        #使用最近邻插值法缩放，得到缩放后50*50的图片
        self.slide_scale_img = cv2.resize(self.slide_img,(0,0),fx=scake_x,fy=scake_x)
        self.background_cut_img = None
        self.display = diaplay

    def get_distance(self):
        #将小图转换为灰色
        slide_grey_img = cv2.cvtColor(self.slide_img,cv2.COLOR_BGR2GRAY)
        #使用canny算子，提取图片边缘特征
        #特征值可以调试：100，200，细节特征比较明显，数值增大后特征较为粗略
        slide_edge_img = cv2.Canny(slide_grey_img,100,250)
        self.cv_show('canny',slide_edge_img)
        #将背景图转换为灰色
        background_grey_img = cv2.cvtColor(self.background_cut_img,cv2.COLOR_BGR2GRAY)
        #使用canny算子，提取图片边缘特征
        background_edge_img = cv2.Canny(background_grey_img,200,300)
        self.cv_show('bg_canny',background_edge_img)
        #取小图的高和宽
        h, w = slide_edge_img.shape

        #将滑块地图与背景进行模板匹配，找到缺口对应的位置
        result = cv2.matchTemplate(background_edge_img,slide_edge_img,cv2.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        #获取缺口左上角位置
        top_left = (max_loc[0],max_loc[1])
        #右下角位置
        bottom_right = (top_left[0] + w, top_left[1] + h)

        #在切割后背景图片中画出需要移动的终点位置
        #rectangle(图片源数据，左上角，右下角，颜色，画笔厚度)
        if self.display:
            print (top_left)
            print (bottom_right)
            after_img = cv2.rectangle(self.background_cut_img,top_left,bottom_right,(0,0,255),2)
            #画图
            self.cv_show('after',after_img)
        #计算移动距离
        slide_distance = top_left[0] +w +10
        return slide_distance

    def cut_background(self):
        #切割图片的上下边框
        height = self.slide_scale_img.shape[0]
        #将背景图中上下多于部分以及滑块图片部分去除，如：background_img[y1:y2,x1:]
        self.background_cut_img = self.background_img[self.offset_py: - 10: self.offset_py + height +10,
                                  self.offset_px + height +10:]
    def cv_show(self,name,img):
        cv2.imshow(name,img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def run(self):
        self.cut_background()
        return self.get_distance()

if __name__ == '__main__':
    path = r'D:\tools\pythonxianmu\picture\sildes'
    background_path = path + r'\back-1766072130.png'
    slide_path = path + r'\slide-1766072130.png'
    distance_px = 28
    main = CalculateDistance(background_path,slide_path,distance_px,distance_px,1)











