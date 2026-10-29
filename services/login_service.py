import uuid

from sqlalchemy.orm import Session

from models.login_model import Login
from models.response_model import Response_Model
from models.user_model import User, UserRequest
from repositories.login_repository import LoginRepository
from repositories.coach_repository import CoachRepository
from repositories.learner_repository import LearnerRepository
import utils.constants as constants
import utils.utils as utils

class LoginService:

    def __init__(self):
        self.repository = LoginRepository()
        self.coach_repository = CoachRepository()
        self.learner_repository = LearnerRepository

    def find_login(self, db: Session, username: str) -> Response_Model[Login]:
        res: Response_Model = Response_Model(status=constants.SUCCESS, message=utils.res_status_msg(constants.LOGIN, constants.SUCCESS))
        login = self.repository.find_coach_login(db, username)
        res.data = login
        return res

    def create_login_cocach(self, db: Session, login_request: UserRequest) -> Response_Model[Login]:
        res: Response_Model = Response_Model(status=constants.SUCCESS, message=utils.res_status_msg(constants.LOGIN, constants.SUCCESS))

        find_user = self.coach_repository.find_user(db, login_request, isPassword=True)
        print(find_user)
        if not find_user:
            res.status = constants.ERROR
            res.message = utils.res_status_msg(constants.LOGIN, constants.ERROR, "Users does not exist or password not match")
            return res
        find_login = self.repository.find_login_coach(db, login_request["username"])
        if find_login:
            res.status = constants.ERROR
            res.message = utils.res_status_msg(constants.LOGIN, constants.ERROR, "Login already exists")
            return res

        login_data: Login = Login(
            username=login_request["username"],
            session=self.generate_session_id()
        )

        result: User = self.repository.create_login_cocach(db, login_data)
        if result:
            res.data = result
        return res 

    def create_login_learner(self, db: Session, login_request: UserRequest) -> Response_Model[Login]:
        res: Response_Model = Response_Model(status=constants.SUCCESS, message=utils.res_status_msg(constants.LOGIN, constants.SUCCESS))
    
        find_user = self.learner_repository.find_user(db, login_request, isPassword=True)
        print(find_user)
        if not find_user:
            res.status = constants.ERROR
            res.message = utils.res_status_msg(constants.LOGIN, constants.ERROR, "Users does not exist or password not match")
            return res
        find_login = self.repository.find_login_learner(db, login_request["username"])
        if find_login:
            res.status = constants.ERROR
            res.message = utils.res_status_msg(constants.LOGIN, constants.ERROR, "Login already exists")
            return res
    
        login_data: Login = Login(
            username=login_request["username"],
            session=self.generate_session_id()
        )
    
        result: User = self.repository.create_login_learner(db, login_data)
        if result:
            res.data = result
        return res 


    def logout_coach(self, db: Session, logout: dict) -> Response_Model[Login]:
        res: Response_Model = Response_Model(status=constants.SUCCESS, 
                                                  message=utils.res_status_msg(constants.LOGOUT, constants.SUCCESS))
        find_login = self.repository.find_login_by_session_coach(db, logout["session"])
        if not find_login:
            res.status = constants.ERROR
            res.message =  utils.res_status_msg(constants.LOGOUT, constants.ERROR, "Login session does not exist")
            return res 

        result: bool = self.repository.logout_coach(db, logout["session"])
        if result == False:
            res.status = constants.ERROR
            res.message = utils.res_status_msg(constants.LOGOUT, constants.ERROR)

        return res
    
    
    def logout_learner(self, db: Session, logout: dict) -> Response_Model[Login]:
            res: Response_Model = Response_Model(status=constants.SUCCESS, 
                                                      message=utils.res_status_msg(constants.LOGOUT, constants.SUCCESS))
            find_login = self.repository.find_login_by_session_learner(db, logout["session"])
            if not find_login:
                res.status = constants.ERROR
                res.message =  utils.res_status_msg(constants.LOGOUT, constants.ERROR, "Login session does not exist")
                return res 
    
            result: bool = self.repository.logout_learner(db, logout["session"])
            if result == False:
                res.status = constants.ERROR
                res.message = utils.res_status_msg(constants.LOGOUT, constants.ERROR)
    
            return res

    def generate_session_id(self) -> str:
        return str(uuid.uuid4())