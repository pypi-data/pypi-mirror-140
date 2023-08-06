import jsondb, pymysql, json, time
from datetime import datetime
from zoomtools import safe

connect = pymysql.connect

class SqlManager(jsondb.Manager):
    """Add on to Json DB"""
    
    def __init__(self, con, db_id="debug", table_name="jsondb", default={}, everyload=False):
        self.table_name = table_name
        self.db_id = db_id
        self.con = con
        self.con.autocommit = False
        self.con.cursorclass = pymysql.cursors.DictCursor
        super().__init__("", default, everyload)
    
    def load(self):
        cursor = self.con.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS `%s`(id varchar(255), _data TEXT, last_edit varchar(255), create_date varchar(255))" % self.table_name)
        cursor.execute("SELECT `_data` FROM `%s`" % self.table_name)
        sql_db = cursor.fetchall()
        print(sql_db)
        if self.db_id not in sql_db:
            self.db = self.default
            cursor.execute("INSERT INTO `%s` (id, _data, create_date) VALUES('%s', '%s', '%s')" % (self.table_name, self.db_id, json.dumps(self.db, ensure_ascii=False), datetime.now().strftime("%H:%M:%S %d.%m.%y | " + str(int(time.time())))))
        else:
            self.db = json.loads(sql_db[self.db_id]['_data'], encoding="cp1251")
        self.con.commit()
                
    def import_dbfile(self, path):
        try:
            f = open(path, "r")
            self.db = json.load(f)
            safe(lambda: f.close())
            return self.db
        except Exception as err:
            safe(lambda: f.close())
            return err

    def export_dbfile(self, path):
        try:
            f = open(path, "w")
            json.dump(f)
            f.close()
            return self.db
        except Exception as err:
            f.close()
            return err

    def save(self):
        cursor = self.con.cursor()
        cursor.execute("UPDATE `%s` SET `_data`='%s', `last_edit`='%s' WHERE `id`='%s'" % (self.table_name, json.dumps(self.db, ensure_ascii=False), datetime.now().strftime("%H:%M:%S %d.%m.%y | " + str(int(time.time()))), self.db_id))
        self.con.commit()
        return True
        
    def delete(self):
        cursor = self.con.cursor()
        cursor.execute("ALTER TABLE `%s` DROP `%s`;" % self.table_name, self.db_id)
        self.con.commit()
        return True

# ---------------------------------------- #
# | Add on created by Zoom Developer     | #
# | VK: vk.com/zoom_developer            | #
# | DISCORD: Zoom aka Дурка#1185         | # 
# ---------------------------------------- #