import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

 
class FramelessMainWindow(QWidget):
	def __init__(self):
		QWidget.__init__(self)
		self.init_layout()
		self.init_frameless()


	def init_layout(self):
		self.main_layout    = QVBoxLayout()
		self.main_window    = QMainWindow()
		self.main_title_bar = FramelessTitleBar()

		self.main_layout.setSpacing(0)
		self.main_layout.addWidget(self.main_title_bar)
		self.main_layout.addWidget(self.main_window)
		self.main_window.setCentralWidget(QMdiArea())
		self.main_window.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
		self.setLayout(self.main_layout)

		self.main_title_bar.minimize_signal.connect(self.showMinimized)
		self.main_title_bar.maximize_signal.connect(lambda : self.showNormal() if self.isMaximized() else self.showMaximized())
		self.main_title_bar.close_signal.connect(self.close)
		self.main_title_bar.move_signal.connect(lambda pos : None if self.isMaximized() else self.move(pos) )
	

	def init_frameless(self):
		self.edge_sense_dist  = 3
		self.resize_activated = False
		self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		self.setMouseTracking(True)


	def showMaximized(self):
		QWidget.show(self)
		QWidget.showMaximized(self)

	def resizeEvent(self, event):
		self.eliminate_border(self.isMaximized())

	def eliminate_border(self, state):

		border_width = (not state) * (self.edge_sense_dist)
		self.main_layout.setContentsMargins(QMargins(border_width, border_width, border_width, border_width))
		self.setCursor(Qt.ArrowCursor)

	def mouseMoveEvent(self, event):
		if not self.isMaximized():
			event_to_left_border   = (event.globalPos()-self.frameGeometry().topLeft()).x()
			event_to_right_border  = (event.globalPos()-self.frameGeometry().bottomRight()).x()
			event_to_top_border    = (event.globalPos()-self.frameGeometry().topLeft()).y()
			event_to_bottom_border = (event.globalPos()-self.frameGeometry().bottomRight()).y()

			at_left_border         = abs(event_to_left_border)    < self.edge_sense_dist
			at_right_border        = abs(event_to_right_border)   < self.edge_sense_dist
			at_top_border          = abs(event_to_top_border)     < self.edge_sense_dist
			at_bottom_border       = abs(event_to_bottom_border)  < self.edge_sense_dist

			sense_array            = [      at_left_border,       at_right_border,       at_top_border,       at_bottom_border]
			dist_array             = [event_to_left_border, event_to_right_border, event_to_top_border, event_to_bottom_border]

			print (sense_array)
			if not self.resize_activated == True:
				self.previous_sense = sense_array
				self.previous_dist  = dist_array
				if   sense_array in ([1, 0, 1, 0], [0, 1, 0, 1]):
					self.setCursor(Qt.SizeFDiagCursor)
				elif sense_array in ([1, 1, 0, 0], [0, 0, 1, 1]):
					self.setCursor(Qt.SizeBDiagCursor)
				elif sense_array in ([1, 0, 0, 0], [0, 1, 0, 0]):
					self.setCursor(Qt.SizeHorCursor)
				elif sense_array in ([0, 0, 1, 0], [0, 0, 0, 1]):
					self.setCursor(Qt.SizeVerCursor)
				else:
					self.setCursor(Qt.ArrowCursor)

			if self.resize_activated == True:
				n = [dist * sense for sense, dist in zip(self.previous_sense, self.previous_dist)]
				m = [dist * sense for sense, dist in zip(self.previous_sense,         dist_array)]
				delta_left, delta_right, delta_top, delta_bottom = [dist - predist  for dist, predist in zip(m, n)]
				if (self.width() - delta_left >= self.minimumWidth() and self.height()- delta_top >= self.minimumHeight()):
					self.setGeometry(self.x()+delta_left, self.y()+delta_top, self.width()-delta_left+delta_right, self.height()-delta_top+delta_bottom)
					self.update()


	def mousePressEvent(self,event):
		if event.button() == Qt.LeftButton and sum(self.previous_sense)>0:
			self.resize_activated = True

			
	def mouseReleaseEvent(self,event):
		if event.button() == Qt.LeftButton:
			self.resize_activated = False

	def paintEvent(self, event):
		self.backgroundColor = QColor(0, 0, 0, 1);#hex2QColor("efefef")
		self.foregroundColor = QColor(0, 0, 0, 1);#hex2QColor("333333")
		self.borderRadius = 5    	
		# get current window size
		s = self.size()
		qp = QPainter()
		qp.begin(self)
		qp.setRenderHint(QPainter.Antialiasing, True)
		qp.setPen(self.foregroundColor)
		qp.setBrush(self.backgroundColor)
		qp.drawRoundedRect(0, 0, s.width(), s.height(),
						   self.borderRadius, self.borderRadius)
		qp.end()

	def setMouseTracking(self, flag):
		def recursive_set(parent):
			for child in parent.findChildren(QObject):
				try:

					child.setMouseTracking(flag)
				except:
					pass
				recursive_set(child)
		QWidget.setMouseTracking(self, flag)
		recursive_set(self)

