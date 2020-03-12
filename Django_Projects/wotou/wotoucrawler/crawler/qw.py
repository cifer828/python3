from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication


class Crawler():
    def __init__(self):
        self.settings().setMaximumPagesInCache(0)
        self.settings().setObjectCacheCapacities(0, 0, 0)
        self.settings().setOfflineStorageDefaultQuota(0)
        self.settings().setOfflineWebApplicationCacheQuota(0)
        # self.settings().setAttribute(QWebSettings.AutoLoadImages, False)
        self.loadFinished.connect(self._result_available)

    def start(self):
        # self.load(QUrl('http://stackoverflow.com/'))
        self.load(QUrl('https://movie.douban.com/chart'))

    def _result_available(self, ok):
        print('got it!')
        self.settings().clearMemoryCaches()  # it doesn't help
        self.settings().clearIconDatabase()
        self.start()  # next try

if __name__ == '__main__':
    app = QApplication([])
    crawler = Crawler()
    crawler.start()
    app.exec_()
