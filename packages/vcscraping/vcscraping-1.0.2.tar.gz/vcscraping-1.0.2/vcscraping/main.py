import itertools #line:2
import numpy as np #line:3
from copy import deepcopy #line:4
from requests_html import HTMLSession #line:7
import warnings #line:8
warnings .simplefilter ('ignore')#line:9
def get_html (OO000000O0O000000 ):#line:12
    O000O000O0O0O000O =HTMLSession ()#line:19
    OOOO000O00OOOO0O0 =O000O000O0O0O000O .get (OO000000O0O000000 )#line:20
    OOOO000O00OOOO0O0 .html .arender ()#line:21
    OOOOOOOOOO0000000 =OOOO000O00OOOO0O0 .html .raw_html .replace (b'\t',b'')#line:23
    OOOOOOOOOO0000000 =OOOOOOOOOO0000000 .decode ('utf-8')#line:25
    return OOOOOOOOOO0000000 #line:27
def find_starts (O0O0OO0OO0O0O0O0O ,O0OOOOOOOOOOO0000 ):#line:30
    O0O00000OO0O0O0O0 =[-1 ]#line:31
    while 1 :#line:32
        O0O00O0O000000O00 =O0O0OO0OO0O0O0O0O .find (O0OOOOOOOOOOO0000 ,O0O00000OO0O0O0O0 [-1 ]+1 )#line:33
        if O0O00O0O000000O00 <0 :#line:34
            break #line:35
        O0O00000OO0O0O0O0 .append (O0O00O0O000000O00 )#line:36
    O0O00000OO0O0O0O0 .pop (0 )#line:37
    return O0O00000OO0O0O0O0 #line:38
def get_between (O000OO000OOOOOO0O ,O0OO000O00O00O0OO ,O0OOO0OOOO0OOO00O ,dropin =0 ,max_text_len =1000 ):#line:41
    O0OOO00O0OOO0OOOO =O000OO000OOOOOO0O .find (O0OO000O00O00O0OO ,dropin )#line:42
    if O0OOO00O0OOO0OOOO <0 :#line:43
        return None ,-1 ,-1 #line:44
    OOO0O0000O000OOO0 =O000OO000OOOOOO0O [O0OOO00O0OOO0OOOO +len (O0OO000O00O00O0OO ):O0OOO00O0OOO0OOOO +len (O0OO000O00O00O0OO )+max_text_len +1 ]#line:45
    OOOO0O000OO0O000O =OOO0O0000O000OOO0 .find (O0OOO0OOOO0OOO00O )#line:46
    if OOOO0O000OO0O000O <0 :#line:47
        return None ,-1 ,-1 #line:48
    OOO0O0000O000OOO0 =OOO0O0000O000OOO0 [:OOOO0O000OO0O000O ]#line:49
    return OOO0O0000O000OOO0 ,O0OOO00O0OOO0OOOO +len (O0OO000O00O00O0OO ),O0OOO00O0OOO0OOOO +len (O0OO000O00O00O0OO )+OOOO0O000OO0O000O #line:50
def get_between_all (O0OOO000OO0O0O0OO ,O0000000O0O00O00O ,O000O00OOOO0OO00O ,max_text_len =1000 ):#line:53
    O000O0OOOOOO0OO00 =[]#line:54
    OO0OO000000OO00OO =[-1 ]#line:55
    OO0O00OOO0O000OO0 =[-1 ]#line:56
    while 1 :#line:57
        O0O00O0O0O000O0OO ,OOO0OO0OOO0OO0O00 ,O0O0OOO0O000OOOOO =get_between (O0OOO000OO0O0O0OO ,O0000000O0O00O00O ,O000O00OOOO0OO00O ,dropin =OO0OO000000OO00OO [-1 ]+1 ,max_text_len =max_text_len )#line:58
        if O0O00O0O0O000O0OO ==None :#line:59
            break #line:60
        O000O0OOOOOO0OO00 .append (O0O00O0O0O000O0OO )#line:61
        OO0OO000000OO00OO .append (OOO0OO0OOO0OO0O00 )#line:62
        OO0O00OOO0O000OO0 .append (O0O0OOO0O000OOOOO )#line:63
    OO0OO000000OO00OO .pop (0 )#line:64
    OO0O00OOO0O000OO0 .pop (0 )#line:65
    return O000O0OOOOOO0OO00 ,OO0OO000000OO00OO ,OO0O00OOO0O000OO0 #line:66
