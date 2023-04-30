import blog
import packagebuild
import sqlite3
import manager

from threading import Lock

PKG_CONTENT_STORAGE_FILE="pkgcontent.db"

class storage():
    
    # only one thread can access an sqlite object at a time
    lock = Lock()
    
    @staticmethod
    def populate():
        blog.debug("Acquiring Database lock")
        
        try:
            db_connection = sqlite3.connect(PKG_CONTENT_STORAGE_FILE)
            storage.lock.acquire()
            cur = db_connection.cursor()

            res = cur.execute("SELECT name FROM sqlite_master")
            
            existing_tables = res.fetchone()
            if(existing_tables is None or "files" not in existing_tables):
                blog.info("Creating table..")
                cur.execute("CREATE TABLE IF NOT EXISTS files(pkgname, filepath)")
                
            blog.debug("Releasing Database lock")
        except Exception as ex:
            blog.error("Could not populate database: {}".format(ex))
            manager.manager.report_system_event("PKGCONTENTSTORAGE", "CRITICAL-ERROR: {}".format(ex))

        storage.lock.release()
    
    @staticmethod
    def insert_package_content(pkgname: str, paths: list) -> bool:
        """
        """

        try:
            storage.lock.acquire()
            db_connection = sqlite3.connect(PKG_CONTENT_STORAGE_FILE)
            cur = db_connection.cursor()
            
            # delete old entries from this package
            cur.execute("DELETE FROM files WHERE pkgname = ?", (pkgname, ))
            db_connection.commit()

            # insert the new provided files using
            # a tuple so we can use executemany
            _tuples = [ ]

            for path in paths:
                _tuples.append((pkgname, path))

            cur.executemany("INSERT INTO files VALUES (?,?)", _tuples)
            db_connection.commit()
            storage.lock.release()
            return True

        except Exception as ex:
            blog.error("Could not add to database: {}".format(ex))
            manager.manager.report_system_event("PKGCONTENTSTORAGE", "CRITICAL-ERROR: {}".format(ex))
            storage.lock.release()
            return True

    @staticmethod
    def check_file_conflicts(paths: list) -> list:

        try:
            storage.lock.acquire()
            db_connection = sqlite3.connect(PKG_CONTENT_STORAGE_FILE)
            cur = db_connection.cursor()

            file_conflicts: list = [ ]
            
            for path in paths:
                res = cur.execute("SELECT pkgname FROM files WHERE filepath = ?", (path,))
                content_result = res.fetchone()

                if(content_result is None):
                    continue
                
                file_conflicts.append({
                    content_result[0]: path
                })

            storage.lock.release()
            return file_conflicts

        except Exception as ex:
            blog.error("Could not check database: {}".format(ex))
            manager.manager.report_system_event("PKGCONTENTSTORAGE", "CRITICAL-ERROR: {}".format(ex))
            storage.lock.release()
            return [ ] 
        
    @staticmethod
    def get_file_owner(path: str) -> str:
        try:
            storage.lock.acquire()
            db_connection = sqlite3.connect(PKG_CONTENT_STORAGE_FILE)
            cur = db_connection.cursor()

            res = cur.execute("SELECT pkgname FROM files WHERE filepath = ?", (path,))

            owner = res.fetchone()

            if(owner is None):
                storage.lock.release()
                return None

            storage.lock.release()
            return owner[0]

        except Exception as ex:
            pass