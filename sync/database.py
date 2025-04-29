import sqlite3
from log import log
import os
import json
import datetime
import sys


class Database:

    @staticmethod
    def trace_callback(statement):
        log.info(f"{statement}")

    def __enter__(self):
        log.info(os.getcwd())
        # 获取应用程序的根目录路径
        if getattr(sys, "frozen", False):
            # 如果是打包后的可执行文件
            application_path = os.path.dirname(sys.executable)
        else:
            # 如果是开发环境
            application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        # 确保数据库目录存在
        db_dir = os.path.join(application_path, 'output', 'db')
        os.makedirs(db_dir, exist_ok=True)
        
        # 连接数据库并返回实例以供使用
        db_path = os.path.join(db_dir, 'sync.db')
        log.info(f"数据库路径: {db_path}")
        self.conn = sqlite3.connect(db_path)
        self.conn.set_trace_callback(Database.trace_callback)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # 关闭连接，即使遇到异常也会执行
        self.conn.close()

    def execute(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            log.exception(f"execute error occurred: ")
            self.conn.rollback()
        finally:
            cursor.close()

    def query(self, query):
        cursor = self.conn.cursor()
        results = None
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            # 获取列名
            columns = [col[0] for col in cursor.description]

            # 转换为字典列表
            dict_list = [dict(zip(columns, row)) for row in results]
            return dict_list
        except Exception as e:
            log.exception(f"query error occurred: ")
            raise e
        finally:
            cursor.close()

    def init(self):
        cursor = self.conn.cursor()

        # 创建笔记同步记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS note_sync_rec (
                id INTEGER PRIMARY KEY AUTOINCREMENT, -- 记录的唯一标识符，自增主键
                doc_guid TEXT NOT NULL UNIQUE, -- 文档的全局唯一标识符
                type TEXT, -- 文档的类型
                title TEXT NOT NULL, -- 文档的标题
                category TEXT, -- 文档的分类
                created INTEGER, -- 文档创建时间
                accessed INTEGER, -- 最后访问时间
                url TEXT, -- 文档的链接
                sync_status INTEGER, -- 同步状态（0为未同步，1为已同步）
                fail_reason TEXT, -- 同步失败的原因
                sync_time TEXT,-- 同步成功时间
                create_time TIMESTAMP default (datetime('now', 'localtime')),
                update_time TIMESTAMP default (datetime('now', 'localtime'))
            )
        ''')

        # 创建笔记图片同步记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS note_image_sync_rec (
                id INTEGER PRIMARY KEY AUTOINCREMENT, -- 图片的唯一标识符，自增主键
                doc_guid TEXT NOT NULL, -- 关联文档的全局唯一标识符
                file_name TEXT NOT NULL, -- 图片名称
                upload_url TEXT,-- 上传图片地址
                created INTEGER, -- 图片添加时间
                sync_status INTEGER, -- 同步状态（0为未同步，1为已同步）
                fail_reason TEXT, -- 同步失败的原因
                sync_time TEXT,-- 同步成功时间
                create_time TIMESTAMP default (datetime('now', 'localtime')),
                update_time TIMESTAMP default (datetime('now', 'localtime'))
            )
        ''')

        # 提交创建表的事务
        self.conn.commit()
        # 使用完后，关闭cursor
        cursor.close()

    def get_pending_sync_note_list(self, wiz_note_list):
        # 如果wiz_note_list 是空, 直接返回空集合
        if not wiz_note_list:
            return []

        # wiz_note_list map doc_guid, 去数据库中查询是否存在, 获取不存在的笔记id集合
        doc_guids = ','.join(map(lambda note: f"'{note['docGuid']}'", wiz_note_list))
        not_in_db_notes = self.query(f"SELECT doc_guid FROM note_sync_rec WHERE doc_guid IN ({doc_guids})")

        log.info(f"not_in_db_notes: {not_in_db_notes}")
        if not not_in_db_notes:
            return wiz_note_list

        # wiz_note_list filter 不存在的笔记id, 返回过滤后的笔记
        return list(filter(lambda note: note['docGuid'] not in not_in_db_notes, wiz_note_list))

    def insert_note_list(self, note_list):
        if not note_list:
            return

        # 将 note_list 转换为 data, 为了 executemany
        data = list(map(lambda note: (note['docGuid'], note['type'], note['title'],
                                      note['category'], note['created'], note['accessed'],
                                      note['url'], 0),
                        note_list))

        # 将note_list中的笔记插入到数据库中
        cursor = self.conn.cursor()
        cursor.execute('BEGIN TRANSACTION')
        try:
            cursor.executemany('''
                INSERT OR IGNORE INTO note_sync_rec (doc_guid, type, title, category, created, accessed, url, sync_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
            self.conn.commit()
        except Exception as e:
            log.exception(f"insert_note_list error occurred: ")
            self.conn.rollback()
        finally:
            cursor.close()

    def get_unsync_note_list(self, max_version, page_size):
        rows = self.query(f'''
            SELECT id, doc_guid, type, title, category, created, accessed, url FROM note_sync_rec
            WHERE sync_status in (0, -1) and id > {max_version}
            LIMIT {page_size}
        ''')
        return [dict(row) for row in rows]


    def get_uploaded_images(self, doc_guid, need_upload_images):
        """
        获取已经上传过的图片(即使上传失败了)
        :param doc_guid:
        :param need_upload_images:
        :return:
        """
        # need_upload_images 需要 join,
        need_upload_images = ','.join(map(lambda image: f"'{image}'", need_upload_images))

        rows = self.query(f'''
            SELECT file_name FROM note_image_sync_rec
            WHERE doc_guid = '{doc_guid}' and file_name in ({need_upload_images})
        ''')
        # 提取其中的 file_name 作为list 返回
        return list(map(lambda row: row['file_name'], rows))

    def create_image_upload_record(self, doc_guid, img_file_name):
        """
        插入同步图片记录, 初始化同步状态为0
        :param doc_guid:
        :param img_file_name:
        :return:
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO note_image_sync_rec (doc_guid, file_name, sync_status)
            VALUES (?, ?, 0)
        ''', (doc_guid, img_file_name))
        self.conn.commit()

    def update_note_sync_status(self, doc_guid, sync_status, fail_reason):
        log.info(f"update_note_sync_status: {doc_guid}, {sync_status}, {fail_reason}")

        # 如果 sync_status 为 True, 表示同步成功, 同步时间更新为当前时间
        # 否则同步失败, 更新同步原因
        cursor = self.conn.cursor()
        if sync_status is True:
            # 同步成功
            # 根据你的具体数据表结构和字段名，执行更新同步时间的操作
            update_query = "UPDATE note_sync_rec SET sync_time = datetime('now'), sync_status = 1 WHERE doc_guid = ?"
            cursor.execute(update_query, (doc_guid,))
        else:
            # 同步失败
            # 根据你的具体数据表结构和字段名，执行更新同步失败原因的操作
            update_query = "UPDATE note_sync_rec SET fail_reason = ? , sync_status = -1 WHERE doc_guid = ?"
            cursor.execute(update_query, (fail_reason, doc_guid))

        # 提交事务
        self.conn.commit()
        cursor.close()

    def update_img_sync_status(self, doc_guid,img_file_name, sync_status, fail_reason, upload_url):
        log.info(f"update_img_sync_status: {doc_guid}, {img_file_name}, {sync_status}, {fail_reason}")

        # 如果 sync_status 为 True, 表示同步成功, 同步时间更新为当前时间
        # 否则同步失败, 更新同步原因
        cursor = self.conn.cursor()
        if sync_status is True:
            # 同步成功
            current_time = datetime.datetime.now()
            # 根据你的具体数据表结构和字段名，执行更新同步时间的操作
            update_query = "UPDATE note_image_sync_rec SET sync_time = datetime('now'),upload_url = ?, sync_status = 1 WHERE doc_guid = ? and file_name = ?"
            cursor.execute(update_query, (upload_url, doc_guid, img_file_name))
        else:
            # 同步失败
            # 根据你的具体数据表结构和字段名，执行更新同步失败原因的操作
            update_query = "UPDATE note_image_sync_rec SET fail_reason = ? , sync_status = -1 WHERE doc_guid = ? and file_name = ?"
            cursor.execute(update_query, (fail_reason, doc_guid, img_file_name))
        cursor.close()

    def get_note_count(self):
        return self.query(f'''
            SELECT count(*) as cnt FROM note_sync_rec
        ''')[0]['cnt']

    def select_by_guid(self, doc_guid):
        rows = self.query(f'''
            SELECT id, doc_guid, type, title, category, created, accessed, url FROM note_sync_rec
            WHERE doc_guid = '{doc_guid}'
        ''')
        return rows[0]



