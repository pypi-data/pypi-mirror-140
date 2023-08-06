import re
from datetime import datetime
import xml.etree.ElementTree as ET
import logging
from urllib.parse import urljoin

import requests

from nomadix_api.utils.decorators import parse_xml_return

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class NomadixClient(object):

    def __init__(self, base_url, user_name=None, password=None, ssl_verify=False, force_init=False):
        # USG URI will be formed with these attributes
        self.base_url = base_url

        # Username and password will be used for basic auth
        # if the nomadix is configured for ip access, these are irrelevant
        self.user_name = user_name
        self.password = password

        # to use with self signed certs, only relevant with https
        self.ssl_verify = ssl_verify

        # force session init before first call
        if force_init:
            self._init_session()

    def _init_session(self):
        self._close_session()
        self._session = requests.session()
        if self.user_name:
            self._session.auth = (self.user_name, self.password or 'dummy')
        self._session.verify = self.ssl_verify

    def _close_session(self):
        if hasattr(self, '_session'):
            self._session.close()
            delattr(self, '_session')
            return True
        return False

    @property
    def session(self):
        if not hasattr(self, '_session') or not self._session:
            self._init_session()
        return self._session

    @classmethod
    def xml_treat_raw(cls, raw_xml_str):
        '''
            Nomadix xml (from docs) are not valid xml because of the dtd definition on the doctype comment
            So this "fix" should make the xml valid and able to be used with canon libs for xml parsing like ElementTree or minidom

        '''
        return re.sub('<\!DOCTYPE ([^ >]*).*?>', '<!DOCTYPE \g<1>>', raw_xml_str)

    @classmethod
    def parse_xml_element_to_dict(cls, element):
        children = element.getchildren()
        xml_dict = {'tag': element.tag, 'attrib': element.attrib}
        if not children:
            # leaf element
            if element.text and element.text.strip():
                xml_dict['val'] = element.text
            return xml_dict

        # has children
        xml_dict['children'] = {}
        for ch in children:
            xml_dict['children'][ch.tag] = cls.parse_xml_element_to_dict(ch)
        return xml_dict

    @classmethod
    def parse_xml_to_dict(cls, raw_xml_str):
        xml_str = cls.xml_treat_raw(raw_xml_str)
        usg = ET.fromstring(xml_str)
        return cls.parse_xml_element_to_dict(usg)

    @classmethod
    def parse_xml_to_etree(cls, raw_xml_str):
        xml_str = cls.xml_treat_raw(raw_xml_str)
        return ET.fromstring(xml_str)

    @property
    def command_url(self):
        return urljoin(self.base_url, '/usg/command.xml')

    # Radius Commands

    @parse_xml_return
    def radius_login(self, user_name, password, mac_address):
        '''
            TODO:
                - make http/https an option? port should be reconsidered
        '''

        usg = ET.Element('USG', {'COMMAND': 'RADIUS_LOGIN'})
        un  = ET.SubElement(usg, 'SUB_USER_NAME')
        pw  = ET.SubElement(usg, 'SUB_PASSWORD')
        mac = ET.SubElement(usg, 'SUB_MAC_ADDR')
        psi = ET.SubElement(usg, 'PORTAL_SUB_ID')

        un.text = user_name
        pw.text = password
        mac.text = mac_address

        xml_cmd = ET.tostring(usg, encoding='UTF-8')
        logger.debug('[controller nomadix] radius_login:', self.command_url, xml_cmd.decode())
        #try:
        return self.session.post(self.command_url, data=xml_cmd, timeout=3)
        #except Exception as e:
        #    logger.error('[PACKAGE][nomadix.radius_login] command_url: %s data: %s error: %s' % (str(self.command_url), str(xml_cmd), str(e))


    @parse_xml_return
    def radius_logout(self, mac_address=None, user_name=None):
        '''
            Either mac_address is present, or user_name
        '''
        assert mac_address or user_name, 'Either mac or user_name must be present'
        usg = ET.Element('USG', {'COMMAND': 'LOGOUT'})

        if user_name:
            un  = ET.SubElement(usg, 'SUB_USER_NAME')
            un.text = user_name
        if mac_address:
            mac = ET.SubElement(usg, 'SUB_MAC_ADDR')
            mac.text = mac_address

        xml_cmd = ET.tostring(usg, encoding='UTF-8')
        logger.debug('[controller nomadix] radius_logout: ', self.command_url, xml_cmd.decode())

        return self.session.post(self.command_url, data=xml_cmd, timeout=3)

    # Subscriber Administration Commands

    @parse_xml_return
    def user_add(
            self,
            mac_address=None,
            user_name=None,
            password=None,
            encrypt=False,
            expiry_time=None,
            expiry_units='SECONDS',
            countdown=None,
            room_number=None,
            payment_method=None,
            plan=None,
            ip_type=None,
            confirmation=None,
            payment=None,
            smtp_redirect=None,
            bandwidth_up=None,
            bandwidth_down=None,
            bandwidth_max_up=None,
            bandwidth_max_down=None,
            qos_policy=None
            ):
        '''
           ┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
           ┃   argument name    ┃   type             ┃     Description                                      ┃
           ┣━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
           ┃mac_address         ┃  str[12]           ┃                                                      ┃
           ┃user_name           ┃  str[96]           ┃                                                      ┃
           ┃password            ┃  str[128],         ┃                                                      ┃
           ┃expiry_time         ┃  int/str           ┃  Expiration time                                     ┃
           ┃expiry_units        ┃  enum              ┃  Either "SECONDS", "MINUTES", "HOURS" or "DAYS"      ┃
           ┃countdown           ┃  bool              ┃                                                      ┃
           ┃room_number         ┃  str[8]            ┃                                                      ┃
           ┃payment_method      ┃  enum              ┃  Either "RADIUS", "PMS", "CREDIT_CARD", "ROOM_OPEN"  ┃
           ┃plan                ┃  str (maybe int)   ┃  To use with X over Y billing plan                   ┃
           ┃ip_type             ┃  enum              ┃  Either "PRIVATE" or "PUBLIC"                        ┃
           ┃confirmation        ┃  str               ┃  confirmation number/id                              ┃
           ┃payment             ┃  int/float/str     ┃  amount charged for access                           ┃
           ┃smtp_redirect       ┃  bool              ┃  should smtp redirection be enabled for the user     ┃
           ┃bandwidth_up        ┃  int               ┃  legacy, use BANDWIDTH_MAX_UP                        ┃
           ┃bandwidth_down      ┃  int               ┃  legacy, use BANDWIDTH_MAX_DOWN                      ┃
           ┃bandwidth_max_up    ┃  int               ┃  set here or use max_bandwidth_up                    ┃
           ┃bandwidth_max_down  ┃  int               ┃  set here or use max_bandwidth_down                  ┃
           ┃qos_policy          ┃  str               ┃  QOS policy configured on the NSE                    ┃
           ┗━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

           TODO:
            - create argument validation based on the table above (trafaret)
        '''
        usg = ET.Element('USG', {'COMMAND': 'USER_ADD'})
        if mac_address:
            usg.set('MAC_ADDR', mac_address)
        if user_name:
            un  = ET.SubElement(usg, 'USER_NAME')
            un.text = user_name
        if password:
            pw  = ET.SubElement(usg, 'PASSWORD', {'ENCRYPT': 'TRUE' if encrypt else 'FALSE'})
            pw.text = password
        if expiry_time:
            exp_time = ET.SubElement(usg, 'EXPIRY_TIME', {'UNITS': expiry_units})
            exp_time.text = str(expiry_time)
        if countdown:
            ctdw = ET.SubElement(usg, 'COUNTDOWN')
            ctdw.text = '1' if countdown else '0'
        if room_number:
            roomn = ET.SubElement(usg, 'ROOM_NUMBER')
            roomn.text = str(room_number)
        if payment_method:
            pymt = ET.SubElement(usg, 'PAYMENT_METHOD')
            pymt.text = payment_method
        if plan:
            pl = ET.SubElement(usg, 'PLAN')
            pl.text = str(plan)
        if ip_type:
            ipt = ET.SubElement(usg, 'IP_TYPE')
            ipt = ip_type
        if confirmation:
            confm = ET.SubElement(usg, 'CONFIRMATION')
            confm.text = str(confirmation)
        if payment:
            pm = ET.SubElement(usg, 'PAYMENT')
            pm.text = str(payment)
        if smtp_redirect:
            smtpr = ET.SubElement(usg, 'SMTP_REDIRECT') # Either TRUE or FALSE
            smtpr.text = 'TRUE' if smtp_redirect else 'FALSE'
        if bandwidth_up:
            bwu = ET.SubElement(usg, 'BANDWIDTH_UP')
            bwu.text = str(bandwidth_up)
        if bandwidth_down:
            bwd = ET.SubElement(usg, 'BANDWIDTH_DOWN')
            bwd.text = str(bandwidth_down)
        if bandwidth_max_up:
            bwmu = ET.SubElement(usg, 'BANDWIDTH_MAX_UP')
            bwmu.text = str(bandwidth_max_up)
        if bandwidth_max_down:
            bwmd = ET.SubElement(usg, 'BANDWIDTH_MAX_DOWN')
            bwmd.text = str(bandwidth_max_down)
        if qos_policy:
            qosp = ET.SubElement(usg, 'QOS_POLICY')
            qosp.text = str(qos_policy)

        xml_cmd = ET.tostring(usg, encoding='UTF-8')
        logger.debug('[controller nomadix] user_add:', self.command_url, xml_cmd.decode())

        return self.session.post(self.command_url, data=xml_cmd, timeout=3)

    @parse_xml_return
    def update_cache(self, mac_address, payment_method=None):
        usg = ET.Element('USG', {'COMMAND': 'CACHE_UPDATE'})
        usg.set('MAC_ADDR', mac_address)
        if payment_method:
            pymt = ET.SubElement(usg, 'PAYMENT_METHOD')
            pymt.text = payment_method

        xml_cmd = ET.tostring(usg, encoding='UTF-8')
        logger.debug('[controller nomadix] update_cache:', self.command_url, xml_cmd.decode())

        return self.session.post(self.command_url, data=xml_cmd, timeout=3)

    @parse_xml_return
    def bandwidth_up(self, mac_address, bandwidth_up):
        '''
            BANDWIDTH is measured in kbps
        '''

        usg = ET.Element('USG', {'COMMAND': 'SET_BANDWIDTH_UP'})
        usg.set('SUBSCRIBER', mac_address)
        bwu = ET.SubElement(usg, 'BANDWIDTH_UP')
        bwu.text = str(bandwidth_up)

        xml_cmd = ET.tostring(usg, encoding='UTF-8')
        logger.debug('[controller nomadix] bandwidth_up:', self.command_url, xml_cmd.decode())

        return self.session.post(self.command_url, data=xml_cmd, timeout=3)

    @parse_xml_return
    def bandwidth_down(self, mac_address, bandwidth_down):
        '''
            BANDWIDTH is measured in kbps
        '''

        usg = ET.Element('USG', {'COMMAND': 'SET_BANDWIDTH_DOWN'})
        usg.set('SUBSCRIBER', mac_address)
        bwd = ET.SubElement(usg, 'BANDWIDTH_DOWN')
        bwd.text = str(bandwidth_down)

        xml_cmd = ET.tostring(usg, encoding='UTF-8')
        logger.debug('[controller nomadix] bandwidth_down:', self.command_url, xml_cmd.decode())

        return self.session.post(self.command_url, data=xml_cmd, timeout=3)

    @parse_xml_return
    def max_bandwidth_down(self, mac_address, bandwidth_max_down):
        '''
            BANDWIDTH is measured in kbps
        '''

        usg = ET.Element('USG', {'COMMAND': 'SET_BANDWIDTH_MAX_DOWN'})
        usg.set('SUBSCRIBER', mac_address)
        bwmd = ET.SubElement(usg, 'BANDWIDTH_MAX_DOWN')
        bwmd.text = str(bandwidth_max_down)

        xml_cmd = ET.tostring(usg, encoding='UTF-8')
        logger.debug('[controller nomadix] max_bandwidth_down:', self.command_url, xml_cmd.decode())

        return self.session.post(self.command_url, data=xml_cmd, timeout=3)

    @parse_xml_return
    def max_bandwidth_up(self, mac_address, bandwidth_max_up):
        '''
            BANDWIDTH is measured in kbps
        '''

        usg = ET.Element('USG', {'COMMAND': 'SET_BANDWIDTH_MAX_UP'})
        usg.set('SUBSCRIBER', mac_address)
        bwmu = ET.SubElement(usg, 'BANDWIDTH_MAX_UP')
        bwmu.text = str(bandwidth_max_up)

        xml_cmd = ET.tostring(usg, encoding='UTF-8')
        logger.debug('[controller nomadix] max_bandwidth_up:', self.command_url, xml_cmd.decode())

        return self.session.post(self.command_url, data=xml_cmd, timeout=3)

    @parse_xml_return
    def user_payment(self, *args, **kwargs):
        raise NotImplementedError('TODO')

    @parse_xml_return
    def user_delete(self, mac_address=None, user_name=None):
        '''
            Only one of mac_address and user_name should be present
            if both are given, user_name will be ignored

            TODO:
                - add validation
                - fix the logic
        '''
        usg = ET.Element('USG', {'COMMAND': 'USER_DELETE'})
        user = ET.SubElement(usg, 'USER')
        if mac_address:
            user.set('ID_TYPE', 'MAC_ADDR')
            user.text = mac_address
        elif user_name:
            user.set('ID_TYPE', 'USER_NAME')
            user.text = user_name
        else:
            raise Exception('Missing either "mac_address" or "user_name"')

        xml_cmd = ET.tostring(usg, encoding='UTF-8')
        logger.debug('[controller nomadix] user_delete:', self.command_url, xml_cmd.decode())

        return self.session.post(self.command_url, data=xml_cmd, timeout=3)

    @parse_xml_return
    def user_query(self, mac_address=None, user_name=None):
        '''
            Only one of mac_address and user_name should be present
            if both are given, user_name will be ignored

            TODO:
                - add validation
                - fix the logic
        '''
        usg = ET.Element('USG', {'COMMAND': 'USER_QUERY'})
        user = ET.SubElement(usg, 'USER')
        if mac_address:
            user.set('ID_TYPE', 'MAC_ADDR')
            user.text = mac_address
        elif user_name:
            user.set('ID_TYPE', 'USER_NAME')
            user.text = user_name
        else:
            raise Exception('Missing either "mac_address" or "user_name"')

        xml_cmd = ET.tostring(usg, encoding='UTF-8')
        logger.debug('[controller nomadix] user_query:', self.command_url, xml_cmd.decode())

        #try:
        return self.session.post(self.command_url, data=xml_cmd, timeout=3)
        #except Exception as e:
        #    logger.error('[PACKAGE][nomadix.user_query] command_url: %s data: %s error: %s' % (str(self.command_url), str(xml_cmd), str(e))


    @parse_xml_return
    def user_authorize(self, mac_address):
        '''
            response["RESULT"] == "OK" and response["children"]["STATUS"] == "VALID_USER"
        '''
        usg = ET.Element('USG', {'COMMAND': 'USER_AUTHORIZE'})
        usg.set('SUBSCRIBER', mac_address)

        xml_cmd = ET.tostring(usg, encoding='UTF-8')
        logger.debug('[controller nomadix] user_authorize:', self.command_url, xml_cmd.decode())
        #try:
        return self.session.post(self.command_url, data=xml_cmd, timeout=3)
        #except Exception as e:
        #    logger.error('[PACKAGE][nomadix.user_authorize] command_url: %s data: %s error: %s' % (str(self.command_url), str(xml_cmd), str(e))

    @parse_xml_return
    def user_purchase(self, *args, **kwargs):
        raise NotImplementedError('TODO')

    # Room Administration Commands
    #

    @parse_xml_return
    def room_set_access(self, *args, **kwargs):
        raise NotImplementedError('TODO')
    @parse_xml_return
    def room_query_access(self, *args, **kwargs):
        raise NotImplementedError('TODO')
