#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author: Cifer Z.
date: 6/15/20
"""

import base64
import copy

if __name__ == "__main__":
    # auth_token = "ya29.a0AfH6SMCOXtlXkPZ2sxkCad3B9FwZN8_lVNYrdxPuZDOoETssjHQ8S_Fh6Vg7KQNwIcPOLutccqnrIRf15tboHbsSHUFj0wOQMa2_3f5LY2srSuS_JhxYotdJftXin7_8iPkQGLNysnKPISslPp-eAyiSDrQRYsbb79g"
    # xoauth2 = "user=qiuchenzhang94@gmail.com\1auth=Bearer " + auth_token + "\1\1"


    # auth_token = "TEkr4n6eswCMMnnNdt7uxD7CXzPOg2sWYHuPuPBuWS3kUwggpM__sNKAyWS3SuTivDbuMNKO6HL6p2hBl22_IZcpKorOMVNU1CgCL55129bOZVHHjNmQqmmb8TBantg3FFhxXRfvN8JHcCzEfsBLwhQ57TqeaSJu6vwLOzy0HIwf_0HMbH1bDdi6C41yssG8Me7TFFROE0YDtSuOXu6.Gn2ShovwbZVRsbVNRgeARVPE5VIpyUqAiTsJADPr_8OWZFGcXubH3o0qJXvTE4W5NMRw60KTNa_0gu2UH0V2ZOohes1z1M0uVT63KR5CXEXzo1fcBKZITUFHt_TQK6AmHNw01B0BU670wwBxawz9gPDES5KBunHIVNpLPKimjlHA32Lm7mXcMBAwEIsGwkPGdIZ5LA42qOJddhpYo7brZISrPCJJthN0JUktYw994ZinDJPxV30JSOFeGfgLiLdPM0g5IW2zK490oZ0KvTs3xEL0rzID4xMdQEVz7Q3ibYkPzF.n6nrKkgEN9k7EpuqfWeiBIZ3OXTh9ASDSPOq8zrVMsufugH.bBUS1GYgr3jqytGr8AzDHgBU6pskezZHUguVzcm1QPtukk453_jEQ67KNbFo8TM1gf6Ce2UBs7CEdZ2NJfg0.xYlj.FcqpoqnM.Wsrx3pYmqjjE40tSbQVRR4gQZVOHXc4QyImfIESzxFZnDVqZXLcNbdoPBpU7GMIrfu0tpakZpD.LgmBHW_.J.c4jS8aD8CHiA1J8dYEKoUctY7rM0tIvP3rimM7pKhTEPUCPoJTbjGtIuP7RN0DE9vlPNNsGNSyq9ITcIXo1zfI0acsNQxv8gW1zctJIUALgNdAXI24181zqD7s.C.lmEpRs9Zl6RQ0RAEPv1ua3692eX8M6q2WcVoc_tyfUTsMWI1DFOJLhsuR0A6srWi5WXmCeTFxfVu56daNY9wQEII7F1565GdMmZbPxLX0veAjHs7RNOj_lYed2kDvy0ft1H48Gu0jzJlc3UP7Xchf0oULJhdrGUF9kWZvaO.B.JPzR6.ZBr5ZVnFEEL6BLt_8UB7L2LYFkueekzeYWOgc4d4Uhd6TlkFPThFNnQpleIW6ntPmfk-"
    # xoauth2 = "user=qiuchenz@yahoo.com\1auth=Bearer " + auth_token + "\1\1"
    #
    # print('echo "auth xoauth2 ' + base64.b64encode(xoauth2.encode()).decode() + '" | openssl s_client -connect smtp.mail.yahoo.com:465 -crlf -ign_eof')

    # client_secret = "14451a2db2060fe7779ec99d181f41f9bba311ee"
    # auth_code = client_id + ":" + client_secret
    # print(base64.b64encode((auth_code.encode("ascii"))))
    arr1 = [[1,2,3],[4,5,6]]
    arr1_backup = copy.deepcopy(arr1)
    arr1[0][0] = 2
    arr1.append([7,8])
    print(arr1_backup)



