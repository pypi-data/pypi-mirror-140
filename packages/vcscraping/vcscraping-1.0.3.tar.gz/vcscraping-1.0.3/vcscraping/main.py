import itertools #line:2
import numpy as np #line:3
from copy import deepcopy #line:4
from requests_html import HTMLSession #line:7
import warnings #line:8
warnings .simplefilter ('ignore')#line:9
def get_html (O0O0OO0OOO0OOOOOO ):#line:12
    O0000OOO000000000 =HTMLSession ()#line:19
    OO0O0OO0OO00000OO =O0000OOO000000000 .get (O0O0OO0OOO0OOOOOO )#line:20
    OO0O0OO0OO00000OO .html .arender ()#line:21
    OO0OOOOOO00OO0O00 =OO0O0OO0OO00000OO .html .raw_html .replace (b'\t',b'')#line:23
    OO0OOOOOO00OO0O00 =OO0OOOOOO00OO0O00 .decode ('utf-8')#line:25
    return OO0OOOOOO00OO0O00 ,OO0O0OO0OO00000OO .status_code #line:27
def find_starts (OOOOO000OO0O00000 ,OOO00OO000000OOOO ):#line:30
    OOOO00OO0000O000O =[-1 ]#line:31
    while 1 :#line:32
        OOOOO0O0OO00O0OO0 =OOOOO000OO0O00000 .find (OOO00OO000000OOOO ,OOOO00OO0000O000O [-1 ]+1 )#line:33
        if OOOOO0O0OO00O0OO0 <0 :#line:34
            break #line:35
        OOOO00OO0000O000O .append (OOOOO0O0OO00O0OO0 )#line:36
    OOOO00OO0000O000O .pop (0 )#line:37
    return OOOO00OO0000O000O #line:38
def get_between (O00OOOO000000O00O ,O0OOO0OO0OOO0O00O ,O00OOO0OOO0O0O00O ,dropin =0 ,max_text_len =1000 ):#line:41
    OO000OOO0000O00O0 =O00OOOO000000O00O .find (O0OOO0OO0OOO0O00O ,dropin )#line:42
    if OO000OOO0000O00O0 <0 :#line:43
        return None ,-1 ,-1 #line:44
    O000O0OO00OO0OO00 =O00OOOO000000O00O [OO000OOO0000O00O0 +len (O0OOO0OO0OOO0O00O ):OO000OOO0000O00O0 +len (O0OOO0OO0OOO0O00O )+max_text_len +1 ]#line:45
    O0OO0O00OOO0000O0 =O000O0OO00OO0OO00 .find (O00OOO0OOO0O0O00O )#line:46
    if O0OO0O00OOO0000O0 <0 :#line:47
        return None ,-1 ,-1 #line:48
    O000O0OO00OO0OO00 =O000O0OO00OO0OO00 [:O0OO0O00OOO0000O0 ]#line:49
    return O000O0OO00OO0OO00 ,OO000OOO0000O00O0 +len (O0OOO0OO0OOO0O00O ),OO000OOO0000O00O0 +len (O0OOO0OO0OOO0O00O )+O0OO0O00OOO0000O0 #line:50
def get_between_all (O00O0O0O0OO0O00O0 ,O00000000O0000O00 ,OOOO0OOO000000OOO ,max_text_len =1000 ):#line:53
    OO00OOOO0O00000OO =[]#line:54
    OOOOOO00OOOOOO00O =[-1 ]#line:55
    O0000O00O0O0O0OOO =[-1 ]#line:56
    while 1 :#line:57
        OOOOO0O0O0000O000 ,OO0O00O0OO00OOO0O ,OO0O0000O00OO0000 =get_between (O00O0O0O0OO0O00O0 ,O00000000O0000O00 ,OOOO0OOO000000OOO ,dropin =OOOOOO00OOOOOO00O [-1 ]+1 ,max_text_len =max_text_len )#line:58
        if OOOOO0O0O0000O000 ==None :#line:59
            break #line:60
        OO00OOOO0O00000OO .append (OOOOO0O0O0000O000 )#line:61
        OOOOOO00OOOOOO00O .append (OO0O00O0OO00OOO0O )#line:62
        O0000O00O0O0O0OOO .append (OO0O0000O00OO0000 )#line:63
    OOOOOO00OOOOOO00O .pop (0 )#line:64
    O0000O00O0O0O0OOO .pop (0 )#line:65
    return OO00OOOO0O00000OO ,OOOOOO00OOOOOO00O ,O0000O00O0O0O0OOO #line:66
