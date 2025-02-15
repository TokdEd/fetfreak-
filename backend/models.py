import edgedb

# 假設有一個User模型
class User:
    def __init__(self, id: int, name: str, email: str, password: str = None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

    @classmethod
    def from_edgeql(cls, data: dict):
        """
        從 EdgeDB 查詢結果創建 User 實例
        """
        return cls(
            id=data['id'],
            name=data['name'],
            email=data['email'],
            password=data.get('password')  # 密碼可能是空的
        )

# 這個方法可以用來查詢 User 資料
async def get_user_by_id(db, user_id: int) -> User:
    """
    通過用戶 ID 查詢用戶
    """
    query = """
        SELECT User {
            id,
            name,
            email,
            password
        }
        FILTER .id = <int>$user_id
    """
    result = await db.query_single(query, user_id=user_id)
    if result:
        return User.from_edgeql(result)
    return None

async def get_user_by_email(db, email: str) -> User:
    """
    通過電子郵件查詢用戶
    """
    query = """
        SELECT User {
            id,
            name,
            email,
            password
        }
        FILTER .email = <str>$email
    """
    result = await db.query_single(query, email=email)
    if result:
        return User.from_edgeql(result)
    return None

async def create_user(db, name: str, email: str, password: str) -> User:
    """
    創建一個新用戶並返回用戶對象
    """
    query = """
        INSERT User {
            name := <str>$name,
            email := <str>$email,
            password := <str>$password
        }
        RETURNING User {
            id,
            name,
            email,
            password
        }
    """
    result = await db.query_single(query, name=name, email=email, password=password)
    if result:
        return User.from_edgeql(result)
    return None

async def update_user(db, user_id: int, name: str = None, email: str = None, password: str = None) -> User:
    """
    更新用戶資料並返回更新後的用戶對象
    """
    set_clause = []
    params = {'user_id': user_id}

    if name:
        set_clause.append('name := <str>$name')
        params['name'] = name
    if email:
        set_clause.append('email := <str>$email')
        params['email'] = email
    if password:
        set_clause.append('password := <str>$password')
        params['password'] = password

    if not set_clause:
        return None

    query = f"""
        UPDATE User
        FILTER .id = <int>$user_id
        SET {{
            {', '.join(set_clause)}
        }}
        RETURNING User {{
            id,
            name,
            email,
            password
        }}
    """
    result = await db.query_single(query, **params)
    if result:
        return User.from_edgeql(result)
    return None

async def delete_user(db, user_id: int) -> bool:
    """
    刪除用戶
    """
    query = """
        DELETE User
        FILTER .id = <int>$user_id
    """
    try:
        await db.query(query, user_id=user_id)
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False