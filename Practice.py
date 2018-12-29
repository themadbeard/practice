# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtSql, QtWidgets


class AutoIncrement(QtWidgets.QItemDelegate):
    def __init__(self, parent=None):
        super(AutoIncrement, self).__init__(parent)

    def createEditor(self, parent, option, index): pass

    def setEditorData(self, editor, index): pass

    def setModelData(self, editor, model, index): pass


class BoolDelegate(QtWidgets.QItemDelegate):

    def __init__(self, parent=None):
        super(BoolDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        self.drawCheck(painter, option, option.rect,
                       QtCore.Qt.Checked if index.data() == 'TRUE' else QtCore.Qt.Unchecked)
        self.drawFocus(painter, option, option.rect)

    def editorEvent(self, event, model, option, index):
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            return model.setData(index, 'FALSE' if index.data() == 'TRUE' else 'TRUE', QtCore.Qt.EditRole)
        return False


class Page(QtWidgets.QWidget):
    def __init__(self, model, appname, parent=None):
        super(Page, self).__init__(parent)
        self.view = QtWidgets.QTableView()
        self.view.setModel(model)
        self.view.setItemDelegateForColumn(0, AutoIncrement(self.view))
        self.view.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.view.setAlternatingRowColors(True)
        self.view.setSortingEnabled(True)
        self.view.setItemDelegate(QtSql.QSqlRelationalDelegate(self.view))

        self.insertButton = QtWidgets.QPushButton(u"Вставить")
        self.insertButton.clicked.connect(self.insert)

        self.removeButton = QtWidgets.QPushButton(u"Удалить")
        self.removeButton.clicked.connect(self.remove)

        self.updateButton = QtWidgets.QPushButton(u"Обновить")
        self.updateButton.clicked.connect(self.update)

        self.saveButton = QtWidgets.QPushButton(u"Сохранить")
        self.saveButton.clicked.connect(self.save)

        self.undoButton = QtWidgets.QPushButton(u"Отменить")
        self.undoButton.clicked.connect(self.undo)

        self.popMenu = QtWidgets.QMenu(self.view)
        self.popMenu.addAction(u"Вставить", self.insert)
        self.popMenu.addAction(u"Удалить", self.remove)
        self.popMenu.addSeparator()
        self.popMenu.addAction(u"Обновить", self.update)
        self.popMenu.addAction(u"Сохранить", self.save)
        self.popMenu.addAction(u"Отменить", self.undo)
        self.view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.view.customContextMenuRequested.connect(self.onContextMenu)
        #self.connect(self.view, QtCore.SIGNAL("customContextMenuRequested(const QPoint &)"), self.onContextMenu)

        viewselectionModel = self.view.selectionModel()
        viewselectionModel.selectionChanged.connect(self.updateActions)

        self.view.model().dataChanged.connect(self.dataChanged)

        self.hasUndo = False

        buttonsLayout = QtWidgets.QHBoxLayout()
        buttonsLayout.addWidget(self.insertButton)
        buttonsLayout.addWidget(self.removeButton)
        buttonsLayout.addStretch(1)
        buttonsLayout.addWidget(self.updateButton)
        buttonsLayout.addWidget(self.saveButton)
        buttonsLayout.addWidget(self.undoButton)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addWidget(self.view)
        self.mainLayout.addLayout(buttonsLayout, 1)

        self.setLayout(self.mainLayout)
        self.readSettings()

        self.updateActions()

    def dataChanged(self):

        self.hasUndo = True
        self.updateActions()

    def insert(self):

        if self.view.selectionModel().currentIndex().isValid():
            row = self.view.currentIndex().row()
            record = self.view.model().record(row)
            record.remove(0)
            self.view.model().insertRow(row)
            self.view.model().setRecord(row, record)
        else:
            row = self.view.model().rowCount()
            record = self.view.model().record()
            record.remove(0)
            self.view.model().insertRow(row)
            self.view.model().setRecord(row, record)
            self.hasUndo = True
            self.updateActions()

    def remove(self):

        model = self.view.model()
        for r in set((i.row() for i in self.view.selectedIndexes())):
            model.removeRow(r)
            self.hasUndo = True
            self.updateActions()

    def update(self):

        self.view.model().select()
        self.hasUndo = False
        self.updateActions()

    def save(self):

        self.view.model().submitAll()
        lastError = self.view.model().lastError()
        if lastError.isValid():
            QtWidgets.QMessageBox.warning(self, u"Ошибка при запросе", lastError.text(), QtWidgets.QMessageBox.Ok)
        else:
            self.hasUndo = False
            self.updateActions()

    def undo(self):

        self.view.model().revertAll()
        self.hasUndo = False
        self.updateActions()

    def updateActions(self):

        hasSelection = not self.view.selectionModel().selection().isEmpty()
        hasCurrent = self.view.selectionModel().currentIndex().isValid()
        self.removeButton.setEnabled(hasSelection)
        self.updateButton.setEnabled(self.hasUndo)
        self.saveButton.setEnabled(self.hasUndo)
        self.undoButton.setEnabled(self.hasUndo)

    def onContextMenu(self, point):

        hasSelection = not self.view.selectionModel().selection().isEmpty()

        self.popMenu.actions()[1].setEnabled(hasSelection)
        self.popMenu.actions()[2].setEnabled(self.hasUndo)
        self.popMenu.actions()[3].setEnabled(self.hasUndo)
        self.popMenu.actions()[4].setEnabled(self.hasUndo)
        self.popMenu.exec_(self.view.mapToGlobal(point))

    def readSettings(self):

        settings = QtCore.QSettings(appname, self.view.model().tableName())
        for i in range(self.view.model().columnCount()):
            self.view.setColumnWidth(i, int(settings.value(u"column%d" % i, 60)))

    def writeSettings(self):

        settings = QtCore.QSettings(appname, self.view.model().tableName())
        for i in range(self.view.model().columnCount()):
            settings.setValue(u"column%d" % i, self.view.columnWidth(i))


class PageIngredients(Page):
    def __init__(self, parent=None):
        model = QtSql.QSqlTableModel()
        model.setTable(u'Ингредиенты')
        model.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        model.select()

        super(PageIngredients, self).__init__(model, parent)


class PagePizzas(Page):
    def __init__(self, parent=None):
        model = QtSql.QSqlTableModel()
        model.setTable(u'Пицца')
        model.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        model.select()

        super(PagePizzas, self).__init__(model, appname, parent)


class PageOrders(Page):
    def __init__(self, parent=None):
        model = QtSql.QSqlRelationalTableModel()
        model.setTable(u'ПиццаЗаказ')
        model.setRelation(1, QtSql.QSqlRelation(u"Пицца", u"код", u"название"))
        model.setHeaderData(1, QtCore.Qt.Horizontal, u"Наименование пиццы", QtCore.Qt.DisplayRole)

        model.setRelation(2, QtSql.QSqlRelation(u"Заказ", u"код", u"статус"))
        model.setHeaderData(2, QtCore.Qt.Horizontal, u"Статус заказа", QtCore.Qt.DisplayRole)

        model.setRelation(3, QtSql.QSqlRelation(u"Клиенты", u"код", u"адрес"))
        model.setHeaderData(3, QtCore.Qt.Horizontal, u"Адрес доставки", QtCore.Qt.DisplayRole)
        model.select()
        super(PageOrders, self).__init__(model, appname, parent)


class PageCustomer(Page):
    def __init__(self, parent=None):
        model = QtSql.QSqlTableModel()
        model.setTable(u'Клиенты')
        model.setEditStrategy(QtSql.QSqlTableModel.OnManualSubmit)
        model.select()

        super(PageCustomer, self).__init__(model, appname, parent)


class DateDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(DateDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QDateEdit(parent)
        editor.setDisplayFormat('yyyy-MM-dd')
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        editor.setDate(QtCore.QDate.fromString(value, 'yyyy-MM-dd'))
        if index.column() == 3:
            editor.setMaximumDate(QtCore.QDate.fromString(model.record(index.row()).value(4), 'yyyy-MM-dd'))
        else:
            assert index.column() == 4
            editor.setMinimumDate(QtCore.QDate.fromString(model.record(index.row()).value(3), 'yyyy-MM-dd'))

    def setModelData(self, editor, model, index):
        value = editor.date().toString('yyyy-MM-dd')
        model.setData(index, value, QtCore.Qt.EditRole)
        self.view.setItemDelegateForColumn(3, DateDelegate(self.view))

        self.view.setItemDelegateForColumn(4, DateDelegate(self.view))
        self.view.setItemDelegateForColumn(5, BoolDelegate(self.view))
        self.view.setItemDelegateForColumn(6, BoolDelegate(self.view))


class ConfigDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)

        self.setWindowTitle(appname)

        self.contentsWidget = QtWidgets.QListWidget()
        self.contentsWidget.setMovement(QtWidgets.QListView.Static)
        self.contentsWidget.setMaximumWidth(180)
        self.contentsWidget.setSpacing(2)

        self.pagesWidget = QtWidgets.QStackedWidget()
        self.pages = [PageIngredients(), PagePizzas(), PageOrders(), PageCustomer()]
        for p in self.pages:
            self.pagesWidget.addWidget(p)

        button = QtWidgets.QListWidgetItem(self.contentsWidget)

        button.setText(u"Ингредиенты")
        button.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        button = QtWidgets.QListWidgetItem(self.contentsWidget)
        button.setText(u"Пиццы")
        button.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        button = QtWidgets.QListWidgetItem(self.contentsWidget)
        button.setText(u"Заказы")
        button.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        button = QtWidgets.QListWidgetItem(self.contentsWidget)
        button.setText(u"Клиенты")
        button.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

        self.contentsWidget.currentItemChanged.connect(self.changePage)
        self.contentsWidget.setCurrentRow(0)

        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.addWidget(self.contentsWidget)
        horizontalLayout.addWidget(self.pagesWidget, 1)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(horizontalLayout)

        self.setLayout(mainLayout)
        self.readSettings()

    def changePage(self, current, previous):

        if not current:
            current = previous
        self.pagesWidget.setCurrentIndex(self.contentsWidget.row(current))

    def closeEvent(self, event):
        dbase.close()
        self.writeSettings()
        return super(ConfigDialog, self).closeEvent(event)

    def readSettings(self):

        settings = QtCore.QSettings(appname, appname)
        pos = settings.value(u"pos", QtCore.QPoint(200, 200))
        size = settings.value(u"size", QtCore.QSize(400, 400))
        self.resize(size)
        self.move(pos)

    def writeSettings(self):
        settings = QtCore.QSettings(appname, appname)
        settings.setValue(u"pos", self.pos())
        settings.setValue(u"size", self.size())

        for p in self.pages:
            p.writeSettings()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    QtCore.QLocale.setDefault(QtCore.QLocale("ru_RU"))

    global dbase

    dbase = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    dbase.setDatabaseName(u'пиццерия.sqlite')
    dbase.open()

    global appname
    appname = u'Пиццерия'

    dialog = ConfigDialog()
    sys.exit(dialog.exec_())
