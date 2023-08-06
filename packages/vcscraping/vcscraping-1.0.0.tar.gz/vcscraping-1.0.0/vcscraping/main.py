import itertools #line:2
import numpy as np #line:3
from copy import deepcopy #line:4
from requests_html import HTMLSession #line:7
import warnings #line:8
warnings .simplefilter ('ignore')#line:9
def get_html (OO000OOO00O0OO000 ):#line:12
    OO00O0O00OOO00O0O =HTMLSession ()#line:19
    O000O0000OO0OO0OO =OO00O0O00OOO00O0O .get (OO000OOO00O0OO000 )#line:20
    O000O0000OO0OO0OO .html .arender ()#line:21
    OO00OO0OO0O000000 =O000O0000OO0OO0OO .html .raw_html .replace (b'\t',b'')#line:23
    OO00OO0OO0O000000 =OO00OO0OO0O000000 .decode ('utf-8')#line:25
    return OO00OO0OO0O000000 #line:27
def find_starts (O000O0O0OO00OO000 ,OOOOOOO00000O00O0 ):#line:30
    O000O0OO000O0O0OO =[-1 ]#line:31
    while 1 :#line:32
        OOOO0O00OOO00O00O =O000O0O0OO00OO000 .find (OOOOOOO00000O00O0 ,O000O0OO000O0O0OO [-1 ]+1 )#line:33
        if OOOO0O00OOO00O00O <0 :#line:34
            break #line:35
        O000O0OO000O0O0OO .append (OOOO0O00OOO00O00O )#line:36
    O000O0OO000O0O0OO .pop (0 )#line:37
    return O000O0OO000O0O0OO #line:38
def find_text (OO0O00O00OO0O0O00 ,OO000OO0OO0O00OOO ,OO0OOO000OOOOO00O ,dropin =0 ,max_text_len =1000 ):#line:41
    O0OOOO00OO00OO0OO =OO0O00O00OO0O0O00 .find (OO000OO0OO0O00OOO ,dropin )#line:42
    if O0OOOO00OO00OO0OO <0 :#line:43
        return None ,None #line:44
    OO00O00OOO0OO00OO =OO0O00O00OO0O0O00 [O0OOOO00OO00OO0OO +len (OO000OO0OO0O00OOO ):O0OOOO00OO00OO0OO +len (OO000OO0OO0O00OOO )+max_text_len ]#line:45
    OO0OO000O0OO0O0O0 =OO00O00OOO0OO00OO .find (OO0OOO000OOOOO00O )#line:46
    if OO0OO000O0OO0O0O0 <0 :#line:47
        return None ,None #line:48
    OO00O00OOO0OO00OO =OO00O00OOO0OO00OO [:OO0OO000O0OO0O0O0 ]#line:49
    return OO00O00OOO0OO00OO ,O0OOOO00OO00OO0OO #line:50
def find_texts (O00OOO0OO0OO0000O ,O0O0OOOO000O0OOOO ,OOOOO0O000O000O00 ,max_text_len =1000 ):#line:53
    O000O00OO00O0000O =[]#line:54
    O000O0O0O000O0O00 =[-1 ]#line:55
    O000O00O0OO000O0O =[-1 ]#line:56
    while 1 :#line:57
        O00O0O00O0O00OOO0 ,O000O000O0O0000O0 =find_text (O00OOO0OO0OO0000O ,O0O0OOOO000O0OOOO ,OOOOO0O000O000O00 ,dropin =O000O0O0O000O0O00 [-1 ]+1 ,max_text_len =max_text_len )#line:58
        if O00O0O00O0O00OOO0 ==None :#line:59
            break #line:60
        O000O00OO00O0000O .append (O00O0O00O0O00OOO0 )#line:61
        O000O0O0O000O0O00 .append (O000O000O0O0000O0 +len (O0O0OOOO000O0OOOO ))#line:62
        O000O00O0OO000O0O .append (O000O000O0O0000O0 +len (O0O0OOOO000O0OOOO )+len (O00O0O00O0O00OOO0 )+len (OOOOO0O000O000O00 )-1 )#line:63
    O000O0O0O000O0O00 .pop (0 )#line:64
    O000O00O0OO000O0O .pop (0 )#line:65
    return O000O00OO00O0000O ,O000O0O0O000O0O00 ,O000O00O0OO000O0O #line:66
