"""
Role-Based Access Control (RBAC) middleware and authorization
"""
from __future__ import annotations
from typing import Callable, Optional, Set
from functools import wraps
from starlette.requests import Request
from starlette.responses import JSONResponse
from .auth import JWTManager
from .models import UserRole


class Permission:
    """Permission definitions"""
    
    # Prediction permissions
    PREDICT = "predict"
    VIEW_EVIDENCE = "view_evidence"
    VIEW_SAFETY = "view_safety"
    
    # User management
    CREATE_USER = "create_user"
    MANAGE_USERS = "manage_users"
    ASSIGN_ROLES = "assign_roles"
    
    # System management
    TOGGLE_RAG = "toggle_rag"
    TOGGLE_AI = "toggle_ai"
    VIEW_SYSTEM_HEALTH = "view_system_health"
    
    # Audit and logging
    VIEW_AUDIT_LOGS = "view_audit_logs"
    VIEW_COMPLIANCE_LOGS = "view_compliance_logs"
    VIEW_METRICS = "view_metrics"


class RolePermissions:
    """Map roles to permissions"""
    
    PERMISSIONS_MAP = {
        UserRole.DOCTOR: {
            Permission.PREDICT,
            Permission.VIEW_EVIDENCE,
            Permission.VIEW_SAFETY,
        },
        UserRole.AUDITOR: {
            Permission.VIEW_EVIDENCE,
            Permission.VIEW_SAFETY,
            Permission.VIEW_AUDIT_LOGS,
            Permission.VIEW_COMPLIANCE_LOGS,
            Permission.VIEW_METRICS,
        },
        UserRole.ADMIN: {
            # Admin has all permissions
            Permission.PREDICT,
            Permission.VIEW_EVIDENCE,
            Permission.VIEW_SAFETY,
            Permission.CREATE_USER,
            Permission.MANAGE_USERS,
            Permission.ASSIGN_ROLES,
            Permission.TOGGLE_RAG,
            Permission.TOGGLE_AI,
            Permission.VIEW_SYSTEM_HEALTH,
            Permission.VIEW_AUDIT_LOGS,
            Permission.VIEW_COMPLIANCE_LOGS,
            Permission.VIEW_METRICS,
        }
    }

    @classmethod
    def has_permission(cls, role: UserRole, permission: str) -> bool:
        """Check if role has permission"""
        return permission in cls.PERMISSIONS_MAP.get(role, set())

    @classmethod
    def get_permissions(cls, role: UserRole) -> Set[str]:
        """Get all permissions for a role"""
        return cls.PERMISSIONS_MAP.get(role, set())


class AuthorizationMiddleware:
    """Middleware for authorization checks"""
    
    @staticmethod
    async def __call__(scope, receive, send):
        """Process request through authorization"""
        if scope["type"] != "http":
            return

        request = Request(scope)
        
        # Extract token
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            await request.app.middleware_stack(scope, receive, send)
            return

        token = auth_header[7:]
        is_valid, payload = JWTManager.verify_token(token)
        
        if is_valid:
            # Attach user info to request state
            scope["user"] = payload
        
        await request.app.middleware_stack(scope, receive, send)


def require_auth(func: Callable) -> Callable:
    """Decorator to require authentication"""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user = getattr(request.state, "user", None)
        
        if not user:
            # Try to extract from header
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                is_valid, payload = JWTManager.verify_token(token)
                if is_valid:
                    request.state.user = payload
                    user = payload

        if not user:
            return JSONResponse(
                {"error": "Unauthorized - Missing or invalid token"},
                status_code=401
            )

        if not user.get("is_active"):
            return JSONResponse(
                {"error": "Unauthorized - Account disabled"},
                status_code=403
            )

        return await func(request, *args, **kwargs)
    
    return wrapper


def require_role(*roles: UserRole) -> Callable:
    """Decorator to require specific role(s)"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = getattr(request.state, "user", None)
            
            if not user:
                return JSONResponse(
                    {"error": "Unauthorized - Missing or invalid token"},
                    status_code=401
                )

            user_role = UserRole(user.get("role"))
            if user_role not in roles:
                return JSONResponse(
                    {"error": f"Forbidden - Required role: {[r.value for r in roles]}"},
                    status_code=403
                )

            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_permission(permission: str) -> Callable:
    """Decorator to require specific permission"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = getattr(request.state, "user", None)
            
            if not user:
                return JSONResponse(
                    {"error": "Unauthorized - Missing or invalid token"},
                    status_code=401
                )

            user_role = UserRole(user.get("role"))
            if not RolePermissions.has_permission(user_role, permission):
                return JSONResponse(
                    {"error": f"Forbidden - Required permission: {permission}"},
                    status_code=403
                )

            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


class AccessControl:
    """Fine-grained access control"""
    
    @staticmethod
    def user_can_predict(user: dict) -> bool:
        """Check if user can submit predictions"""
        role = UserRole(user.get("role"))
        return RolePermissions.has_permission(role, Permission.PREDICT)

    @staticmethod
    def user_can_manage_users(user: dict) -> bool:
        """Check if user can manage other users"""
        role = UserRole(user.get("role"))
        return RolePermissions.has_permission(role, Permission.MANAGE_USERS)

    @staticmethod
    def user_can_toggle_features(user: dict) -> bool:
        """Check if user can toggle AI features"""
        role = UserRole(user.get("role"))
        return role == UserRole.ADMIN

    @staticmethod
    def user_can_view_metrics(user: dict) -> bool:
        """Check if user can view system metrics"""
        role = UserRole(user.get("role"))
        return RolePermissions.has_permission(role, Permission.VIEW_METRICS)
