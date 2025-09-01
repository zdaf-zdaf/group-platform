from .clients import UserServiceClient, ExperimentServiceClient

class NoticeService:
    @staticmethod
    def get_author_name(author_id, request=None):
        client = UserServiceClient()
        if request:
            # 传递当前用户的JWT Token
            token = AccessToken.for_user(request.user)
            client.set_jwt_token(token)
            
        user_info = client.get_user_info(author_id)
        return user_info.get('username', '未知') if user_info else '未知'
    
    @staticmethod
    def get_experiment_info(experiment_id, request=None):
        if not experiment_id:
            return None
            
        client = ExperimentServiceClient()
        if request:
            token = AccessToken.for_user(request.user)
            client.set_jwt_token(token)
            
        return client.get_experiment_info(experiment_id)
    
    @staticmethod
    def validate_teacher_role(user_id, request=None):
        client = UserServiceClient()
        if request:
            token = AccessToken.for_user(request.user)
            client.set_jwt_token(token)
            
        return client.validate_teacher_role(user_id)