class vcscraping :#line:69
    def __init__ (OO0OOO0OO0O00OOOO ,O0OOO0O0O0O00O0O0 ,url2 =None ):#line:70
        if url2 ==None :#line:71
            OO0OOO0OO0O00OOOO .html =get_html (O0OOO0O0O0O00O0O0 )#line:72
            OO0OOO0OO0O00OOOO .mode ='single'#line:73
            print ('mode = <single page>')#line:74
        else :#line:75
            OO0OOO0OO0O00OOOO .html =get_html (O0OOO0O0O0O00O0O0 )#line:76
            OO0OOO0OO0O00OOOO .html2 =get_html (url2 )#line:77
            OO0OOO0OO0O00OOOO .mode ='multi'#line:78
            print ('mode = <multi page>')#line:79
    def __del__ (O00OO0O0000O0O000 ):#line:81
        pass #line:82
    def find_text (OO0OOOOO0O00O0000 ,OOOOO0OOOOO0O00OO ,O0OOOOO0O0O0OOO0O ,max_text_len =1000 ):#line:85
        O0OOOOOO00OO00000 =OO0OOOOO0O00O0000 .html .find (OOOOO0OOOOO0O00OO )#line:86
        if O0OOOOOO00OO00000 <0 :#line:87
            return None ,None #line:88
        O00O00OOO00O0000O =OO0OOOOO0O00O0000 .html [O0OOOOOO00OO00000 +len (OOOOO0OOOOO0O00OO ):O0OOOOOO00OO00000 +len (OOOOO0OOOOO0O00OO )+max_text_len ]#line:89
        O0O000000O000OOO0 =O00O00OOO00O0000O .find (O0OOOOO0O0O0OOO0O )#line:90
        if O0O000000O000OOO0 <0 :#line:91
            return None ,None #line:92
        O00O00OOO00O0000O =O00O00OOO00O0000O [:O0O000000O000OOO0 ]#line:93
        return O00O00OOO00O0000O ,O0OOOOOO00OO00000 +len (OOOOO0OOOOO0O00OO ),O0OOOOOO00OO00000 +len (OOOOO0OOOOO0O00OO )+O0O000000O000OOO0 #line:94
    def get_texts (O000O000O00O0OO00 ,OOO0O0O00O00OO00O ,O00O000000O0OOO00 ,max_text_len =1000 ):#line:97
        if O000O000O00O0OO00 .mode !='single':#line:98
            print ('this method is avalable only in single mode')#line:99
            return None ,None #line:100
        O00O000OOO00O0O00 =[]#line:101
        OOO000000OO0OOOO0 =[-1 ]#line:102
        O0O0O00O0OO0O0OOO =[-1 ]#line:103
        while 1 :#line:104
            O0OOO0OOO000O00O0 ,O00OO00OOO00OOO0O =find_text (O000O000O00O0OO00 .html ,OOO0O0O00O00OO00O ,O00O000000O0OOO00 ,dropin =OOO000000OO0OOOO0 [-1 ]+1 ,max_text_len =max_text_len )#line:105
            if O0OOO0OOO000O00O0 ==None :#line:106
                break #line:107
            O00O000OOO00O0O00 .append (O0OOO0OOO000O00O0 )#line:108
            OOO000000OO0OOOO0 .append (O00OO00OOO00OOO0O +len (OOO0O0O00O00OO00O ))#line:109
            O0O0O00O0OO0O0OOO .append (O00OO00OOO00OOO0O +len (OOO0O0O00O00OO00O )+len (O0OOO0OOO000O00O0 )+len (O00O000000O0OOO00 )-1 )#line:110
        OOO000000OO0OOOO0 .pop (0 )#line:111
        O0O0O00O0OO0O0OOO .pop (0 )#line:112
        return O00O000OOO00O0O00 ,OOO000000OO0OOOO0 ,O0O0O00O0OO0O0OOO #line:113
    def find_presuf (OOO0OO0O000OO0O0O ,O00O0O00OO0OO0OOO ,OOOOOO000O0OOO000 ,max_text_len =None ,min_text_num =2 ,max_text_num =1000 ,max_presuf_len =40 ):#line:115
        if OOO0OO0O000OO0O0O .mode =='single':#line:116
            if max_text_len ==None :#line:119
                max_text_len =int (max (len (O00O0O00OO0OO0OOO ),len (OOOOOO000O0OOO000 ))*2 )#line:120
            OO0OOO0O0O0O00OOO =find_starts (OOO0OO0O000OO0O0O .html ,O00O0O00OO0OO0OOO )#line:123
            O00OO00O00O0O00O0 =np .zeros ((max_presuf_len *max_presuf_len ,3 ),int )#line:126
            O00OO00O00O0O00O0 [:,:2 ]=np .array (list (itertools .product (range (1 ,max_presuf_len +1 ),range (1 ,max_presuf_len +1 ))))#line:127
            O00OO00O00O0O00O0 [:,2 ]=np .sum (O00OO00O00O0O00O0 [:,:2 ],axis =1 )#line:128
            O00OO00O00O0O00O0 =O00OO00O00O0O00O0 [np .argsort (O00OO00O00O0O00O0 [:,2 ])]#line:129
            print ('-------------- setting --------------')#line:132
            print ('@ single'.format ())#line:133
            print ('max_text_len = {}'.format (max_text_len ))#line:134
            print ('min_text_num = {}'.format (min_text_num ))#line:135
            print ('max_text_num = {}'.format (max_text_num ))#line:136
            print ('max_presuf_len = {}'.format (max_presuf_len ))#line:137
            print ('--------------- start ---------------')#line:138
            O000OOO0O0OO0O000 =len (O00OO00O00O0O00O0 )//25 #line:141
            O00O00OO0O00O0O00 =False #line:144
            for O00O0OO00O0OO0OO0 ,O0OOO0O0OO0OOOOO0 in enumerate (OO0OOO0O0O0O00OOO ):#line:145
                print ('try {}/{} |'.format (O00O0OO00O0OO0OO0 +1 ,len (OO0OOO0O0O0O00OOO )),end ='')#line:147
                for OOOOOO0O00O000O00 ,(O00O0OO00O0OO0OO0 ,O0O00000O0O0OO0O0 )in enumerate (O00OO00O00O0O00O0 [:,:2 ]):#line:149
                    if OOOOOO0O00O000O00 %O000OOO0O0OO0O000 ==0 :#line:150
                        print ('{}'.format ('>'),end ='')#line:151
                    O000OO0O0OOOOO0O0 =OOO0OO0O000OO0O0O .html [O0OOO0O0OO0OOOOO0 -O00O0OO00O0OO0OO0 :O0OOO0O0OO0OOOOO0 ]#line:154
                    O0OO0OOO00O0OO0O0 =OOO0OO0O000OO0O0O .html [O0OOO0O0OO0OOOOO0 +len (O00O0O00OO0OO0OOO ):O0OOO0O0OO0OOOOO0 +len (O00O0O00OO0OO0OOO )+O0O00000O0O0OO0O0 ]#line:155
                    OOOO000O0OOOO0O0O ,OOOO0OO00OOOOOO0O ,O0OOOOO000OOOOOO0 =find_texts (OOO0OO0O000OO0O0O .html ,O000OO0O0OOOOO0O0 ,O0OO0OOO00O0OO0O0 ,max_text_len =max_text_len )#line:156
                    if len (OOOO000O0OOOO0O0O )<2 :#line:158
                        continue #line:159
                    if OOOO000O0OOOO0O0O [0 ]==O00O0O00OO0OO0OOO and OOOO000O0OOOO0O0O [1 ]==OOOOOO000O0OOO000 and len (OOOO000O0OOOO0O0O )>=min_text_num and len (OOOO000O0OOOO0O0O )<=max_text_num :#line:162
                        OOOO000O0OOOOOOO0 =deepcopy (O000OO0O0OOOOO0O0 )#line:163
                        OO0OOOO000OO000OO =deepcopy (O0OO0OOO00O0OO0O0 )#line:164
                        O00O00OO0O00O0O00 =True #line:168
                        break #line:169
                print ()#line:170
                if O00O00OO0O00O0O00 :#line:171
                    break #line:172
            print ('---------------- end ----------------')#line:174
            if O00O00OO0O00O0O00 ==False :#line:176
                print ('not found'.format ())#line:177
                print ('-------------------------------------')#line:178
                return None ,None #line:180
            print ('found = {}'.format (len (OOOO000O0OOOO0O0O )))#line:183
            print ('prefix = {}'.format (repr (OOOO000O0OOOOOOO0 )))#line:184
            print ('suffix = {}'.format (repr (OO0OOOO000OO000OO )))#line:185
            print ('-------------------------------------')#line:186
            return OOOO000O0OOOOOOO0 ,OO0OOOO000OO000OO #line:188
        if OOO0OO0O000OO0O0O .mode =='multi':#line:191
            if max_text_len ==None :#line:194
                max_text_len =int (max (len (O00O0O00OO0OO0OOO ),len (OOOOOO000O0OOO000 ))*2 )#line:195
            OO0OOO0O0O0O00OOO =find_starts (OOO0OO0O000OO0O0O .html ,O00O0O00OO0OO0OOO )#line:198
            O00OO00O00O0O00O0 =np .zeros ((max_presuf_len *max_presuf_len ,3 ),int )#line:201
            O00OO00O00O0O00O0 [:,:2 ]=np .array (list (itertools .product (range (1 ,max_presuf_len +1 ),range (1 ,max_presuf_len +1 ))))#line:202
            O00OO00O00O0O00O0 [:,2 ]=np .sum (O00OO00O00O0O00O0 [:,:2 ],axis =1 )#line:203
            O00OO00O00O0O00O0 =O00OO00O00O0O00O0 [np .argsort (O00OO00O00O0O00O0 [:,2 ])]#line:204
            print ('-------------- setting --------------')#line:207
            print ('@ multi'.format ())#line:208
            print ('max_text_len = {}'.format (max_text_len ))#line:209
            print ('max_presuf_len = {}'.format (max_presuf_len ))#line:210
            print ('--------------- start ---------------')#line:211
            O000OOO0O0OO0O000 =len (O00OO00O00O0O00O0 )//25 #line:214
            O00O00OO0O00O0O00 =False #line:217
            for O00O0OO00O0OO0OO0 ,O0OOO0O0OO0OOOOO0 in enumerate (OO0OOO0O0O0O00OOO ):#line:218
                print ('try {}/{} |'.format (O00O0OO00O0OO0OO0 +1 ,len (OO0OOO0O0O0O00OOO )),end ='')#line:220
                for OOOOOO0O00O000O00 ,(O00O0OO00O0OO0OO0 ,O0O00000O0O0OO0O0 )in enumerate (O00OO00O00O0O00O0 [:,:2 ]):#line:222
                    if OOOOOO0O00O000O00 %O000OOO0O0OO0O000 ==0 :#line:223
                        print ('{}'.format ('>'),end ='')#line:224
                    O000OO0O0OOOOO0O0 =OOO0OO0O000OO0O0O .html [O0OOO0O0OO0OOOOO0 -O00O0OO00O0OO0OO0 :O0OOO0O0OO0OOOOO0 ]#line:227
                    O0OO0OOO00O0OO0O0 =OOO0OO0O000OO0O0O .html [O0OOO0O0OO0OOOOO0 +len (O00O0O00OO0OO0OOO ):O0OOO0O0OO0OOOOO0 +len (O00O0O00OO0OO0OOO )+O0O00000O0O0OO0O0 ]#line:228
                    OOO0O00OOO0O00OOO ,OO00O0OOO000OOOO0 =find_text (OOO0OO0O000OO0O0O .html ,O000OO0O0OOOOO0O0 ,O0OO0OOO00O0OO0O0 ,max_text_len =max_text_len )#line:229
                    O0O0000O0OOO0OO0O ,OOOO0OOOOOO00O00O =find_text (OOO0OO0O000OO0O0O .html2 ,O000OO0O0OOOOO0O0 ,O0OO0OOO00O0OO0O0 ,max_text_len =max_text_len )#line:230
                    if OOO0O00OOO0O00OOO ==None or O0O0000O0OOO0OO0O ==None :#line:232
                        continue #line:233
                    if OOO0O00OOO0O00OOO ==O00O0O00OO0OO0OOO and O0O0000O0OOO0OO0O ==OOOOOO000O0OOO000 :#line:236
                        OOOO000O0OOOOOOO0 =deepcopy (O000OO0O0OOOOO0O0 )#line:237
                        OO0OOOO000OO000OO =deepcopy (O0OO0OOO00O0OO0O0 )#line:238
                        O00O00OO0O00O0O00 =True #line:239
                        break #line:240
                print ()#line:241
                if O00O00OO0O00O0O00 :#line:242
                    break #line:243
            print ('---------------- end ----------------')#line:245
            if O00O00OO0O00O0O00 ==False :#line:247
                print ('not found'.format ())#line:248
                print ('-------------------------------------')#line:249
                return None ,None #line:250
            print ('prefix = {}'.format (repr (OOOO000O0OOOOOOO0 )))#line:253
            print ('suffix = {}'.format (repr (OO0OOOO000OO000OO )))#line:254
            print ('-------------------------------------')#line:255
            return OOOO000O0OOOOOOO0 ,OO0OOOO000OO000OO #line:256
