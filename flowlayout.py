#!/usr/bin/env python

"""PyQt4 port of the layouts/flowlayout example from Qt v4.x"""

from PyQt4 import QtCore, QtGui


# ------------------------------------------------------------------------
class FlowLayout(QtGui.QLayout):
    """
    Standard PyQt examples FlowLayout modified to work with a scollable parent
    """
    
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setMargin(margin)

        self.setSpacing(spacing)

        self.itemList = []


    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)


    def addItem(self, item):
        self.itemList.append(item)


    def count(self):
        return len(self.itemList)


    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None


    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None


    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))


    def hasHeightForWidth(self):
        return True


    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height


    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)


    def sizeHint(self):
        return self.minimumSize()


    def minimumSize(self):
        size = QtCore.QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2 * self.margin(), 2 * self.margin())
        return size

    def minimumSize(self):
        w = self.geometry().width()
        h = self.doLayout(QtCore.QRect(0, 0, w, 0), True)
        return QtCore.QSize(w + 2 * self.margin(), h + 2 * self.margin())
    


    def doLayout(self, rect, testOnly=False):
        """
        """
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(QtGui.QSizePolicy.PushButton, QtGui.QSizePolicy.PushButton, QtCore.Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QtGui.QSizePolicy.PushButton, QtGui.QSizePolicy.PushButton, QtCore.Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


# ------------------------------------------------------------------------
class ResizeScrollArea(QtGui.QScrollArea):
    """
    A QScrollArea that propagates the resizing to any FlowLayout children.
    """
    
    def __init(self, parent=None):  
        QtGui.QScrollArea.__init__(self, parent)


    def resizeEvent(self, event):
        wrapper = self.findChild(QtGui.QWidget)
        flow = wrapper.findChild(FlowLayout)
        
        if wrapper and flow:            
            width = self.viewport().width()
            height = flow.heightForWidth(width)
            size = QtCore.QSize(width, height)
            point = self.viewport().rect().topLeft()
            flow.setGeometry(QtCore.QRect(point, size))
            self.viewport().update()

        super(ResizeScrollArea, self).resizeEvent(event)



class SpriteAnimation(object):
    #https://stackoverflow.com/questions/14019468/pyqt4-and-tiles-animation
    def __init__(self, image_path, sprite_width, sprite_height, label):
        pixmap = QtGui.QPixmap(image_path)

        width, height = pixmap.width(), pixmap.height()
        self.pixmaps = []
        for x in range(0, width, sprite_width):
            for y in range(0, height, sprite_height):
                self.pixmaps.append(pixmap.copy(x, y, 
                                                sprite_width, sprite_height))
        self._current_frame = 0
        self.label = label
        self.label.setPixmap(self.pixmaps[self._current_frame])

    def play(self, interval=100):
        self._timer = QtCore.QTimer(interval=interval,
                                    timeout=self._animation_step)
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def _animation_step(self):
        self.label.setPixmap(self.pixmaps[self._current_frame])
        self.label.update()
        self._current_frame += 1
        if self._current_frame >= len(self.pixmaps):
            self._current_frame = 0

class labelSprite(QtGui.QFrame):
    itemSelected = QtCore.pyqtSignal()

    def __init__(self, image_path, sprite_width, sprite_height,info,parent= None):
        """
          
        """
        super(labelSprite,self).__init__(parent)
        self.setLayout( QtGui.QVBoxLayout(self) )
        self.labelAnim = QtGui.QLabel()
        self.sprite = SpriteAnimation(image_path, sprite_width, sprite_height,self.labelAnim)
        self.labelText = QtGui.QPushButton("TOTO")
        self.labelText.setToolTip("<h1>titi</h1><br> toto <br> ttutut")
        self.labelAnim.setToolTip("<h1>titi</h1><br> toto <br> ttutut")
        self.layout().addWidget(self.labelAnim)
        self.layout().addWidget(self.labelText,QtCore.Qt.AlignCenter )
        #self.sprite.play()

    def mouseDoubleClickEvent(self, event):
        self.itemSelected.emit()
        print("Double click ")

    def enterEvent(self, event):
        self.sprite.play()

    def leaveEvent(self, event):
        self.sprite.stop()

    def match(self, text):
        return random.randint(0,2)==1

# ------------------------------------------------------------------------
class ScrollingFlowWidget(QtGui.QWidget):
    """
    A resizable and scrollable widget that uses a flow layout.
    Use its addWidget() method to flow children into it.
    """
    
    def __init__(self,parent=None):
        super(ScrollingFlowWidget,self).__init__(parent)
        grid = QtGui.QGridLayout(self)
        scroll = ResizeScrollArea()
        self._wrapper = QtGui.QWidget(scroll)
        self.flowLayout = FlowLayout(self._wrapper)
        self._wrapper.setLayout(self.flowLayout)
        scroll.setWidget(self._wrapper)
        scroll.setWidgetResizable(True)
        grid.addWidget(scroll)


    def addWidget(self, widget):
        self.flowLayout.addWidget(widget)
        widget.setParent(self._wrapper)


# ------------------------------------------------------------------------
if __name__ == '__main__':

    import sys
    import random


    class ExampleScroller(ScrollingFlowWidget):
        def sizeHint(self):
            return QtCore.QSize(500,300)


    class ExampleWindow(QtGui.QWidget):
        def __init__(self): 
            super(ExampleWindow, self).__init__()

            self.scroller = ExampleScroller(self)
            self.setLayout( QtGui.QVBoxLayout(self) )
            hlayout = QtGui.QHBoxLayout(self)
            self.button = QtGui.QPushButton("Search")
            self.button.pressed.connect(self.matchElem)
            self.edit = QtGui.QLineEdit()
            self.edit.editingFinished.connect(self.matchElem)
            hlayout.addWidget(self.edit)
            hlayout.addWidget(self.button) 
            self.layout().addLayout(hlayout)
            self.layout().addWidget(self.scroller)
            self.elem = {}
            for n in range(20):
                self.elem[n] = labelSprite("animation.png",256,256,"aaa")
                self.elem[n].itemSelected.connect(self.elemSelected)
                self.scroller.addWidget(self.elem[n])

            """
            for w in range( random.randint(25,50))
                words = " ".join([ "".join([ chr(random.choice(range(ord('a'),ord('z'))))  
                            for x in range( random.randint(2,9) ) ])  
                                for n in range(random.randint(1,5)) ]).title()
                widget = QtGui.QPushButton(words)
                self.scroller.addWidget(widget)
            """
            self.setWindowTitle("Scrolling Flow Layout")

        def matchElem(self):
            for n in self.elem:
                if self.elem[n].match(self.edit.text()):
                    self.elem[n].show()
                else:
                    self.elem[n].hide()

        def elemSelected(self):
            print(self.sender())


    app = QtGui.QApplication(sys.argv)
    mainWin = ExampleWindow()
    mainWin.show()
    sys.exit(app.exec_())