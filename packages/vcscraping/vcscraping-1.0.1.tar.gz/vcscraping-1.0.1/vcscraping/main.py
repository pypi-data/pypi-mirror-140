import itertools #line:2
import numpy as np #line:3
from copy import deepcopy #line:4
from requests_html import HTMLSession #line:7
import warnings #line:8
warnings .simplefilter ('ignore')#line:9
def get_html (OOO0OOO0OO000O0OO ):#line:12
    O0O0OO0O0O000O000 =HTMLSession ()#line:19
    O0O0O0000O00O000O =O0O0OO0O0O000O000 .get (OOO0OOO0OO000O0OO )#line:20
    O0O0O0000O00O000O .html .arender ()#line:21
    O0O000000OO000O00 =O0O0O0000O00O000O .html .raw_html .replace (b'\t',b'')#line:23
    O0O000000OO000O00 =O0O000000OO000O00 .decode ('utf-8')#line:25
    return O0O000000OO000O00 #line:27
def find_starts (OO0O000O0000O00O0 ,OO0O00000OO000O0O ):#line:30
    O00O000O00000O0OO =[-1 ]#line:31
    while 1 :#line:32
        O0OOO0OOOO0OOOOOO =OO0O000O0000O00O0 .find (OO0O00000OO000O0O ,O00O000O00000O0OO [-1 ]+1 )#line:33
        if O0OOO0OOOO0OOOOOO <0 :#line:34
            break #line:35
        O00O000O00000O0OO .append (O0OOO0OOOO0OOOOOO )#line:36
    O00O000O00000O0OO .pop (0 )#line:37
    return O00O000O00000O0OO #line:38
def get_between (O00OO0O0OO0OOO000 ,O000OOOOO0O00O00O ,OOO0O00O0O0OO0OO0 ,dropin =0 ,max_text_len =1000 ):#line:41
    OO00OOO0O00OO00OO =O00OO0O0OO0OOO000 .find (O000OOOOO0O00O00O ,dropin )#line:42
    if OO00OOO0O00OO00OO <0 :#line:43
        return None ,-1 ,-1 #line:44
    O0OO0000OOOOOOOOO =O00OO0O0OO0OOO000 [OO00OOO0O00OO00OO +len (O000OOOOO0O00O00O ):OO00OOO0O00OO00OO +len (O000OOOOO0O00O00O )+max_text_len ]#line:45
    OO0OO0O00O00O00O0 =O0OO0000OOOOOOOOO .find (OOO0O00O0O0OO0OO0 )#line:46
    if OO0OO0O00O00O00O0 <0 :#line:47
        return None ,-1 ,-1 #line:48
    O0OO0000OOOOOOOOO =O0OO0000OOOOOOOOO [:OO0OO0O00O00O00O0 ]#line:49
    return O0OO0000OOOOOOOOO ,OO00OOO0O00OO00OO +len (O000OOOOO0O00O00O ),OO00OOO0O00OO00OO +len (O000OOOOO0O00O00O )+OO0OO0O00O00O00O0 #line:50
def get_between_all (OOOOO0O00O0O0000O ,OO0OOOOOO000OO000 ,O000OO0OOO0OOO0OO ,max_text_len =1000 ):#line:53
    O0OOO0OO0OO0O0O0O =[]#line:54
    OO00O0O00O00OO0O0 =[-1 ]#line:55
    OO000O00000OOO0OO =[-1 ]#line:56
    while 1 :#line:57
        OOOOO0O000O0OOO00 ,OOOOOOOO0OOOO0OOO ,OOOO0O0O0OO00O00O =get_between (OOOOO0O00O0O0000O ,OO0OOOOOO000OO000 ,O000OO0OOO0OOO0OO ,dropin =OO00O0O00O00OO0O0 [-1 ]+1 ,max_text_len =max_text_len )#line:58
        if OOOOO0O000O0OOO00 ==None :#line:59
            break #line:60
        O0OOO0OO0OO0O0O0O .append (OOOOO0O000O0OOO00 )#line:61
        OO00O0O00O00OO0O0 .append (OOOOOOOO0OOOO0OOO )#line:62
        OO000O00000OOO0OO .append (OOOO0O0O0OO00O00O )#line:63
    OO00O0O00O00OO0O0 .pop (0 )#line:64
    OO000O00000OOO0OO .pop (0 )#line:65
    return O0OOO0OO0OO0O0O0O ,OO00O0O00O00OO0O0 ,OO000O00000OOO0OO #line:66
