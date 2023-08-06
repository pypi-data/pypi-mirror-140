# 从关键字文件导入基类
from yhproject_pkg.framework.key_word.keyword_web import WebKeys


class MenuPage(WebKeys):
    def table_manage(self):
        self.locator("xpath", "/html/body/section/div/span/ul/li[2]/span").click()
        self.wait(3)

    def menu_icon(self):
        self.locator("xpath", "/html/body/section/div/div[1]/div/i").click()
        self.wait(3)

    # 数据开发
    def menu_sjkf(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/section/ul/li[1]/div/span").click()
        self.wait(3)

    # 数据管控
    def menu_sjgk(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/section/ul/li[2]/div/span").click()
        self.wait(3)

    # 数据分类分级
    def sjgk_sjflfj_sjfl(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[4]/dd[1]").click()
        self.wait(3)

    def sjgk_sjflfj_sjfj(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[4]/dd[2]").click()
        self.wait(3)

    def sjgk_sjfl_iframe(self):
        self.switch_iframe("id", "yhdgp:controll:classification:sensitivityLevel")
        self.wait(3)

    def sjgk_sjfj_iframe(self):
        self.switch_iframe("id", "yhdgp:controll:classification:dataClassification")
        self.wait(3)

    # 脱敏规则
    def sjgk_sjaq_tmgz(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[5]/dd[1]").click()
        self.wait(3)

    def sjgk_tmgz_iframe(self):
        self.switch_iframe("id", "yhdgp:controll:dataSafe:antianaphylaxisRule")
        self.wait(3)

    # 数据脱敏
    def sjgk_sjaq_sjtm(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[5]/dd[2]").click()
        self.wait(3)

    def sjgk_sjtm_iframe(self):
        self.switch_iframe("id", "yhdgp:controll:dataSafe:dataAntianaphylaxis")
        self.wait(3)

    # 脱敏管理
    def sjgk_sjaq_tmgl(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[5]/dd[3]").click()
        self.wait(3)

    def sjgk_tmgl_iframe(self):
        self.switch_iframe("id", "yhdgp:controll:dataSafe:antianaphylaxisManage")
        self.wait(3)

    # 规则库管理
    def sjgk_sjzl_gzkgl(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[3]/dd[1]").click()
        self.wait(3)

    def sjgk_gzkgl_iframe(self):
        self.switch_iframe("id", "yhdgp:controll:dataQuality:ruleBase")
        self.wait(3)

    # 数据质量规则管理
    def sjgk_sjzl_sjzlgzgl(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[3]/dd[2]").click()
        self.wait(3)

    def sjgk_sjzlgzgl_iframe(self):
        self.switch_iframe("id", "yhdgp:controll:dataQuality:dataRuleManage")
        self.wait(3)

    # 数据服务
    def menu_sjfw(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/section/ul/li[6]/div/span").click()
        self.wait(3)

    # 数据开发-采集中心-调度管理
    def sjkf_cjzx_ddgl(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[1]/dd[4]").click()
        self.wait(3)

    def sjkf_ddgl_iframe(self):
        self.switch_iframe("id", "yhdgp:dev:collection:diaodu")
        self.wait(3)

    # 数据开发-元数据-元数据管理
    def sjgk_ysj_ysjgl(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[1]/dd[2]").click()
        self.wait(5)

    def sjgk_ysjgl_iframe(self):
        self.switch_iframe("id", "yhdgp:controll:metaData:metaDataManage")
        self.wait(3)

    # 数据服务-数据服务-权限管理
    def sjfw_sjfw_qxgl(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[2]/dd[1]").click()
        self.wait(3)

    def sjfw_qxgl_iframe(self):
        self.switch_iframe("id", "yhdgp:dataApplication:dataServer:sourceAuthorize")
        self.wait(3)

    # 数据服务-数据服务-业务主题管理
    def sjfw_sjfw_ywztgl(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[2]/dd[2]").click()
        self.wait(3)

    def sjfw_yeztgl_iframe(self):
        self.switch_iframe("id", "yhdgp:dataApplication:dataServer:apiTheme")
        self.wait(3)

    # 数据服务-数据服务-接口创建
    def sjfw_sjfw_jkcj(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[2]/dd[3]").click()
        self.wait(3)

    def sjfw_jkcj_iframe(self):
        self.switch_iframe("id", "yhdgp:dataApplication:dataServer:apiAdd")
        self.wait(3)

    # 数据服务-数据服务-接口审批
    def sjfw_sjfw_jksp(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[2]/dd[4]").click()
        self.wait(3)

    def sjfw_jksp_iframe(self):
        self.switch_iframe("id", "yhdgp:dataApplication:dataServer:apiReview")
        self.wait(3)

    # 数据服务-数据服务-接口上线管理
    def sjfw_sjfw_jksxgl(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[2]/dd[5]").click()
        self.wait(3)

    def sjfw_jksxgl_iframe(self):
        self.switch_iframe("id", "yhdgp:dataApplication:dataServer:apiOnline")
        self.wait(3)

    # 数据服务-数据服务-接口查询
    def sjfw_sjfw_jkcx(self):
        self.locator("xpath", "/html/body/section/div/section[2]/section/div[1]/section/div/div/div[2]/div/dl[2]/dd[6]").click()
        self.wait(3)

    def sjfw_jkcx_iframe(self):
        self.switch_iframe("id", "yhdgp:dataApplication:dataServer:apiList")
        self.wait(3)

