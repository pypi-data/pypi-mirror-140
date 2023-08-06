import inspect
import pandas as pd
import copy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
import LibHanger.Library.uwLogger as Logger

class recset():
    
    """
    レコードセットクラス
    """

    class rowState():

        """
        行状態クラス
        """
        
        noChanged = 0
        """ 変更なし """
        
        added = 1
        """ 追加 """
        
        modified = 2
        """ 変更 """
        
        deleted = 3
        """ 削除 """
        
    def __init__(self, t, __session = None, __where = None) -> None:
        
        """
        コンストラクタ
        
        Parameters
        ----------
        t : Any
            Modelクラス
        __session : Any
            DBセッション
        __where : Any
            Where条件
        """
        
        # Modelクラス
        self.modelType = t

        # DBセッション保持
        self.__session = __session
        
        # カラム情報
        self.__columns = self.__getColumnAttr()
        
        # 主キー情報
        self.__primaryKeys = self.__getPrimaryKeys()

        # レコードセット行初期化
        self.rows = []
        if self.__session is None or __where is None:
            self.rows = []
        else:
            self.filter(__where)
        
        # 現在行位置
        self.__currentRowIndex = -1
        
    @property
    def session(self):
        
        """
        DBセッション
        """
        
        return self.__session
    
    def setSession(self, __session):

        """
        DBセッションセット
        """

        if self.__session is None:
            self.__session = __session
    
    def __getColumnAttr(self):
        
        """
        モデルクラスのインスタンス変数(列情報)取得

        Parameters
        ----------
        None
        
        """
        
        # インスタンス変数取得
        attributes = inspect.getmembers(self.modelType, lambda x: not(inspect.isroutine(x)))
        
        # 特定のインスタンス変数を除外してリストとしてインスタンス変数を返す
        return list(filter(lambda x: not(x[0].startswith("__") or x[0].startswith("_") or x[0] == "metadata" or x[0] == "registry"), attributes))
    
    def __getPrimaryKeys(self):
        
        """
        主キー情報取得

        Parameters
        ----------
        None
        
        """
        
        # 主キーリスト作成            
        primaryKeys = []
        for col in self.__columns:

            memberInvoke = getattr(self.modelType, col[0])            
            if memberInvoke.primary_key == True:
                primaryKeys.append(col[0])
        
        # 主キー情報を返す
        return primaryKeys
    
    def __getPKeyFilter(self, row):
        
        """
        主キー条件取得
        
        row : Any
            行情報
        """
        
        # 主キー条件リスト初期化
        pKeyList = []
        
        # 主キーのみで条件を組み立て
        for key in self.__getPrimaryKeys():
            w = (getattr(self.modelType, key) == getattr(row, key))
            pKeyList.append(w)
        
        # 主キー条件リストをtupleに変換して返す
        return and_(*tuple(pKeyList))
    
    def newRow(self):
        
        """
        新規行を生成する

        Parameters
        ----------
        None

        """

        # 行生成
        row = self.modelType()
        # 行状態をaddedに変更
        row.__rowState = self.rowState.added
        # 行情報生成
        return self.rowSetting(row)
    
    def editRow(self):
        
        """
        編集行を取得する

        Parameters
        ----------
        None

        """
        
        # rowsのカレント行の行状態をmodifiedに変更
        self.rows[self.__currentRowIndex].__rowState = self.rowState.modified
        # rowsのカレント行を返す
        return self.rows[self.__currentRowIndex]
    
    def rowSetting(self, row):
        
        """
        行情報を生成する
        
        Parameters
        ----------
        None
        
        """
        
        for col in self.__columns:

            # Modelのインスタンス変数取得
            memberInvoke = getattr(self.modelType, col[0])
            # 既定値の設定
            setattr(row, col[0], memberInvoke.default.arg)
        
        # 生成した行を返す                                 
        return row
    
    def columns(self):
        
        """
        カラム情報プロパティ
        """
        
        return self.__columns
    
    def addRow(self, row):
        
        """
        レコードセットに行を追加する
        
        Parameters
        ----------
        row : Any
            追加する行情報
        """
        
        self.rows.append(row)
    
    def delRow(self):
        
        """
        レコードセットのカレント行を削除対象とする
        """

        self.rows[self.__currentRowIndex]._recset__rowState = self.rowState.deleted
        
    def eof(self):
        
        """
        レコードセットの行情報有無を返す
        
        Parameters
        ----------
        None
        
        """

        # カレント行インデックス++
        self.__currentRowIndex += 1

        return False if len(self.rows) > self.__currentRowIndex else True
    
    def primaryKeys(self):
        
        """
        主キー情報プロパティ
        """
        
        return self.__primaryKeys
    
    def getCurrentRow(self):
        
        """
        カレント行を取得する
        """        
        
        # カレント行を返す
        return self.rows[self.__currentRowIndex]
    
    def getDataFrame(self):
        
        """
        Model⇒DataFrameに変換する

        Parameters
        ----------
        None

        """
        
        rowlist = []
        if len(self.rows) == 0:
            for column in self.__columns:
                rowlist.append(column[0])
        else:            
            # 行インスタンスをDeepCopy
            targetRows = copy.deepcopy(self.rows)
            # DataFrame化で不要な列を削除
            for rowInstance in targetRows:
                delattr(rowInstance, '_sa_instance_state')
            # 行インスタンスをリスト化
            rowlist = list(map(lambda f: vars(f), targetRows))

        # rowlistをDataFrame変換
        df = pd.DataFrame(rowlist) if len(self.rows) > 0 else pd.DataFrame(columns=rowlist)
        
        # DataFrameに主キー設定
        if len(self.__primaryKeys) > 0 and len(self.rows) > 0:
            df = df.set_index(self.__primaryKeys, drop=False)
                
        # 戻り値を返す
        return df
    
    def filter(self, w):
        
        """
        レコードセットをフィルタする

        Parameters
        ----------
        w : any
            where条件
        """
        
        # クエリ実行
        self.rows = []
        q = self.__session.query(self.modelType).filter(w).all()
        for row in q:
            # 行状態をnoChangedに変更
            row.__rowState = self.rowState.noChanged
            # rowsにクエリ結果を追加
            self.rows.append(row)
    
    def existsPKeyRec(self, row):
        
        """
        対象行に対して主キー制約に違反しているか
        
        row : Any
            行情報
        """
        
        # 主キーを条件として該当レコードが存在するか確認
        w = self.__getPKeyFilter(row)
        q = self.__session.query(self.modelType).filter(w).all()

        # 結果を返す
        return len(q) > 0

    def upsert(self):

        """
        データ更新(upsert用)
        
        Notes
        -----
            rowState = addedとした行を追加する際に主キー違反している場合、強制的にmodifiedとして扱う。\n
            recsetに存在する追加行(rowState = added)全てに対して存在チェックが走るので \n
            件数によっては更新にかなりの時間を要する。
            削除行に関してはレコード抽出後にdeleteメソッドを走らせるはずなので存在チェックは行っていない。          
        """

        return self.update(True)
        
    def update(self, upsert = False):
        
        """
        データ更新(通常用)
        
        Notes
        -----
            rowState = addedとした行を追加する際に主キー違反していればSQLAlchemyErrorとなる。\n
            recset側でDBとの制約を解決していればupsertよりこちらのほうが速度は上
        """

        result = False
        
        try:
        
            # 新規行はaddする
            newRows = [row for row in self.rows if row._recset__rowState == self.rowState.added]
            for newRow in newRows:
                # 主キー違反していない行のみadd
                if upsert == False or not self.existsPKeyRec(newRow):
                    self.__session.add(newRow)

            # 削除行はdeleteする
            delRows = [row for row in self.rows if row._recset__rowState == self.rowState.deleted]
            for delRow in delRows:
                self.__session.delete(delRow)

            # Commit
            self.__session.commit()

            # 処理結果セット
            result = True
            
        except SQLAlchemyError as e:
            
            # エラーログ出力
            Logger.logging.error(e)

            # Rollback
            self.__session.rollback()
        
        # 処理結果を返す
        return result