class vcscraping :#line:69
    def __init__ (O0OO00O0O0OO0OOOO ,O0O0OOOOOO0000O0O ,url2 =None ):#line:70
        if url2 ==None :#line:71
            O0OO00O0O0OO0OOOO .html =get_html (O0O0OOOOOO0000O0O )#line:72
            O0OO00O0O0OO0OOOO .mode ='single'#line:73
            print ('mode = <single page>')#line:74
        else :#line:75
            O0OO00O0O0OO0OOOO .html =get_html (O0O0OOOOOO0000O0O )#line:76
            O0OO00O0O0OO0OOOO .html2 =get_html (url2 )#line:77
            O0OO00O0O0OO0OOOO .mode ='multi'#line:78
            print ('mode = <multi page>')#line:79
    def __del__ (OO0O00OO0OO0OO0OO ):#line:81
        pass #line:82
    def get_between (O0O0OOO000000000O ,OOOO000O0OO000O00 ,OOOOO0000000000OO ,dropin =0 ,max_text_len =1000 ):#line:85
        OO0O000000OOOOO00 =O0O0OOO000000000O .html .find (OOOO000O0OO000O00 ,dropin )#line:86
        if OO0O000000OOOOO00 <0 :#line:87
            return None ,-1 ,-1 #line:88
        OO0O0OO0O00O00OOO =O0O0OOO000000000O .html [OO0O000000OOOOO00 +len (OOOO000O0OO000O00 ):OO0O000000OOOOO00 +len (OOOO000O0OO000O00 )+max_text_len +1 ]#line:89
        O0OO0000OOO00OOOO =OO0O0OO0O00O00OOO .find (OOOOO0000000000OO )#line:90
        if O0OO0000OOO00OOOO <0 :#line:91
            return None ,-1 ,-1 #line:92
        OO0O0OO0O00O00OOO =OO0O0OO0O00O00OOO [:O0OO0000OOO00OOOO ]#line:93
        return OO0O0OO0O00O00OOO ,OO0O000000OOOOO00 +len (OOOO000O0OO000O00 ),OO0O000000OOOOO00 +len (OOOO000O0OO000O00 )+O0OO0000OOO00OOOO #line:94
    def get_between_all (OOO0O0OOO0OOO00OO ,O000O0000OOOO00OO ,O0O00O0OO0000000O ,max_text_len =1000 ):#line:97
        O0OOO0OO00O0O0O0O =[]#line:98
        O0000OOO0OOOOO00O =[-1 ]#line:99
        O0O00O000OOOOOO0O =[-1 ]#line:100
        while 1 :#line:101
            O0O00000OOOOO0OO0 ,OO0O00O00O0O0OOO0 ,OOOO0000OO0000O0O =get_between (OOO0O0OOO0OOO00OO .html ,O000O0000OOOO00OO ,O0O00O0OO0000000O ,dropin =O0000OOO0OOOOO00O [-1 ]+1 ,max_text_len =max_text_len )#line:102
            if O0O00000OOOOO0OO0 ==None :#line:103
                break #line:104
            O0OOO0OO00O0O0O0O .append (O0O00000OOOOO0OO0 )#line:105
            O0000OOO0OOOOO00O .append (OO0O00O00O0O0OOO0 )#line:106
            O0O00O000OOOOOO0O .append (OOOO0000OO0000O0O )#line:107
        O0000OOO0OOOOO00O .pop (0 )#line:108
        O0O00O000OOOOOO0O .pop (0 )#line:109
        print ('found = {}'.format (len (O0OOO0OO00O0O0O0O )))#line:110
        return O0OOO0OO00O0O0O0O ,O0000OOO0OOOOO00O ,O0O00O000OOOOOO0O #line:111
    def find_presuf (OOO000O00O00OO00O ,OO0O0OOO00OOOO0O0 ,O0000O0OOOOOO00OO ,max_text_len =None ,min_text_num =2 ,max_text_num =1000 ,max_presuf_len =40 ):#line:113
        if OOO000O00O00OO00O .mode =='single':#line:114
            if max_text_len ==None :#line:117
                max_text_len =int (max (len (OO0O0OOO00OOOO0O0 ),len (O0000O0OOOOOO00OO ))*2 )#line:118
            O0O0O00O00O0OO0OO =find_starts (OOO000O00O00OO00O .html ,OO0O0OOO00OOOO0O0 )#line:121
            OO0O0OOOO0O0O00O0 =np .zeros ((max_presuf_len *max_presuf_len ,3 ),int )#line:124
            OO0O0OOOO0O0O00O0 [:,:2 ]=np .array (list (itertools .product (range (1 ,max_presuf_len +1 ),range (1 ,max_presuf_len +1 ))))#line:125
            OO0O0OOOO0O0O00O0 [:,2 ]=np .sum (OO0O0OOOO0O0O00O0 [:,:2 ],axis =1 )#line:126
            OO0O0OOOO0O0O00O0 =OO0O0OOOO0O0O00O0 [np .argsort (OO0O0OOOO0O0O00O0 [:,2 ])]#line:127
            print ('-------------- setting --------------')#line:130
            print ('@ single'.format ())#line:131
            print ('max_text_len = {}'.format (max_text_len ))#line:132
            print ('min_text_num = {}'.format (min_text_num ))#line:133
            print ('max_text_num = {}'.format (max_text_num ))#line:134
            print ('max_presuf_len = {}'.format (max_presuf_len ))#line:135
            print ('--------------- start ---------------')#line:136
            OOOOOO00OO00OOO00 =len (OO0O0OOOO0O0O00O0 )//25 #line:139
            OO000OO00O0O00O00 =False #line:142
            for OO00O00O0O0000O00 ,OO0O0000O0O0OOO00 in enumerate (O0O0O00O00O0OO0OO ):#line:143
                print ('try {}/{} |'.format (OO00O00O0O0000O00 +1 ,len (O0O0O00O00O0OO0OO )),end ='')#line:145
                for O0O0O0OO00OOO0OOO ,(OO00O00O0O0000O00 ,O0OO0OOOO00O000OO )in enumerate (OO0O0OOOO0O0O00O0 [:,:2 ]):#line:147
                    if O0O0O0OO00OOO0OOO %OOOOOO00OO00OOO00 ==0 :#line:148
                        print ('{}'.format ('>'),end ='')#line:149
                    OO0OOO00O0OO00OO0 =OOO000O00O00OO00O .html [OO0O0000O0O0OOO00 -OO00O00O0O0000O00 :OO0O0000O0O0OOO00 ]#line:152
                    OOOO0O0O000000OO0 =OOO000O00O00OO00O .html [OO0O0000O0O0OOO00 +len (OO0O0OOO00OOOO0O0 ):OO0O0000O0O0OOO00 +len (OO0O0OOO00OOOO0O0 )+O0OO0OOOO00O000OO ]#line:153
                    O0OOOO00OO00O000O ,OO0OOO00O0OO0OO0O ,OOO00OOO00OOOO0OO =get_between_all (OOO000O00O00OO00O .html ,OO0OOO00O0OO00OO0 ,OOOO0O0O000000OO0 ,max_text_len =max_text_len )#line:154
                    if len (O0OOOO00OO00O000O )<2 :#line:156
                        continue #line:157
                    if O0OOOO00OO00O000O [0 ]==OO0O0OOO00OOOO0O0 and O0OOOO00OO00O000O [1 ]==O0000O0OOOOOO00OO and len (O0OOOO00OO00O000O )>=min_text_num and len (O0OOOO00OO00O000O )<=max_text_num :#line:160
                        O0O00O000O00O00OO =deepcopy (OO0OOO00O0OO00OO0 )#line:161
                        O00000O00O0OO0O00 =deepcopy (OOOO0O0O000000OO0 )#line:162
                        OO000OO00O0O00O00 =True #line:166
                        break #line:167
                print ()#line:168
                if OO000OO00O0O00O00 :#line:169
                    break #line:170
            print ('---------------- end ----------------')#line:172
            if OO000OO00O0O00O00 ==False :#line:174
                print ('not found'.format ())#line:175
                print ('-------------------------------------')#line:176
                return None ,None #line:178
            print ('found = {}'.format (len (O0OOOO00OO00O000O )))#line:181
            print ('prefix = {}'.format (repr (O0O00O000O00O00OO )))#line:182
            print ('suffix = {}'.format (repr (O00000O00O0OO0O00 )))#line:183
            print ('-------------------------------------')#line:184
            return O0O00O000O00O00OO ,O00000O00O0OO0O00 #line:186
        if OOO000O00O00OO00O .mode =='multi':#line:189
            if max_text_len ==None :#line:192
                max_text_len =int (max (len (OO0O0OOO00OOOO0O0 ),len (O0000O0OOOOOO00OO ))*2 )#line:193
            O0O0O00O00O0OO0OO =find_starts (OOO000O00O00OO00O .html ,OO0O0OOO00OOOO0O0 )#line:196
            OO0O0OOOO0O0O00O0 =np .zeros ((max_presuf_len *max_presuf_len ,3 ),int )#line:199
            OO0O0OOOO0O0O00O0 [:,:2 ]=np .array (list (itertools .product (range (1 ,max_presuf_len +1 ),range (1 ,max_presuf_len +1 ))))#line:200
            OO0O0OOOO0O0O00O0 [:,2 ]=np .sum (OO0O0OOOO0O0O00O0 [:,:2 ],axis =1 )#line:201
            OO0O0OOOO0O0O00O0 =OO0O0OOOO0O0O00O0 [np .argsort (OO0O0OOOO0O0O00O0 [:,2 ])]#line:202
            print ('-------------- setting --------------')#line:205
            print ('@ multi'.format ())#line:206
            print ('max_text_len = {}'.format (max_text_len ))#line:207
            print ('max_presuf_len = {}'.format (max_presuf_len ))#line:208
            print ('--------------- start ---------------')#line:209
            OOOOOO00OO00OOO00 =len (OO0O0OOOO0O0O00O0 )//25 #line:212
            OO000OO00O0O00O00 =False #line:215
            for OO00O00O0O0000O00 ,OO0O0000O0O0OOO00 in enumerate (O0O0O00O00O0OO0OO ):#line:216
                print ('try {}/{} |'.format (OO00O00O0O0000O00 +1 ,len (O0O0O00O00O0OO0OO )),end ='')#line:218
                for O0O0O0OO00OOO0OOO ,(OO00O00O0O0000O00 ,O0OO0OOOO00O000OO )in enumerate (OO0O0OOOO0O0O00O0 [:,:2 ]):#line:220
                    if O0O0O0OO00OOO0OOO %OOOOOO00OO00OOO00 ==0 :#line:221
                        print ('{}'.format ('>'),end ='')#line:222
                    OO0OOO00O0OO00OO0 =OOO000O00O00OO00O .html [OO0O0000O0O0OOO00 -OO00O00O0O0000O00 :OO0O0000O0O0OOO00 ]#line:225
                    OOOO0O0O000000OO0 =OOO000O00O00OO00O .html [OO0O0000O0O0OOO00 +len (OO0O0OOO00OOOO0O0 ):OO0O0000O0O0OOO00 +len (OO0O0OOO00OOOO0O0 )+O0OO0OOOO00O000OO ]#line:226
                    O0OOOO0000OOOOOO0 ,OOOO0000OOOOO000O ,O0000OO0000O00OO0 =get_between (OOO000O00O00OO00O .html ,OO0OOO00O0OO00OO0 ,OOOO0O0O000000OO0 ,max_text_len =max_text_len )#line:227
                    O000OO0O0OO00OOO0 ,OO00O0OO00OOOOO00 ,O000OO000OO0000OO =get_between (OOO000O00O00OO00O .html2 ,OO0OOO00O0OO00OO0 ,OOOO0O0O000000OO0 ,max_text_len =max_text_len )#line:228
                    if O0OOOO0000OOOOOO0 ==None or O000OO0O0OO00OOO0 ==None :#line:230
                        continue #line:231
                    if O0OOOO0000OOOOOO0 ==OO0O0OOO00OOOO0O0 and O000OO0O0OO00OOO0 ==O0000O0OOOOOO00OO :#line:234
                        O0O00O000O00O00OO =deepcopy (OO0OOO00O0OO00OO0 )#line:235
                        O00000O00O0OO0O00 =deepcopy (OOOO0O0O000000OO0 )#line:236
                        OO000OO00O0O00O00 =True #line:237
                        break #line:238
                print ()#line:239
                if OO000OO00O0O00O00 :#line:240
                    break #line:241
            print ('---------------- end ----------------')#line:243
            if OO000OO00O0O00O00 ==False :#line:245
                print ('not found'.format ())#line:246
                print ('-------------------------------------')#line:247
                return None ,None #line:248
            print ('prefix = {}'.format (repr (O0O00O000O00O00OO )))#line:251
            print ('suffix = {}'.format (repr (O00000O00O0OO0O00 )))#line:252
            print ('-------------------------------------')#line:253
            return O0O00O000O00O00OO ,O00000O00O0OO0O00 #line:254
if __name__ =='__main__':#line:259
    url ='https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E4%B8%80%E8%A6%A7'#line:261
    query1 ='001'#line:262
    query2 ='002'#line:263
    myscraping =vcscraping (url )#line:265
    pre ,suf =myscraping .find_presuf (query1 ,query2 ,max_text_len =3 ,min_text_num =10 )#line:266
    texts ,starts ,ends =myscraping .get_between_all (pre ,suf )#line:267
    print (texts [:5 ])#line:268
    print (myscraping .html [starts [0 ]:ends [0 ]])#line:269
