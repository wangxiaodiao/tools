#!/usr/bin/python
from transaction.base_task import *
from service.message_define import *
from test_result_enum import *

class CreateLoadBalancerTask(BaseTask):
    operate_timeout = 20
    def __init__(self, task_type, messsage_handler,
                 case_manager,logger_name):
        self.case_manager = case_manager
        #logger_name = "task.create_load_balancer"
        BaseTask.__init__(self, task_type, RequestDefine.create_load_balancer,
                          messsage_handler, logger_name)
        
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_load_balancer, result_success,
                             self.onCreateSuccess)
        self.addTransferRule(state_initial, AppMessage.RESPONSE,
                             RequestDefine.create_load_balancer, result_fail,
                             self.onCreateFail)
        self.addTransferRule(state_initial, AppMessage.EVENT,
                             EventDefine.timeout, result_any,
                             self.onCreateTimeout)             

    def invokeSession(self, session):
        """
        task start, must override
        """
        request = getRequest(RequestDefine.create_load_balancer)
        param = self.case_manager.getParam()
        control_server = param["control_server"]       
        balancer_name = param["balancer_name"]
        balancer_type = param["type"]
        port = param["port"]
        
        
        request.setString(ParamKeyDefine.name, balancer_name)
        request.setUInt(ParamKeyDefine.type, balancer_type)
        request.setUIntArray(ParamKeyDefine.port, port)
     
       
        self.info("[%08X]request create load balancere '%s' to control server '%s'"%
                       (session.session_id, balancer_name, control_server))
        session.target = balancer_name
        request.session = session.session_id
        self.setTimer(session, self.operate_timeout)
        self.sendMessage(request, control_server)

    def onCreateSuccess(self, msg, session):
        self.clearTimer(session)
        uuid = msg.getString(ParamKeyDefine.uuid)
        ip = msg.getString(ParamKeyDefine.ip)
        port = msg.getUIntArray(ParamKeyDefine.port)
        self.info("[%08X]create load balancer success"%
                       (session.session_id,uuid))
        self.case_manager.finishTestCase(TestResultEnum.success)        
        session.finish()

    def onCreateFail(self, msg, session):
        self.clearTimer(session)
        self.info("[%08X]create load balancer fail"%
                  (session.session_id))
        
        self.case_manager.finishTestCase(TestResultEnum.fail)
        session.finish()
        
    def onCreateTimeout(self, msg, session):
        self.info("[%08X]create load balancer timeout"%
                  (session.session_id))
        self.case_manager.finishTestCase(TestResultEnum.timeout)
        session.finish()

   