class vcscraping :#line:69
    def __init__ (O00000O0OO0O00O00 ,OOOO00O00OO000O00 ,url2 =None ):#line:70
        if url2 ==None :#line:71
            O00000O0OO0O00O00 .html ,O0O0O0OOO000000O0 =get_html (OOOO00O00OO000O00 )#line:72
            O00000O0OO0O00O00 .mode ='single'#line:73
            print ('mode = <single page>')#line:74
            if O0O0O0OOO000000O0 !=200 :#line:75
                print ('{} ERR'.format (O0O0O0OOO000000O0 ))#line:76
                O00000O0OO0O00O00 .html =None #line:77
        else :#line:79
            O00000O0OO0O00O00 .html ,O0O0O0OOO000000O0 =get_html (OOOO00O00OO000O00 )#line:80
            O00000O0OO0O00O00 .html2 ,OOOOOOOOO0000O0OO =get_html (url2 )#line:81
            O00000O0OO0O00O00 .mode ='multi'#line:82
            print ('mode = <multi page>')#line:83
            if O0O0O0OOO000000O0 !=200 :#line:84
                print ('{} ERR (url1)'.format (O0O0O0OOO000000O0 ))#line:85
                O00000O0OO0O00O00 .html =None #line:86
            if OOOOOOOOO0000O0OO !=200 :#line:87
                print ('{} ERR (url2)'.format (OOOOOOOOO0000O0OO ))#line:88
                O00000O0OO0O00O00 .html2 =None #line:89
    def __del__ (OOOOO0OO000O00O00 ):#line:91
        pass #line:92
    def get_between (OOOO00OOOOOO0OO00 ,O000O0OOO0O0000OO ,O0OO00000OO0O00OO ,dropin =0 ,max_text_len =1000 ):#line:95
        O0O000O0OO0OO0OO0 =OOOO00OOOOOO0OO00 .html .find (O000O0OOO0O0000OO ,dropin )#line:96
        if O0O000O0OO0OO0OO0 <0 :#line:97
            return None ,-1 ,-1 #line:98
        O0000O0O0000OOO00 =OOOO00OOOOOO0OO00 .html [O0O000O0OO0OO0OO0 +len (O000O0OOO0O0000OO ):O0O000O0OO0OO0OO0 +len (O000O0OOO0O0000OO )+max_text_len +1 ]#line:99
        OO0OO000000OO000O =O0000O0O0000OOO00 .find (O0OO00000OO0O00OO )#line:100
        if OO0OO000000OO000O <0 :#line:101
            return None ,-1 ,-1 #line:102
        O0000O0O0000OOO00 =O0000O0O0000OOO00 [:OO0OO000000OO000O ]#line:103
        return O0000O0O0000OOO00 ,O0O000O0OO0OO0OO0 +len (O000O0OOO0O0000OO ),O0O000O0OO0OO0OO0 +len (O000O0OOO0O0000OO )+OO0OO000000OO000O #line:104
    def get_between_all (O0O0O0O00OOOO0O00 ,OO0O000O0OOO0OO00 ,OOOO00OOO0O0OO000 ,max_text_len =1000 ):#line:107
        O0000OO000OO0O0O0 =[]#line:108
        O0OO0OOO0OO00O0OO =[-1 ]#line:109
        OO0O0OO00O0OOOO0O =[-1 ]#line:110
        while 1 :#line:111
            OO0OO00O000O000OO ,OOOO0000O0OOOOOO0 ,OO00O00OOOO0O000O =get_between (O0O0O0O00OOOO0O00 .html ,OO0O000O0OOO0OO00 ,OOOO00OOO0O0OO000 ,dropin =O0OO0OOO0OO00O0OO [-1 ]+1 ,max_text_len =max_text_len )#line:112
            if OO0OO00O000O000OO ==None :#line:113
                break #line:114
            O0000OO000OO0O0O0 .append (OO0OO00O000O000OO )#line:115
            O0OO0OOO0OO00O0OO .append (OOOO0000O0OOOOOO0 )#line:116
            OO0O0OO00O0OOOO0O .append (OO00O00OOOO0O000O )#line:117
        O0OO0OOO0OO00O0OO .pop (0 )#line:118
        OO0O0OO00O0OOOO0O .pop (0 )#line:119
        print ('found = {}'.format (len (O0000OO000OO0O0O0 )))#line:120
        return O0000OO000OO0O0O0 ,O0OO0OOO0OO00O0OO ,OO0O0OO00O0OOOO0O #line:121
    def find_presuf (OO0O0O0OOOO00OOO0 ,OOOOO0000OO0000OO ,OOOO00O0O0O00OO0O ,max_text_len =None ,min_text_num =2 ,max_text_num =1000 ,max_presuf_len =40 ):#line:123
        if OO0O0O0OOOO00OOO0 .mode =='single':#line:124
            if max_text_len ==None :#line:127
                max_text_len =int (max (len (OOOOO0000OO0000OO ),len (OOOO00O0O0O00OO0O ))*2 )#line:128
            OO0OOO0O0000000OO =find_starts (OO0O0O0OOOO00OOO0 .html ,OOOOO0000OO0000OO )#line:131
            OO0O0000OO00O00OO =np .zeros ((max_presuf_len *max_presuf_len ,3 ),int )#line:134
            OO0O0000OO00O00OO [:,:2 ]=np .array (list (itertools .product (range (1 ,max_presuf_len +1 ),range (1 ,max_presuf_len +1 ))))#line:135
            OO0O0000OO00O00OO [:,2 ]=np .sum (OO0O0000OO00O00OO [:,:2 ],axis =1 )#line:136
            OO0O0000OO00O00OO =OO0O0000OO00O00OO [np .argsort (OO0O0000OO00O00OO [:,2 ])]#line:137
            print ('-------------- setting --------------')#line:140
            print ('@ single'.format ())#line:141
            print ('max_text_len = {}'.format (max_text_len ))#line:142
            print ('min_text_num = {}'.format (min_text_num ))#line:143
            print ('max_text_num = {}'.format (max_text_num ))#line:144
            print ('max_presuf_len = {}'.format (max_presuf_len ))#line:145
            print ('--------------- start ---------------')#line:146
            OO000OO0O0O0O0O00 =len (OO0O0000OO00O00OO )//25 #line:149
            OO0000000000OOO0O =False #line:152
            for O00OOO00O00OO0O00 ,O0OO0O0000000OO0O in enumerate (OO0OOO0O0000000OO ):#line:153
                print ('try {}/{} |'.format (O00OOO00O00OO0O00 +1 ,len (OO0OOO0O0000000OO )),end ='')#line:155
                for OO0O0OOOO00000000 ,(O00OOO00O00OO0O00 ,OOO0OOOO00O000O00 )in enumerate (OO0O0000OO00O00OO [:,:2 ]):#line:157
                    if OO0O0OOOO00000000 %OO000OO0O0O0O0O00 ==0 :#line:158
                        print ('{}'.format ('>'),end ='')#line:159
                    O000OOOOOOO0O0O00 =OO0O0O0OOOO00OOO0 .html [O0OO0O0000000OO0O -O00OOO00O00OO0O00 :O0OO0O0000000OO0O ]#line:162
                    O0O00OOO00O0O0O00 =OO0O0O0OOOO00OOO0 .html [O0OO0O0000000OO0O +len (OOOOO0000OO0000OO ):O0OO0O0000000OO0O +len (OOOOO0000OO0000OO )+OOO0OOOO00O000O00 ]#line:163
                    OOOO0OO00OO000000 ,O0OOOOOOOO000O0O0 ,OOOOOO0OO0O0O0000 =get_between_all (OO0O0O0OOOO00OOO0 .html ,O000OOOOOOO0O0O00 ,O0O00OOO00O0O0O00 ,max_text_len =max_text_len )#line:164
                    if len (OOOO0OO00OO000000 )<2 :#line:166
                        continue #line:167
                    if OOOO0OO00OO000000 [0 ]==OOOOO0000OO0000OO and OOOO0OO00OO000000 [1 ]==OOOO00O0O0O00OO0O and len (OOOO0OO00OO000000 )>=min_text_num and len (OOOO0OO00OO000000 )<=max_text_num :#line:170
                        O0O0O0OO0O0OO000O =deepcopy (O000OOOOOOO0O0O00 )#line:171
                        OOO000O0O0000O0OO =deepcopy (O0O00OOO00O0O0O00 )#line:172
                        OO0000000000OOO0O =True #line:176
                        break #line:177
                print ()#line:178
                if OO0000000000OOO0O :#line:179
                    break #line:180
            print ('---------------- end ----------------')#line:182
            if OO0000000000OOO0O ==False :#line:184
                print ('not found'.format ())#line:185
                print ('-------------------------------------')#line:186
                return None ,None #line:188
            print ('found = {}'.format (len (OOOO0OO00OO000000 )))#line:191
            print ('prefix = {}'.format (repr (O0O0O0OO0O0OO000O )))#line:192
            print ('suffix = {}'.format (repr (OOO000O0O0000O0OO )))#line:193
            print ('-------------------------------------')#line:194
            return O0O0O0OO0O0OO000O ,OOO000O0O0000O0OO #line:196
        if OO0O0O0OOOO00OOO0 .mode =='multi':#line:199
            if max_text_len ==None :#line:202
                max_text_len =int (max (len (OOOOO0000OO0000OO ),len (OOOO00O0O0O00OO0O ))*2 )#line:203
            OO0OOO0O0000000OO =find_starts (OO0O0O0OOOO00OOO0 .html ,OOOOO0000OO0000OO )#line:206
            OO0O0000OO00O00OO =np .zeros ((max_presuf_len *max_presuf_len ,3 ),int )#line:209
            OO0O0000OO00O00OO [:,:2 ]=np .array (list (itertools .product (range (1 ,max_presuf_len +1 ),range (1 ,max_presuf_len +1 ))))#line:210
            OO0O0000OO00O00OO [:,2 ]=np .sum (OO0O0000OO00O00OO [:,:2 ],axis =1 )#line:211
            OO0O0000OO00O00OO =OO0O0000OO00O00OO [np .argsort (OO0O0000OO00O00OO [:,2 ])]#line:212
            print ('-------------- setting --------------')#line:215
            print ('@ multi'.format ())#line:216
            print ('max_text_len = {}'.format (max_text_len ))#line:217
            print ('max_presuf_len = {}'.format (max_presuf_len ))#line:218
            print ('--------------- start ---------------')#line:219
            OO000OO0O0O0O0O00 =len (OO0O0000OO00O00OO )//25 #line:222
            OO0000000000OOO0O =False #line:225
            for O00OOO00O00OO0O00 ,O0OO0O0000000OO0O in enumerate (OO0OOO0O0000000OO ):#line:226
                print ('try {}/{} |'.format (O00OOO00O00OO0O00 +1 ,len (OO0OOO0O0000000OO )),end ='')#line:228
                for OO0O0OOOO00000000 ,(O00OOO00O00OO0O00 ,OOO0OOOO00O000O00 )in enumerate (OO0O0000OO00O00OO [:,:2 ]):#line:230
                    if OO0O0OOOO00000000 %OO000OO0O0O0O0O00 ==0 :#line:231
                        print ('{}'.format ('>'),end ='')#line:232
                    O000OOOOOOO0O0O00 =OO0O0O0OOOO00OOO0 .html [O0OO0O0000000OO0O -O00OOO00O00OO0O00 :O0OO0O0000000OO0O ]#line:235
                    O0O00OOO00O0O0O00 =OO0O0O0OOOO00OOO0 .html [O0OO0O0000000OO0O +len (OOOOO0000OO0000OO ):O0OO0O0000000OO0O +len (OOOOO0000OO0000OO )+OOO0OOOO00O000O00 ]#line:236
                    OO0O00O0OO0O00000 ,OO000OO0O0OO000O0 ,OOO000O0OOO000O00 =get_between (OO0O0O0OOOO00OOO0 .html ,O000OOOOOOO0O0O00 ,O0O00OOO00O0O0O00 ,max_text_len =max_text_len )#line:237
                    O0O00O00O000O0OOO ,O00O0O000OO0OOOOO ,OOOOO0O0OOO000OOO =get_between (OO0O0O0OOOO00OOO0 .html2 ,O000OOOOOOO0O0O00 ,O0O00OOO00O0O0O00 ,max_text_len =max_text_len )#line:238
                    if OO0O00O0OO0O00000 ==None or O0O00O00O000O0OOO ==None :#line:240
                        continue #line:241
                    if OO0O00O0OO0O00000 ==OOOOO0000OO0000OO and O0O00O00O000O0OOO ==OOOO00O0O0O00OO0O :#line:244
                        O0O0O0OO0O0OO000O =deepcopy (O000OOOOOOO0O0O00 )#line:245
                        OOO000O0O0000O0OO =deepcopy (O0O00OOO00O0O0O00 )#line:246
                        OO0000000000OOO0O =True #line:247
                        break #line:248
                print ()#line:249
                if OO0000000000OOO0O :#line:250
                    break #line:251
            print ('---------------- end ----------------')#line:253
            if OO0000000000OOO0O ==False :#line:255
                print ('not found'.format ())#line:256
                print ('-------------------------------------')#line:257
                return None ,None #line:258
            print ('pre = {}'.format (repr (O0O0O0OO0O0OO000O )))#line:261
            print ('suf = {}'.format (repr (OOO000O0O0000O0OO )))#line:262
            print ('-------------------------------------')#line:263
            return O0O0O0OO0O0OO000O ,OOO000O0O0000O0OO #line:264
if __name__ =='__main__':#line:269
    url ='https://www.embopress.org/action/doSearch?AllField=circuit+AND+%28stability+OR+oscillation%29' '&sortBy=Earliest&startPage=0&SeriesKey=17444292' '&pageSize=500'#line:332
    myscraping =vcscraping (url ,url )#line:333
    pre ,suf =myscraping .find_presuf ('aaa','bbb')#line:334