if __name__ =='__main__':#line:261
    url1 ='https://wiki.xn--rckteqa2e.com/wiki/%E3%83%95%E3%82%B7%E3%82%AE%E3%83%80%E3%83%8D'#line:275
    url2 ='https://wiki.xn--rckteqa2e.com/wiki/%E3%83%95%E3%82%B7%E3%82%AE%E3%82%BD%E3%82%A6'#line:276
    query1 ='うまれたときから せなかに しょくぶつの タネが あって すこしずつ おおきく そだつ。'#line:277
    query2 ='つぼみが せなかに ついていて ようぶんを きゅうしゅうしていくと おおきな はなが さくという。'#line:278
    myscraping =vcscraping (url1 ,url2 )#line:280
    pre ,suf =myscraping .find_presuf (query1 ,query2 )#line:281
    url3 ='https://wiki.xn--rckteqa2e.com/wiki/%E3%83%95%E3%82%B7%E3%82%AE%E3%83%90%E3%83%8A'#line:283
    url4 ='https://wiki.xn--rckteqa2e.com/wiki/%E3%83%92%E3%83%88%E3%82%AB%E3%82%B2'#line:284
    myscraping =vcscraping (url3 )#line:286
    text ,start ,end =myscraping .find_text (pre ,suf )#line:287
    print (text )#line:288
    print (myscraping .html [start :end ])#line:289
    myscraping =vcscraping (url4 )#line:291
    text ,start ,end =myscraping .find_text (pre ,suf )#line:292
    print (text )#line:293
    print (myscraping .html [start :end ])#line:294
