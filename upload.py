import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
from tornado.options import define, options

# import BigFileHandler

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/upload", UploadHandler),
            (r'/bigFileUpload', BigFileHandler),
            (r'/upload_success', MergeHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("upload_form.html")


class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        file1 = self.request.files['file1'][0]
        original_fname = file1['filename']
        extension = os.path.splitext(original_fname)[1]
        fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
        final_filename = fname + extension
        output_file = open("uploads/" + final_filename, 'wb')
        output_file.write(file1['body'])
        # file1['body'].save("uploads/" + final_filename)
        self.finish("file" + final_filename + " is uploaded")


class BigFileHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('big get')

    def post(self):
        # print('big post')
        # 获取文件的唯一标识符
        task = self.get_argument('task_id')
        chunk = self.get_argument(name='chunk', default=0)  # 获取该分片在所有分片中的序号
        filename = '%s%s' % (task, chunk)  # 构造该分片的唯一标识符
        print(filename)
        upload_file = self.request.files['file'][0]
        # print(type(upload_file)) #tornado.httputil.HTTPFile
        # upload_file.save('./uploads/%s' % filename)  # 保存分片到本地
        output_file = open('./uploads/%s' % filename, 'wb')
        output_file.write(upload_file['body'])

        self.finish("file" + filename + " is uploaded")


class MergeHandler(tornado.web.RequestHandler):
    def get(self):
        print('merge get')
        target_filename = self.get_argument('filename')  # 获取上传文件的文件名
        task = self.get_argument('task_id')  # 获取文件的唯一标识符
        chunk = 0  # 分片序号
        with open('./uploads/%s' % target_filename, 'wb') as target_file:  # 创建新文件
            while True:
                try:
                    filename = './uploads/%s%d' % (task, chunk)
                    source_file = open(filename, 'rb')  # 按序打开每个分片
                    target_file.write(source_file.read())  # 读取分片内容写入新文件
                    source_file.close()
                except IOError:
                    break

                chunk += 1
                os.remove(filename)  # 删除该分片，节约空间

        self.finish("file merged" + target_filename)


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
