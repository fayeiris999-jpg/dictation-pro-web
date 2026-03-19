#!/usr/bin/env python3
"""
DictationPro AI - 用户认证模块
支持教师/学生登录、JWT Token 管理
"""

import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# 简单的 JWT 实现（不依赖外部库）
class SimpleJWT:
    """简易 JWT Token 生成/验证"""
    
    SECRET_KEY = os.getenv('JWT_SECRET', secrets.token_hex(32))
    TOKEN_EXPIRY_HOURS = 24
    
    @staticmethod
    def encode(payload: Dict[str, Any]) -> str:
        """生成 Token"""
        header = {"alg": "HS256", "typ": "JWT"}
        exp_dt = datetime.now() + timedelta(hours=SimpleJWT.TOKEN_EXPIRY_HOURS)
        payload["exp"] = exp_dt.timestamp()
        payload["iat"] = datetime.now().timestamp()
        
        header_b64 = SimpleJWT._base64_encode(json.dumps(header))
        payload_b64 = SimpleJWT._base64_encode(json.dumps(payload))
        
        signature = SimpleJWT._sign(f"{header_b64}.{payload_b64}")
        
        return f"{header_b64}.{payload_b64}.{signature}"
    
    @staticmethod
    def decode(token: str) -> Optional[Dict[str, Any]]:
        """验证并解析 Token"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            header_b64, payload_b64, signature = parts
            
            # 验证签名
            expected_sig = SimpleJWT._sign(f"{header_b64}.{payload_b64}")
            if signature != expected_sig:
                return None
            
            # 解析 payload
            payload = json.loads(SimpleJWT._base64_decode(payload_b64))
            
            # 检查过期
            exp = payload.get('exp', 0)
            exp_dt = datetime.fromtimestamp(exp)
            
            if datetime.now() > exp_dt:
                return None
            
            return payload
        except Exception as e:
            print(f"Token decode error: {e}")
            return None
    
    @staticmethod
    def _base64_encode(data: str) -> str:
        import base64
        return base64.urlsafe_b64encode(data.encode()).decode().rstrip('=')
    
    @staticmethod
    def _base64_decode(data: str) -> str:
        import base64
        # 补齐 padding
        padding = 4 - len(data) % 4
        if padding != 4:
            data += '=' * padding
        return base64.urlsafe_b64decode(data).decode()
    
    @staticmethod
    def _sign(data: str) -> str:
        return hashlib.sha256(f"{data}.{SimpleJWT.SECRET_KEY}".encode()).hexdigest()


class UserManager:
    """用户管理（基于文件存储）"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), 'data')
        self.users_file = os.path.join(self.data_dir, 'users.json')
        self.sessions_file = os.path.join(self.data_dir, 'sessions.json')
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # 初始化用户文件
        if not os.path.exists(self.users_file):
            self._save_users({})
        
        # 初始化会话文件
        if not os.path.exists(self.sessions_file):
            self._save_sessions({})
    
    def _load_users(self) -> Dict[str, Dict]:
        """加载用户数据"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_users(self, users: Dict[str, Dict]):
        """保存用户数据"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def _load_sessions(self) -> Dict[str, Dict]:
        """加载会话数据"""
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_sessions(self, sessions: Dict[str, Dict]):
        """保存会话数据"""
        with open(self.sessions_file, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
    
    def _hash_password(self, password: str, salt: str = None) -> tuple:
        """密码加盐哈希"""
        if salt is None:
            salt = secrets.token_hex(16)
        hashed = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        return hashed, salt
    
    def register(self, username: str, password: str, role: str = 'student', 
                 display_name: str = None, class_name: str = None) -> Dict:
        """注册用户"""
        users = self._load_users()
        
        # 检查用户名是否存在
        if username in users:
            return {'success': False, 'error': '用户名已存在'}
        
        # 生成密码哈希
        hashed, salt = self._hash_password(password)
        
        # 创建用户
        user_id = f"user_{secrets.token_hex(8)}"
        users[username] = {
            'user_id': user_id,
            'username': username,
            'password_hash': hashed,
            'salt': salt,
            'role': role,  # 'teacher' or 'student'
            'display_name': display_name or username,
            'class_name': class_name,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        self._save_users(users)
        
        # 生成 Token
        token = SimpleJWT.encode({
            'user_id': user_id,
            'username': username,
            'role': role
        })
        
        return {
            'success': True,
            'user_id': user_id,
            'username': username,
            'role': role,
            'display_name': display_name or username,
            'class_name': class_name or '',
            'token': token
        }
    
    def login(self, username: str, password: str) -> Dict:
        """用户登录"""
        users = self._load_users()
        
        # 检查用户是否存在
        if username not in users:
            return {'success': False, 'error': '用户名或密码错误'}
        
        user = users[username]
        
        # 验证密码
        hashed, _ = self._hash_password(password, user['salt'])
        if hashed != user['password_hash']:
            return {'success': False, 'error': '用户名或密码错误'}
        
        # 更新最后登录时间
        user['last_login'] = datetime.now().isoformat()
        self._save_users(users)
        
        # 生成 Token
        token = SimpleJWT.encode({
            'user_id': user['user_id'],
            'username': username,
            'role': user['role']
        })
        
        return {
            'success': True,
            'user_id': user['user_id'],
            'username': username,
            'role': user['role'],
            'display_name': user['display_name'],
            'class_name': user.get('class_name'),
            'token': token
        }
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """验证 Token"""
        payload = SimpleJWT.decode(token)
        if not payload:
            return None
        
        # 检查用户是否存在
        users = self._load_users()
        for user in users.values():
            if user['user_id'] == payload.get('user_id'):
                return {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'role': user['role'],
                    'display_name': user['display_name'],
                    'class_name': user.get('class_name')
                }
        
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """根据 ID 获取用户"""
        users = self._load_users()
        for user in users.values():
            if user['user_id'] == user_id:
                return {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'role': user['role'],
                    'display_name': user['display_name'],
                    'class_name': user.get('class_name')
                }
        return None
    
    def list_students_by_class(self, class_name: str) -> list:
        """获取班级学生列表"""
        users = self._load_users()
        students = []
        for user in users.values():
            if user['role'] == 'student' and user.get('class_name') == class_name:
                students.append({
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'display_name': user['display_name']
                })
        return students
    
    def list_all_classes(self) -> list:
        """获取所有班级列表"""
        users = self._load_users()
        classes = set()
        for user in users.values():
            if user['role'] == 'student' and user.get('class_name'):
                classes.add(user['class_name'])
        return sorted(list(classes))


# 全局用户管理器实例
user_manager = UserManager()


if __name__ == '__main__':
    # 测试
    print("测试用户注册...")
    result = user_manager.register('teacher1', 'password123', 'teacher', '王老师')
    print(f"注册结果：{result}")
    
    print("\n测试用户登录...")
    result = user_manager.login('teacher1', 'password123')
    print(f"登录结果：{result}")
    
    print("\n测试 Token 验证...")
    if result['success']:
        verified = user_manager.verify_token(result['token'])
        print(f"验证结果：{verified}")