class vcscraping :#line:69
    def __init__ (O0OOOO0O00O0O0OO0 ,O0000O0OO00OOOO0O ,url2 =None ):#line:70
        if url2 ==None :#line:71
            O0OOOO0O00O0O0OO0 .html =get_html (O0000O0OO00OOOO0O )#line:72
            O0OOOO0O00O0O0OO0 .mode ='single'#line:73
            print ('mode = <single page>')#line:74
        else :#line:75
            O0OOOO0O00O0O0OO0 .html =get_html (O0000O0OO00OOOO0O )#line:76
            O0OOOO0O00O0O0OO0 .html2 =get_html (url2 )#line:77
            O0OOOO0O00O0O0OO0 .mode ='multi'#line:78
            print ('mode = <multi page>')#line:79
    def __del__ (OOO0OO000000O0OO0 ):#line:81
        pass #line:82
    def get_between (OOO0O0O00OOO000OO ,O0O0OOO00O0000OOO ,OOOO00O00OO0OO00O ,dropin =0 ,max_text_len =1000 ):#line:85
        OOO0O0OOOOO0O0O00 =OOO0O0O00OOO000OO .html .find (O0O0OOO00O0000OOO ,dropin )#line:86
        if OOO0O0OOOOO0O0O00 <0 :#line:87
            return None ,-1 ,-1 #line:88
        O0OOO0000000O0O00 =OOO0O0O00OOO000OO .html [OOO0O0OOOOO0O0O00 +len (O0O0OOO00O0000OOO ):OOO0O0OOOOO0O0O00 +len (O0O0OOO00O0000OOO )+max_text_len ]#line:89
        OO00000O0O000O00O =O0OOO0000000O0O00 .find (OOOO00O00OO0OO00O )#line:90
        if OO00000O0O000O00O <0 :#line:91
            return None ,-1 ,-1 #line:92
        O0OOO0000000O0O00 =O0OOO0000000O0O00 [:OO00000O0O000O00O ]#line:93
        return O0OOO0000000O0O00 ,OOO0O0OOOOO0O0O00 +len (O0O0OOO00O0000OOO ),OOO0O0OOOOO0O0O00 +len (O0O0OOO00O0000OOO )+OO00000O0O000O00O #line:94
    def get_between_all (O0OOO0O0OOO00O000 ,O00O0OOO000O00000 ,O00O00OO00O00000O ,max_text_len =1000 ):#line:97
        O00O0O0O0OO0000O0 =[]#line:98
        O000OO0O00OO0O00O =[-1 ]#line:99
        O0O0000O000OO00O0 =[-1 ]#line:100
        while 1 :#line:101
            OOOO0OOO0O0OOO0O0 ,O00OO000O0O000OO0 ,OO00OO000O0O0OO0O =get_between (O0OOO0O0OOO00O000 .html ,O00O0OOO000O00000 ,O00O00OO00O00000O ,dropin =O000OO0O00OO0O00O [-1 ]+1 ,max_text_len =max_text_len )#line:102
            if OOOO0OOO0O0OOO0O0 ==None :#line:103
                break #line:104
            O00O0O0O0OO0000O0 .append (OOOO0OOO0O0OOO0O0 )#line:105
            O000OO0O00OO0O00O .append (O00OO000O0O000OO0 )#line:106
            O0O0000O000OO00O0 .append (OO00OO000O0O0OO0O )#line:107
        O000OO0O00OO0O00O .pop (0 )#line:108
        O0O0000O000OO00O0 .pop (0 )#line:109
        print ('found = {}'.format (len (O00O0O0O0OO0000O0 )))#line:110
        return O00O0O0O0OO0000O0 ,O000OO0O00OO0O00O ,O0O0000O000OO00O0 #line:111
    def find_presuf (OO00O00O000O0O0OO ,O00O00OOOO0O0OO00 ,O0000000000000OOO ,max_text_len =None ,min_text_num =2 ,max_text_num =1000 ,max_presuf_len =40 ):#line:113
        if OO00O00O000O0O0OO .mode =='single':#line:114
            if max_text_len ==None :#line:117
                max_text_len =int (max (len (O00O00OOOO0O0OO00 ),len (O0000000000000OOO ))*2 )#line:118
            O0OO000O0OOOO0OO0 =find_starts (OO00O00O000O0O0OO .html ,O00O00OOOO0O0OO00 )#line:121
            O00OOO0OO0O0000O0 =np .zeros ((max_presuf_len *max_presuf_len ,3 ),int )#line:124
            O00OOO0OO0O0000O0 [:,:2 ]=np .array (list (itertools .product (range (1 ,max_presuf_len +1 ),range (1 ,max_presuf_len +1 ))))#line:125
            O00OOO0OO0O0000O0 [:,2 ]=np .sum (O00OOO0OO0O0000O0 [:,:2 ],axis =1 )#line:126
            O00OOO0OO0O0000O0 =O00OOO0OO0O0000O0 [np .argsort (O00OOO0OO0O0000O0 [:,2 ])]#line:127
            print ('-------------- setting --------------')#line:130
            print ('@ single'.format ())#line:131
            print ('max_text_len = {}'.format (max_text_len ))#line:132
            print ('min_text_num = {}'.format (min_text_num ))#line:133
            print ('max_text_num = {}'.format (max_text_num ))#line:134
            print ('max_presuf_len = {}'.format (max_presuf_len ))#line:135
            print ('--------------- start ---------------')#line:136
            O00O0000O000OO00O =len (O00OOO0OO0O0000O0 )//25 #line:139
            OO0OOO000O0OOO0OO =False #line:142
            for O0O0OO00OOOO00OO0 ,O00O0OOOOO0O0OO0O in enumerate (O0OO000O0OOOO0OO0 ):#line:143
                print ('try {}/{} |'.format (O0O0OO00OOOO00OO0 +1 ,len (O0OO000O0OOOO0OO0 )),end ='')#line:145
                for O0O0OOO0O0OO00000 ,(O0O0OO00OOOO00OO0 ,OOOOOOO00O0000OO0 )in enumerate (O00OOO0OO0O0000O0 [:,:2 ]):#line:147
                    if O0O0OOO0O0OO00000 %O00O0000O000OO00O ==0 :#line:148
                        print ('{}'.format ('>'),end ='')#line:149
                    OOOOOOO000O00OOO0 =OO00O00O000O0O0OO .html [O00O0OOOOO0O0OO0O -O0O0OO00OOOO00OO0 :O00O0OOOOO0O0OO0O ]#line:152
                    OOOO000OOO00000O0 =OO00O00O000O0O0OO .html [O00O0OOOOO0O0OO0O +len (O00O00OOOO0O0OO00 ):O00O0OOOOO0O0OO0O +len (O00O00OOOO0O0OO00 )+OOOOOOO00O0000OO0 ]#line:153
                    O0O000OO0O00O0OO0 ,O0OO0000000OO0OO0 ,O0OO0000OOOO0000O =get_between_all (OO00O00O000O0O0OO .html ,OOOOOOO000O00OOO0 ,OOOO000OOO00000O0 ,max_text_len =max_text_len )#line:154
                    if len (O0O000OO0O00O0OO0 )<2 :#line:156
                        continue #line:157
                    if O0O000OO0O00O0OO0 [0 ]==O00O00OOOO0O0OO00 and O0O000OO0O00O0OO0 [1 ]==O0000000000000OOO and len (O0O000OO0O00O0OO0 )>=min_text_num and len (O0O000OO0O00O0OO0 )<=max_text_num :#line:160
                        OO0OOOO0OOO00O0O0 =deepcopy (OOOOOOO000O00OOO0 )#line:161
                        O0OO00OO0O0000000 =deepcopy (OOOO000OOO00000O0 )#line:162
                        OO0OOO000O0OOO0OO =True #line:166
                        break #line:167
                print ()#line:168
                if OO0OOO000O0OOO0OO :#line:169
                    break #line:170
            print ('---------------- end ----------------')#line:172
            if OO0OOO000O0OOO0OO ==False :#line:174
                print ('not found'.format ())#line:175
                print ('-------------------------------------')#line:176
                return None ,None #line:178
            print ('found = {}'.format (len (O0O000OO0O00O0OO0 )))#line:181
            print ('prefix = {}'.format (repr (OO0OOOO0OOO00O0O0 )))#line:182
            print ('suffix = {}'.format (repr (O0OO00OO0O0000000 )))#line:183
            print ('-------------------------------------')#line:184
            return OO0OOOO0OOO00O0O0 ,O0OO00OO0O0000000 #line:186
        if OO00O00O000O0O0OO .mode =='multi':#line:189
            if max_text_len ==None :#line:192
                max_text_len =int (max (len (O00O00OOOO0O0OO00 ),len (O0000000000000OOO ))*2 )#line:193
            O0OO000O0OOOO0OO0 =find_starts (OO00O00O000O0O0OO .html ,O00O00OOOO0O0OO00 )#line:196
            O00OOO0OO0O0000O0 =np .zeros ((max_presuf_len *max_presuf_len ,3 ),int )#line:199
            O00OOO0OO0O0000O0 [:,:2 ]=np .array (list (itertools .product (range (1 ,max_presuf_len +1 ),range (1 ,max_presuf_len +1 ))))#line:200
            O00OOO0OO0O0000O0 [:,2 ]=np .sum (O00OOO0OO0O0000O0 [:,:2 ],axis =1 )#line:201
            O00OOO0OO0O0000O0 =O00OOO0OO0O0000O0 [np .argsort (O00OOO0OO0O0000O0 [:,2 ])]#line:202
            print ('-------------- setting --------------')#line:205
            print ('@ multi'.format ())#line:206
            print ('max_text_len = {}'.format (max_text_len ))#line:207
            print ('max_presuf_len = {}'.format (max_presuf_len ))#line:208
            print ('--------------- start ---------------')#line:209
            O00O0000O000OO00O =len (O00OOO0OO0O0000O0 )//25 #line:212
            OO0OOO000O0OOO0OO =False #line:215
            for O0O0OO00OOOO00OO0 ,O00O0OOOOO0O0OO0O in enumerate (O0OO000O0OOOO0OO0 ):#line:216
                print ('try {}/{} |'.format (O0O0OO00OOOO00OO0 +1 ,len (O0OO000O0OOOO0OO0 )),end ='')#line:218
                for O0O0OOO0O0OO00000 ,(O0O0OO00OOOO00OO0 ,OOOOOOO00O0000OO0 )in enumerate (O00OOO0OO0O0000O0 [:,:2 ]):#line:220
                    if O0O0OOO0O0OO00000 %O00O0000O000OO00O ==0 :#line:221
                        print ('{}'.format ('>'),end ='')#line:222
                    OOOOOOO000O00OOO0 =OO00O00O000O0O0OO .html [O00O0OOOOO0O0OO0O -O0O0OO00OOOO00OO0 :O00O0OOOOO0O0OO0O ]#line:225
                    OOOO000OOO00000O0 =OO00O00O000O0O0OO .html [O00O0OOOOO0O0OO0O +len (O00O00OOOO0O0OO00 ):O00O0OOOOO0O0OO0O +len (O00O00OOOO0O0OO00 )+OOOOOOO00O0000OO0 ]#line:226
                    OO0O0O000OO0O0OO0 ,OOO0O0OOOOO00O00O ,O000O0OOO00OO00O0 =get_between (OO00O00O000O0O0OO .html ,OOOOOOO000O00OOO0 ,OOOO000OOO00000O0 ,max_text_len =max_text_len )#line:227
                    OO00OO0O0O0O0OO0O ,O00OOO000O0OO0O00 ,O0O0OO000000000O0 =get_between (OO00O00O000O0O0OO .html2 ,OOOOOOO000O00OOO0 ,OOOO000OOO00000O0 ,max_text_len =max_text_len )#line:228
                    if OO0O0O000OO0O0OO0 ==None or OO00OO0O0O0O0OO0O ==None :#line:230
                        continue #line:231
                    if OO0O0O000OO0O0OO0 ==O00O00OOOO0O0OO00 and OO00OO0O0O0O0OO0O ==O0000000000000OOO :#line:234
                        OO0OOOO0OOO00O0O0 =deepcopy (OOOOOOO000O00OOO0 )#line:235
                        O0OO00OO0O0000000 =deepcopy (OOOO000OOO00000O0 )#line:236
                        OO0OOO000O0OOO0OO =True #line:237
                        break #line:238
                print ()#line:239
                if OO0OOO000O0OOO0OO :#line:240
                    break #line:241
            print ('---------------- end ----------------')#line:243
            if OO0OOO000O0OOO0OO ==False :#line:245
                print ('not found'.format ())#line:246
                print ('-------------------------------------')#line:247
                return None ,None #line:248
            print ('prefix = {}'.format (repr (OO0OOOO0OOO00O0O0 )))#line:251
            print ('suffix = {}'.format (repr (O0OO00OO0O0000000 )))#line:252
            print ('-------------------------------------')#line:253
            return OO0OOOO0OOO00O0O0 ,O0OO00OO0O0000000 #line:254