class FramelessTitleBar(QWidget):
	minimize_signal = pyqtSignal()
	maximize_signal = pyqtSignal()
	close_signal    = pyqtSignal()
	move_signal     = pyqtSignal(QPoint)

	def __init__(self):
		super().__init__()
		self.setStyleSheet('QWidget{font: 8pt "Inconsolata";}')
		# self.setAutoFillBackground(True)
		# p = self.palette()
		# p.setColor(self.backgroundRole(), Qt.red)
		# self.setPalette(p)
		self.setMouseTracking(True)
		self.borderRadius = 3   	
		self.backgroundColor = QColor(255, 255, 255, 180)
		self.foregroundColor = QColor(0, 0, 0, 0)

		self.ori_pos = None
		self.title_icon      = QLabel()
		pixmap = QPixmap("./src/default_icon.png")
		pixmap = pixmap.scaledToHeight(20)
		self.title_icon.setPixmap(pixmap)
		self.title_label     = QLabel("Python")
		self.minimize_button = Title_button("-", 10, 10 ,5)
		self.maximize_button = Title_button("[]", 20, 20,10)
		self.close_button    = Title_button("x", 20, 20,10)
		self.setContentsMargins(QMargins(0,0,0,0))
		self.minimize_button.setContentsMargins(QMargins(0,0,0,0))
		self.maximize_button.setContentsMargins(QMargins(0,0,0,0))
		self.close_button.setContentsMargins(QMargins(0,0,0,0))
		self.minimize_button.clicked.connect(lambda : self.minimize_signal.emit())
		self.maximize_button.clicked.connect(lambda : self.maximize_signal.emit())
		self.close_button.clicked.connect(   lambda : self.close_signal.emit())

		self.main_layout = HBox(5, self.title_icon, 10, self.title_label ,-1, self.minimize_button, self.maximize_button, self.close_button, 5)
		self.main_layout.setSpacing(2)
		self.main_layout.setContentsMargins(QMargins(0,0,0,0))
		self.setLayout(self.main_layout)
		self.setFixedHeight(25)

	def setMouseTracking(self, flag):
		def recursive_set(parent):
			for child in parent.findChildren(QObject):
				try:

					child.setMouseTracking(flag)
				except:
					pass
				recursive_set(child)
		QWidget.setMouseTracking(self, flag)
		recursive_set(self)

	def setWindowTitle(self, title):
		self.title_label.setText(title)

	def paintEvent(self, event):
		s = self.size()
		qp = QPainter()
		qp.begin(self)
		qp.setRenderHint(QPainter.Antialiasing, True)
		qp.setPen(self.foregroundColor)
		qp.setBrush(self.backgroundColor)
		path = RoundCornerRect(s.width(), s.height(), self.borderRadius, self.borderRadius, 0, 0)
		qp.drawPath(path)
		qp.end()



	def mousePressEvent(self,event):
		if event.button() == Qt.LeftButton:
			self.ori_pos = event.pos()

	def mouseReleaseEvent(self,event):
		if event.button() == Qt.LeftButton:
			self.ori_pos = None

	def mouseMoveEvent(self,event):
		self.setCursor(Qt.ArrowCursor)
		if self.ori_pos:
			self.move_signal.emit(event.globalPos()-self.ori_pos)
		event.accept()


	def mouseDoubleClickEvent (self, event):
		self.maximize_signal.emit()

class Title_button(QPushButton):
	def __init__(self, text="", w=10, h=10, r=0):
		super().__init__()
		self.setText(text)
		self.setFixedHeight(h)
		self.setFixedWidth(w)
		self.borderRadius = r
		self.backgroundColor = QColor(255, 0, 0, 180)
		self.foregroundColor = QColor(0, 0, 0, 0)

	def paintEvent(self, event):
		s = self.size()
		qp = QPainter()
		qp.begin(self)
		qp.setRenderHint(QPainter.Antialiasing, True)
		qp.setPen(self.foregroundColor)
		qp.setBrush(self.backgroundColor)
		path = RoundCornerRect(s.width(), s.height(), self.borderRadius, self.borderRadius,self.borderRadius,self.borderRadius)
		qp.drawPath(path)
		qp.end()

class RoundCornerRect(QPainterPath):
	def __init__(self, w, h, r1, r2, r3, r4):
		super().__init__()
		self.addPolygon(QPolygonF([QPointF(0, r1), QPointF(r1, 0), QPointF(w-r2, 0), QPointF(w, r2), QPointF(w, h-r3), QPointF(w-r3, h), QPointF(r4, h), QPointF(0, h-r4)]))
		self.addEllipse(QPoint(  r1,   r1), r1, r1)
		self.addEllipse(QPoint(w-r2,   r2), r2, r2)
		self.addEllipse(QPoint(w-r3, h-r3), r3, r3)
		self.addEllipse(QPoint(  r4, h-r4), r4, r4)
		self.simplified()
		self.setFillRule(Qt.WindingFill)

class BoxLayout(QBoxLayout):
	def __init__(self, direction, ui_list):
		super().__init__(direction)

		if ui_list:
			for item in ui_list:
				if isinstance(item, int):
					if item >= 0:
						self.addSpacing(item)
					else:
						self.addStretch()
				elif issubclass(type(item), QWidget):
					self.addWidget(item)
				elif issubclass(type(item), QLayout):
					self.addLayout(item)
				else:
					raise TypeError("item %s with object type %s is not supported) " % (item, type(item)))


class HBox(BoxLayout):
	def __init__(self, *ui_list):
		super().__init__(QBoxLayout.LeftToRight, ui_list)
		

class VBox(BoxLayout):
	def __init__(self, *ui_list):
		self.setDirection(QBoxLayout.TopToBottom, ui_list)		




if __name__ == '__main__':
	app = QApplication(sys.argv)
	frame = FramelessMainWindow()
	frame.show()    
	app.exec_()
	sys.exit