if __name__ =='__main__':#line:259
    url ='https://wiki.xn--rckteqa2e.com/wiki/%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E4%B8%80%E8%A6%A7'#line:296
    query1 ='001\n</td>\n<td><a href=\"/wiki/%E3%83%95%E3%82%B7%E3%82%AE%E3%83%80%E3%83%8D\" title=\"フシギダネ\">フシギダネ'#line:297
    query2 ='002\n</td>\n<td><a href=\"/wiki/%E3%83%95%E3%82%B7%E3%82%AE%E3%82%BD%E3%82%A6\" title=\"フシギソウ\">フシギソウ'#line:298
    myscraping =vcscraping (url )#line:300
    pre ,suf =myscraping .find_presuf (query1 ,query2 ,min_text_num =10 )#line:301
    texts ,starts ,ends =myscraping .get_between_all (pre ,suf )#line:302
    print (texts [:5 ])#line:303
    url_start =texts [0 ].find ('title=\"')+len ('title=\"')#line:306
    url_end =texts [0 ].find ('\">')#line:307
    print (url_start ,url_end )#line:308
    print (texts [0 ][url_start :url_end ])#line:309
    url_start =texts [0 ].find ('href=\"')+len ('href=\"')#line:312
    url_end =texts [0 ].find ('\" title')#line:313
    print (url_start ,url_end )#line:314
    print (texts [0 ][url_start :url_end ])#line:315
