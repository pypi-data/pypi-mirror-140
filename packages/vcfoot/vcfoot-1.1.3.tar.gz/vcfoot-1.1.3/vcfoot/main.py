import math #line:2
from scipy import signal #line:3
from copy import deepcopy #line:4
import numpy as np #line:5
import cv2 #line:6
import pickle #line:7
from vcopt import vcopt #line:8
try :#line:10
    from foot_tool import ft ,pl_class ,cl_class #line:11
    print ('import normal version')#line:12
except :#line:13
    from .foot_tool import ft ,pl_class ,cl_class #line:14
    print ('import . version')#line:15
class vcfoot :#line:20
    def __init__ (OO0O00O00OOOOO00O ):#line:21
        pass #line:22
    def __del__ (OO000OO0OO00O0O00 ):#line:23
        pass #line:24
    def level (OO0O0OO0O000OOO0O ,O0OO0O000OO0O0OO0 ,url =None ,flip =False ,save =None ,test =0 ):#line:27
        print ('\n### objファイルの読み込み')#line:29
        O00000OOOO0OOO00O ,O0O0O000OO0000OOO ,O0OOO000OO000OOO0 =ft .load_obj (O0OO0O000OO0O0OO0 )#line:31
        if np .max (O0O0O000OO0000OOO )<=1.0 :#line:33
            O0O0O000OO0000OOO =np .array (O0O0O000OO0000OOO *255.0 ,int )#line:34
        OOO0OOOO0O0000OOO ,OO0OOOOOO00O0O0O0 =ft .down_sample (O00000OOOO0OOO00O ,O0O0O000OO0000OOO ,20000 )#line:36
        if test :#line:37
            ft .showc (OOO0OOOO0O0000OOO ,OO0OOOOOO00O0O0O0 ,'xz')#line:38
        print ('\n### 静置GA')#line:44
        try :#line:46
            O0OO0O0O00O0OOO00 #line:47
        except NameError :#line:48
            print ('\n### ダウンサンプル')#line:50
            OOO0OOOO0O0000OOO ,OO0OOOOOO00O0O0O0 =ft .down_sample (O00000OOOO0OOO00O ,O0O0O000OO0000OOO ,8000 )#line:52
            def OO000OO000O0O0O0O (O0OO0OOOOO00OO000 ):#line:55
                O00O00O0OOO00O000 =deepcopy (OOO0OOOO0O0000OOO )#line:57
                O00O00O0OOO00O000 =ft .rotate_3D_x (O00O00O0OOO00O000 ,O0OO0OOOOO00OO000 [0 ])#line:58
                O00O00O0OOO00O000 =ft .rotate_3D_y (O00O00O0OOO00O000 ,O0OO0OOOOO00OO000 [1 ])#line:59
                OOOOO00OO0O0OO00O ,O00OOO0O00O00O000 =np .histogram (O00O00O0OOO00O000 [:,2 ],bins =50 )#line:61
                OO000O0000O0OO000 =4 #line:63
                OOOO00000O0O00000 =np .ones (OO000O0000O0OO000 )/OO000O0000O0OO000 #line:64
                O000O000000O0OOO0 =signal .convolve (OOOOO00OO0O0OO00O ,OOOO00000O0O00000 ,mode ='same')#line:65
                OO000O0OOOOO0O0O0 =np .max (O000O000000O0OOO0 )#line:67
                return OO000O0OOOOO0O0O0 #line:68
            def O0OO000O0O0000000 ():#line:71
                OOOO00O0O0OO00OO0 =[[0 ,180 ],[0 ,180 ]]#line:73
                OO00O0OO0OOO0O0O0 ,OOOO0OO00OO0000O0 =vcopt ().rcGA (OOOO00O0O0OO00OO0 ,OO000OO000O0O0O0O ,99999 ,show_pool_func ='bar',seed ='grendel_master_eternity',pool_num =100 ,core_num =8 ,max_gen =10000 )#line:82
                return OO00O0OO0OOO0O0O0 #line:83
            print ('\n### 静置GA')#line:86
            O0OO0O0O00O0OOO00 =O0OO000O0O0000000 ()#line:88
            print ('para = [{}, {}]'.format (O0OO0O0O00O0OOO00 [0 ],O0OO0O0O00O0OOO00 [1 ]))#line:90
        print ('\n### 反映')#line:94
        O00000OOOO0OOO00O =ft .rotate_3D_x (O00000OOOO0OOO00O ,O0OO0O0O00O0OOO00 [0 ])#line:96
        O00000OOOO0OOO00O =ft .rotate_3D_y (O00000OOOO0OOO00O ,O0OO0O0O00O0OOO00 [1 ])#line:97
        print ('\n### 確認')#line:102
        OOO0OOOO0O0000OOO ,OO0OOOOOO00O0O0O0 =ft .down_sample (O00000OOOO0OOO00O ,O0O0O000OO0000OOO ,20000 )#line:104
        if test :#line:105
            ft .showc (OOO0OOOO0O0000OOO ,OO0OOOOOO00O0O0O0 ,'xz')#line:106
        print ('\n### 逆さなら反転')#line:118
        O0OOOO000000O000O =np .median (O00000OOOO0OOO00O [:,2 ])#line:121
        OOO0O0000OOOOO0OO =np .mean (O00000OOOO0OOO00O [:,2 ])#line:122
        O0O0000OO0OO0OO00 =OOO0O0000OOOOO0OO >O0OOOO000000O000O #line:123
        print ('up_bool:\n{}'.format (O0O0000OO0OO0OO00 ))#line:124
        if O0O0000OO0OO0OO00 ==True :#line:126
            if flip ==False :#line:128
                pass #line:129
            if flip ==True :#line:131
                print ('強制反転')#line:132
                O00000OOOO0OOO00O =ft .rotate_3D_x (O00000OOOO0OOO00O ,180 )#line:133
        else :#line:135
            if flip ==False :#line:137
                print ('通常反転')#line:138
                O00000OOOO0OOO00O =ft .rotate_3D_x (O00000OOOO0OOO00O ,180 )#line:139
            if flip ==True :#line:142
                pass #line:143
        print ('\n### 確認')#line:146
        OOO0OOOO0O0000OOO ,OO0OOOOOO00O0O0O0 =ft .down_sample (O00000OOOO0OOO00O ,O0O0O000OO0000OOO ,20000 )#line:148
        if test :#line:149
            ft .showc (OOO0OOOO0O0000OOO ,OO0OOOOOO00O0O0O0 ,'xz')#line:150
        print ('\n### zレベル補正')#line:155
        O0000O0O00OOOOO0O ,O0OOO0000OOOOOOO0 =np .histogram (O00000OOOO0OOO00O [:,2 ],bins =100 )#line:158
        O00O0O00000OO0OO0 =4 #line:160
        OO0O0000000OO00O0 =np .ones (O00O0O00000OO0OO0 )/O00O0O00000OO0OO0 #line:161
        OOOO000O0O0OO0000 =signal .convolve (O0000O0O00OOOOO0O ,OO0O0000000OO00O0 ,mode ='same')#line:162
        O0OO00OOOOO0OOO00 =O0OOO0000OOOOOOO0 [np .argmax (OOOO000O0O0OO0000 )]#line:164
        print ('z_level:\n{}'.format (O0OO00OOOOO0OOO00 ))#line:165
        O00000OOOO0OOO00O [:,2 ]-=O0OO00OOOOO0OOO00 #line:167
        O00000OOOO0OOO00O [:,0 ]-=np .min (O00000OOOO0OOO00O [:,0 ])#line:170
        O00000OOOO0OOO00O [:,1 ]-=np .min (O00000OOOO0OOO00O [:,1 ])#line:171
        print ('\n### 確認')#line:174
        OOO0OOOO0O0000OOO ,OO0OOOOOO00O0O0O0 =ft .down_sample (O00000OOOO0OOO00O ,O0O0O000OO0000OOO ,20000 )#line:176
        if test :#line:177
            ft .showc (OOO0OOOO0O0000OOO ,OO0OOOOOO00O0O0O0 ,'xz')#line:178
        if save !=None :#line:180
            print ('\n### 保存')#line:182
            with open (save ,'wb')as O0OO0O0OO00O0OO00 :#line:184
                pickle .dump ([O00000OOOO0OOO00O ,O0O0O000OO0000OOO ,O0OOO000OO000OOO0 ],O0OO0O0OO00O0OO00 )#line:185
            ft .showc (OOO0OOOO0O0000OOO ,OO0OOOOOO00O0O0O0 ,'xz',save =save +'.png')#line:186
    def enkaku (O00000O0OO00OO0O0 ,O000OO0OO0O00O000 ,paper_long =297 ,paper_short =210 ,window_size =900 ,dot_size =1 ,cut_height =90 ,rate1 =0.18 ,rate2 =0.44 ,rate3 =0.54 ,side =30 ,test =0 ):#line:210
        print ('\n### pcklファイルの読み込み')#line:278
        if O000OO0OO0O00O000 [:4 ]=='http':#line:281
            O0O000O00O000OO0O ,O00O0000000OO0O00 ,OOO0OOOOO000OOO0O =ft .load_pckl_url (O000OO0OO0O00O000 )#line:282
        else :#line:283
            O0O000O00O000OO0O ,O00O0000000OO0O00 ,OOO0OOOOO000OOO0O =ft .load_pckl (O000OO0OO0O00O000 )#line:284
        if np .max (O00O0000000OO0O00 )<=1.0 :#line:286
            O00O0000000OO0O00 =np .array (O00O0000000OO0O00 *255.0 ,int )#line:287
        OOO0OOOOO000OOO0O -=1 #line:290
        OOOO0O00000O0000O =O0O000O00O000OO0O [OOO0OOOOO000OOO0O ]#line:291
        OOOOO0OOO0OO0000O =O00O0000000OO0O00 [OOO0OOOOO000OOO0O ]#line:293
        if test :#line:296
            OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 =ft .down_sample (O0O000O00O000OO0O ,O00O0000000OO0O00 ,20000 )#line:297
            ft .showc (OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 ,'xy')#line:298
        print ('\n### 紙の大きさにカット')#line:304
        try :#line:306
            O00O0OO00OO0O0OO0 #line:307
            OO0OO0O00O000O0O0 #line:308
        except NameError :#line:309
            print ('\n### 前処理')#line:311
            OOO0O0000O000O000 =cl_class (window_size ,dot_size ,paper_short ,paper_long ,rate1 )#line:314
            O0O0O000OO00OO00O ,O000O0OOOOOOOO0OO =OOO0O0000O000O000 .window_zoom (OOOO0O00000O0000O ,OOOOO0OOO0OO0000O ,min_face_num =200000 )#line:316
            O0O0O000OO00OO00O =OOO0O0000O000O000 .put_text (O0O0O000OO00OO00O ,['1, Center of paper','2, Select cut range (about)'])#line:319
            OO0O00000O000OOOO ='step1'#line:328
            cv2 .namedWindow (OO0O00000O000OOOO )#line:329
            OOOO0O0OOO0000O0O =2 #line:330
            OO000OOO0O0OO00OO =pl_class (OOOO0O0OOO0000O0O )#line:331
            cv2 .setMouseCallback (OO0O00000O000OOOO ,OOO0O0000O000O000 .onMouse ,[OO0O00000O000OOOO ,O0O0O000OO00OO00O ,OO000OOO0O0OO00OO ])#line:332
            cv2 .imshow (OO0O00000O000OOOO ,O0O0O000OO00OO00O )#line:333
            cv2 .waitKey ()#line:334
            print ('\n### 後処理')#line:337
            O00O0OO00OO0O0OO0 =np .array (OOO0O0000O000O000 .p [0 ],float )#line:340
            OO0OO0O00O000O0O0 =max (abs (OOO0O0000O000O000 .p [1 ,0 ]-OOO0O0000O000O000 .p [0 ,0 ]),abs (OOO0O0000O000O000 .p [1 ,1 ]-OOO0O0000O000O000 .p [0 ,1 ]))#line:341
            O00O0OO00OO0O0OO0 =O00O0OO00OO0O0OO0 /O000O0OOOOOOOO0OO #line:344
            OO0OO0O00O000O0O0 =OO0OO0O00O000O0O0 /O000O0OOOOOOOO0OO #line:345
            print ('cut_center = [{}, {}]'.format (O00O0OO00OO0O0OO0 [0 ],O00O0OO00OO0O0OO0 [1 ]))#line:346
            print ('cut_len = {}'.format (OO0OO0O00O000O0O0 ))#line:347
        print ('\n### 反映')#line:351
        O00O0000000OO0O00 =O00O0000000OO0O00 [O0O000O00O000OO0O [:,0 ]>O00O0OO00OO0O0OO0 [1 ]-OO0OO0O00O000O0O0 ]#line:354
        O0O000O00O000OO0O =O0O000O00O000OO0O [O0O000O00O000OO0O [:,0 ]>O00O0OO00OO0O0OO0 [1 ]-OO0OO0O00O000O0O0 ]#line:355
        O00O0000000OO0O00 =O00O0000000OO0O00 [O0O000O00O000OO0O [:,0 ]<O00O0OO00OO0O0OO0 [1 ]+OO0OO0O00O000O0O0 ]#line:356
        O0O000O00O000OO0O =O0O000O00O000OO0O [O0O000O00O000OO0O [:,0 ]<O00O0OO00OO0O0OO0 [1 ]+OO0OO0O00O000O0O0 ]#line:357
        O00O0000000OO0O00 =O00O0000000OO0O00 [O0O000O00O000OO0O [:,1 ]>O00O0OO00OO0O0OO0 [0 ]-OO0OO0O00O000O0O0 ]#line:359
        O0O000O00O000OO0O =O0O000O00O000OO0O [O0O000O00O000OO0O [:,1 ]>O00O0OO00OO0O0OO0 [0 ]-OO0OO0O00O000O0O0 ]#line:360
        O00O0000000OO0O00 =O00O0000000OO0O00 [O0O000O00O000OO0O [:,1 ]<O00O0OO00OO0O0OO0 [0 ]+OO0OO0O00O000O0O0 ]#line:361
        O0O000O00O000OO0O =O0O000O00O000OO0O [O0O000O00O000OO0O [:,1 ]<O00O0OO00OO0O0OO0 [0 ]+OO0OO0O00O000O0O0 ]#line:362
        OOOO0O0O00000O0O0 =OOOO0O00000O0000O [:,:,0 ]>O00O0OO00OO0O0OO0 [1 ]-OO0OO0O00O000O0O0 #line:364
        OO000O0000OO0OOOO =OOOO0O00000O0000O [:,:,0 ]<O00O0OO00OO0O0OO0 [1 ]+OO0OO0O00O000O0O0 #line:365
        O0O00O00O0O0OO0O0 =OOOO0O00000O0000O [:,:,1 ]>O00O0OO00OO0O0OO0 [0 ]-OO0OO0O00O000O0O0 #line:366
        O0O0OOO00OOO0OO00 =OOOO0O00000O0000O [:,:,1 ]<O00O0OO00OO0O0OO0 [0 ]+OO0OO0O00O000O0O0 #line:367
        OO0O0OOOO0O0000OO =OOOO0O0O00000O0O0 *OO000O0000OO0OOOO *O0O00O00O0O0OO0O0 *O0O0OOO00OOO0OO00 #line:368
        OO0O0OOOO0O0000OO =np .sum (OO0O0OOOO0O0000OO ,axis =1 )#line:369
        OOOO0O00000O0000O =OOOO0O00000O0000O [OO0O0OOOO0O0000OO ==3 ]#line:370
        OOOOO0OOO0OO0000O =OOOOO0OOO0OO0000O [OO0O0OOOO0O0000OO ==3 ]#line:371
        print (OOOO0O00000O0000O .shape )#line:372
        OOOO0O00000O0000O [:,:,0 ]-=np .min (O0O000O00O000OO0O [:,0 ])#line:376
        OOOO0O00000O0000O [:,:,1 ]-=np .min (O0O000O00O000OO0O [:,1 ])#line:377
        O0O000O00O000OO0O [:,0 ]-=np .min (O0O000O00O000OO0O [:,0 ])#line:378
        O0O000O00O000OO0O [:,1 ]-=np .min (O0O000O00O000OO0O [:,1 ])#line:379
        print ('\n### 確認')#line:382
        OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 =ft .down_sample (O0O000O00O000OO0O ,O00O0000000OO0O00 ,20000 )#line:384
        if test :#line:386
            ft .showc (OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 ,'xy')#line:387
        print ('\n### 紙のサイズ校正')#line:399
        try :#line:401
            O0O00O0OOOOO00OOO #line:402
            O0OOO0OOO0OOOO0OO #line:403
            OO0O0O00OO00O00OO #line:404
        except NameError :#line:405
            print ('\n### 前処理')#line:407
            OOO0O0000O000O000 =cl_class (window_size ,dot_size ,paper_short ,paper_long ,rate1 )#line:410
            O0O0O000OO00OO00O ,O000O0OOOOOOOO0OO =OOO0O0000O000O000 .window_zoom (OOOO0O00000O0000O ,OOOOO0OOO0OO0000O ,min_face_num =200000 )#line:412
            O0O0O000OO00OO00O =OOO0O0000O000O000 .put_text (O0O0O000OO00OO00O ,['1, Top-left of paper','2, Bottom-right of paper'])#line:415
            OO0O00000O000OOOO ='step2'#line:421
            cv2 .namedWindow (OO0O00000O000OOOO )#line:422
            OOOO0O0OOO0000O0O =2 #line:423
            OO000OOO0O0OO00OO =pl_class (OOOO0O0OOO0000O0O )#line:424
            cv2 .setMouseCallback (OO0O00000O000OOOO ,OOO0O0000O000O000 .onMouse ,[OO0O00000O000OOOO ,O0O0O000OO00OO00O ,OO000OOO0O0OO00OO ])#line:425
            cv2 .imshow (OO0O00000O000OOOO ,O0O0O000OO00OO00O )#line:426
            cv2 .waitKey ()#line:427
            print ('\n### 後処理')#line:430
            O0OOO0OOO0OOOO0OO =np .array (OOO0O0000O000O000 .p [0 ],float )/O000O0OOOOOOOO0OO #line:433
            print ('top_left = [{}, {}]'.format (O0OOO0OOO0OOOO0OO [0 ],O0OOO0OOO0OOOO0OO [1 ]))#line:434
            OO0O0O00OO00O00OO =np .array (OOO0O0000O000O000 .p [1 ],float )/O000O0OOOOOOOO0OO #line:437
            print ('bottom_right = [{}, {}]'.format (OO0O0O00OO00O00OO [0 ],OO0O0O00OO00O00OO [1 ]))#line:438
            O0O00OO0O00O00000 =math .atan2 (OO0O0O00OO00O00OO [1 ]-O0OOO0OOO0OOOO0OO [1 ],OO0O0O00OO00O00OO [0 ]-O0OOO0OOO0OOOO0OO [0 ])#line:441
            OOO000O00000O0OOO =math .degrees (O0O00OO0O00O00000 )#line:443
            OO0O0OO0OO00OOOOO =math .atan2 (paper_long ,paper_short )#line:447
            O000OOOOO0O00O000 =math .degrees (OO0O0OO0OO00OOOOO )#line:449
            O0O00O0OOOOO00OOO =O000OOOOO0O00O000 -OOO000O00000O0OOO #line:453
            if O0O00O0OOOOO00OOO >180 :#line:454
                O0O00O0OOOOO00OOO =-360 +O0O00O0OOOOO00OOO #line:455
            if O0O00O0OOOOO00OOO <-180 :#line:456
                O0O00O0OOOOO00OOO =360 -O0O00O0OOOOO00OOO #line:457
            print ('rotation_paper = {}'.format (O0O00O0OOOOO00OOO ))#line:458
        print ('\n### 反映')#line:462
        O0OOO0OOO0OOOO0OO =ft .rotate_2D_z (O0OOO0OOO0OOOO0OO ,theta =-O0O00O0OOOOO00OOO )#line:465
        OO0O0O00OO00O00OO =ft .rotate_2D_z (OO0O0O00OO00O00OO ,theta =-O0O00O0OOOOO00OOO )#line:466
        O0O000O00O000OO0O =ft .rotate_3D_z (O0O000O00O000OO0O ,theta =-O0O00O0OOOOO00OOO )#line:467
        for OOOO00OO0OO0OOOOO in range (3 ):#line:468
            OOOO0O00000O0000O [:,OOOO00OO0OO0OOOOO ,:]=ft .rotate_3D_z (OOOO0O00000O0000O [:,OOOO00OO0OO0OOOOO ,:],theta =-O0O00O0OOOOO00OOO )#line:469
        OO000OO0000O0OOOO =OO0O0O00OO00O00OO [0 ]-O0OOO0OOO0OOOO0OO [0 ]#line:472
        O00O000OO0O0OO00O =OO0O0O00OO00O00OO [1 ]-O0OOO0OOO0OOOO0OO [1 ]#line:473
        OOOO000OOOO00O0O0 =paper_short /OO000OO0000O0OOOO #line:475
        O000O00O000O0O000 =paper_long /O00O000OO0O0OO00O #line:476
        O000O0OOOOOOOO0OO =(OOOO000OOOO00O0O0 +O000O00O000O0O000 )/2 #line:480
        O0OOO0OOO0OOOO0OO *=O000O0OOOOOOOO0OO #line:483
        OO0O0O00OO00O00OO *=O000O0OOOOOOOO0OO #line:484
        O0O000O00O000OO0O *=O000O0OOOOOOOO0OO #line:485
        OOOO0O00000O0000O *=O000O0OOOOOOOO0OO #line:486
        O00O0000000OO0O00 =O00O0000000OO0O00 [O0O000O00O000OO0O [:,0 ]>O0OOO0OOO0OOOO0OO [1 ]-side ]#line:489
        O0O000O00O000OO0O =O0O000O00O000OO0O [O0O000O00O000OO0O [:,0 ]>O0OOO0OOO0OOOO0OO [1 ]-side ]#line:490
        O00O0000000OO0O00 =O00O0000000OO0O00 [O0O000O00O000OO0O [:,0 ]<OO0O0O00OO00O00OO [1 ]+side ]#line:491
        O0O000O00O000OO0O =O0O000O00O000OO0O [O0O000O00O000OO0O [:,0 ]<OO0O0O00OO00O00OO [1 ]+side ]#line:492
        O00O0000000OO0O00 =O00O0000000OO0O00 [O0O000O00O000OO0O [:,1 ]>O0OOO0OOO0OOOO0OO [0 ]-side ]#line:494
        O0O000O00O000OO0O =O0O000O00O000OO0O [O0O000O00O000OO0O [:,1 ]>O0OOO0OOO0OOOO0OO [0 ]-side ]#line:495
        O00O0000000OO0O00 =O00O0000000OO0O00 [O0O000O00O000OO0O [:,1 ]<OO0O0O00OO00O00OO [0 ]+side ]#line:496
        O0O000O00O000OO0O =O0O000O00O000OO0O [O0O000O00O000OO0O [:,1 ]<OO0O0O00OO00O00OO [0 ]+side ]#line:497
        OOOO0O0O00000O0O0 =OOOO0O00000O0000O [:,:,0 ]>O0OOO0OOO0OOOO0OO [1 ]-side #line:499
        OO000O0000OO0OOOO =OOOO0O00000O0000O [:,:,0 ]<OO0O0O00OO00O00OO [1 ]+side #line:500
        O0O00O00O0O0OO0O0 =OOOO0O00000O0000O [:,:,1 ]>O0OOO0OOO0OOOO0OO [0 ]-side #line:501
        O0O0OOO00OOO0OO00 =OOOO0O00000O0000O [:,:,1 ]<OO0O0O00OO00O00OO [0 ]+side #line:502
        OO0O0OOOO0O0000OO =OOOO0O0O00000O0O0 *OO000O0000OO0OOOO *O0O00O00O0O0OO0O0 *O0O0OOO00OOO0OO00 #line:503
        OO0O0OOOO0O0000OO =np .sum (OO0O0OOOO0O0000OO ,axis =1 )#line:504
        OOOO0O00000O0000O =OOOO0O00000O0000O [OO0O0OOOO0O0000OO ==3 ]#line:505
        OOOOO0OOO0OO0000O =OOOOO0OOO0OO0000O [OO0O0OOOO0O0000OO ==3 ]#line:506
        print (OOOO0O00000O0000O .shape )#line:507
        O00O0000000OO0O00 =O00O0000000OO0O00 [O0O000O00O000OO0O [:,2 ]<cut_height ]#line:510
        O0O000O00O000OO0O =O0O000O00O000OO0O [O0O000O00O000OO0O [:,2 ]<cut_height ]#line:511
        OO0O0OOOO0O0000OO =OOOO0O00000O0000O [:,:,2 ]<cut_height #line:513
        print (OO0O0OOOO0O0000OO .shape )#line:514
        OO0O0OOOO0O0000OO =np .sum (OO0O0OOOO0O0000OO ,axis =1 )#line:515
        OOOO0O00000O0000O =OOOO0O00000O0000O [OO0O0OOOO0O0000OO ==3 ]#line:516
        OOOOO0OOO0OO0000O =OOOOO0OOO0OO0000O [OO0O0OOOO0O0000OO ==3 ]#line:517
        print (OOOO0O00000O0000O .shape )#line:518
        O0OOO0OOO0OOOO0OO [1 ]-=np .min (O0O000O00O000OO0O [:,0 ])#line:521
        O0OOO0OOO0OOOO0OO [0 ]-=np .min (O0O000O00O000OO0O [:,1 ])#line:522
        OO0O0O00OO00O00OO [1 ]-=np .min (O0O000O00O000OO0O [:,0 ])#line:523
        OO0O0O00OO00O00OO [0 ]-=np .min (O0O000O00O000OO0O [:,1 ])#line:524
        OOOO0O00000O0000O [:,:,0 ]-=np .min (O0O000O00O000OO0O [:,0 ])#line:525
        OOOO0O00000O0000O [:,:,1 ]-=np .min (O0O000O00O000OO0O [:,1 ])#line:526
        O0O000O00O000OO0O [:,0 ]-=np .min (O0O000O00O000OO0O [:,0 ])#line:527
        O0O000O00O000OO0O [:,1 ]-=np .min (O0O000O00O000OO0O [:,1 ])#line:528
        print ('\n### 確認')#line:532
        OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 =ft .down_sample (O0O000O00O000OO0O ,O00O0000000OO0O00 ,20000 )#line:534
        if test :#line:535
            ft .showc (OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 ,'xy',O0OOO0OOO0OOOO0OO ,OO0O0O00OO00O00OO )#line:536
        print ('\n### 足の向き補正')#line:554
        try :#line:556
            O0O0O0OO0OO0O0O00 #line:557
            O000OO0O0OOO0O0O0 #line:558
            O0O0O000OOOO0O0OO #line:559
        except NameError :#line:560
            print ('\n### 前処理')#line:562
            OOO0O0000O000O000 =cl_class (window_size ,dot_size ,paper_short ,paper_long ,rate1 )#line:565
            O0O0O000OO00OO00O ,O000O0OOOOOOOO0OO =OOO0O0000O000O000 .window_zoom (OOOO0O00000O0000O ,OOOOO0OOO0OO0000O ,min_face_num =80000 )#line:567
            O0O0O000OO00OO00O =OOO0O0000O000O000 .put_text (O0O0O000OO00OO00O ,['1, Second-finger tip','2, Heel tip'],right =True )#line:570
            OO0O00000O000OOOO ='step3'#line:576
            cv2 .namedWindow (OO0O00000O000OOOO )#line:577
            OOOO0O0OOO0000O0O =2 #line:578
            OO000OOO0O0OO00OO =pl_class (OOOO0O0OOO0000O0O )#line:579
            cv2 .setMouseCallback (OO0O00000O000OOOO ,OOO0O0000O000O000 .onMouse ,[OO0O00000O000OOOO ,O0O0O000OO00OO00O ,OO000OOO0O0OO00OO ])#line:580
            cv2 .imshow (OO0O00000O000OOOO ,O0O0O000OO00OO00O )#line:581
            cv2 .waitKey ()#line:582
            print ('\n### 後処理')#line:585
            O0O0O0OO0OO0O0O00 =np .array (OOO0O0000O000O000 .p [0 ],float )/O000O0OOOOOOOO0OO #line:588
            print ('foot_tip = [{}, {}]'.format (O0O0O0OO0OO0O0O00 [0 ],O0O0O0OO0OO0O0O00 [1 ]))#line:589
            O000OO0O0OOO0O0O0 =np .array (OOO0O0000O000O000 .p [1 ],float )/O000O0OOOOOOOO0OO #line:592
            print ('heel_tip = [{}, {}]'.format (O000OO0O0OOO0O0O0 [0 ],O000OO0O0OOO0O0O0 [1 ]))#line:593
            O0O00OO0O00O00000 =math .atan2 (O000OO0O0OOO0O0O0 [1 ]-O0O0O0OO0OO0O0O00 [1 ],O000OO0O0OOO0O0O0 [0 ]-O0O0O0OO0OO0O0O00 [0 ])#line:596
            OOO000O00000O0OOO =math .degrees (O0O00OO0O00O00000 )#line:597
            O0O0O000OOOO0O0OO =OOO000O00000O0OOO -90 #line:599
            if O0O0O000OOOO0O0OO >180 :#line:601
                O0O0O000OOOO0O0OO =-360 +O0O0O000OOOO0O0OO #line:602
            if O0O0O000OOOO0O0OO <-180 :#line:603
                O0O0O000OOOO0O0OO =360 -O0O0O000OOOO0O0OO #line:604
            print ('rotation_foot = {}'.format (O0O0O000OOOO0O0OO ))#line:605
        print ('\n### 反映')#line:609
        O0O0O0OO0OO0O0O00 =ft .rotate_2D_z (O0O0O0OO0OO0O0O00 ,theta =O0O0O000OOOO0O0OO )#line:612
        O000OO0O0OOO0O0O0 =ft .rotate_2D_z (O000OO0O0OOO0O0O0 ,theta =O0O0O000OOOO0O0OO )#line:613
        O0O000O00O000OO0O =ft .rotate_3D_z (O0O000O00O000OO0O ,theta =O0O0O000OOOO0O0OO )#line:614
        for OOOO00OO0OO0OOOOO in range (3 ):#line:615
            OOOO0O00000O0000O [:,OOOO00OO0OO0OOOOO ,:]=ft .rotate_3D_z (OOOO0O00000O0000O [:,OOOO00OO0OO0OOOOO ,:],theta =O0O0O000OOOO0O0OO )#line:616
        O0O0O0OO0OO0O0O00 [1 ]-=np .min (O0O000O00O000OO0O [:,0 ])#line:620
        O0O0O0OO0OO0O0O00 [0 ]-=np .min (O0O000O00O000OO0O [:,1 ])#line:621
        O000OO0O0OOO0O0O0 [1 ]-=np .min (O0O000O00O000OO0O [:,0 ])#line:622
        O000OO0O0OOO0O0O0 [0 ]-=np .min (O0O000O00O000OO0O [:,1 ])#line:623
        OOOO0O00000O0000O [:,:,0 ]-=np .min (O0O000O00O000OO0O [:,0 ])#line:624
        OOOO0O00000O0000O [:,:,1 ]-=np .min (O0O000O00O000OO0O [:,1 ])#line:625
        O0O000O00O000OO0O [:,0 ]-=np .min (O0O000O00O000OO0O [:,0 ])#line:626
        O0O000O00O000OO0O [:,1 ]-=np .min (O0O000O00O000OO0O [:,1 ])#line:627
        print ('\n### 確認')#line:631
        OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 =ft .down_sample (O0O000O00O000OO0O ,O00O0000000OO0O00 ,20000 )#line:633
        if test :#line:634
            ft .showc (OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 ,'xy',O0O0O0OO0OO0O0O00 ,O000OO0O0OOO0O0O0 )#line:635
        print ('\n### 足の測定１')#line:654
        try :#line:656
            O0O0OOO000O0OO00O #line:657
            O00OO000OO0000OO0 #line:658
            OO0O0O0OOOO0O0O0O #line:659
            OOO00O0OOOO000OOO #line:660
            O0OO000O0O000O0O0 #line:661
            OOOOO0OOO0OOOO0OO #line:662
            O0O0OO0OO00O00OO0 #line:663
            O00O00O0000O0O0OO #line:664
            OOO00O0OO0OO000O0 #line:665
        except NameError :#line:666
            print ('\n### 前処理')#line:668
            OOO0O0000O000O000 =cl_class (window_size ,dot_size ,paper_short ,paper_long ,rate1 )#line:671
            O0O0O000OO00OO00O ,O000O0OOOOOOOO0OO =OOO0O0000O000O000 .window_zoom (OOOO0O00000O0000O ,OOOOO0OOO0OO0000O ,min_face_num =80000 )#line:673
            O0O0O000OO00OO00O =OOO0O0000O000O000 .put_text (O0O0O000OO00OO00O ,['1, Toe tip','2, Heel tip','3, Heel-left','4, Heel-right','5, Width-left','6, Width-right'],right =True )#line:680
            OO0O00000O000OOOO ='step4'#line:686
            cv2 .namedWindow (OO0O00000O000OOOO )#line:687
            OOOO0O0OOO0000O0O =6 #line:688
            OO000OOO0O0OO00OO =pl_class (OOOO0O0OOO0000O0O )#line:689
            cv2 .setMouseCallback (OO0O00000O000OOOO ,OOO0O0000O000O000 .onMouse ,[OO0O00000O000OOOO ,O0O0O000OO00OO00O ,OO000OOO0O0OO00OO ])#line:690
            cv2 .imshow (OO0O00000O000OOOO ,O0O0O000OO00OO00O )#line:691
            cv2 .waitKey ()#line:692
            print ('\n### 後処理')#line:695
            O0000OO0O000O0OOO ,O00OOO0000O000OO0 =OOO0O0000O000O000 .p [0 ]/O000O0OOOOOOOO0OO #line:698
            O0OOO0O000OO0O0O0 ,O00OOO0OO00000OO0 =OOO0O0000O000O000 .p [1 ]/O000O0OOOOOOOO0OO #line:699
            OOOO0000OO000OO0O ,OO0OOO0OO00O00OOO =OOO0O0000O000O000 .p [2 ]/O000O0OOOOOOOO0OO #line:700
            OO00OOO0OOO00OOOO ,O0O0000OO0O00OOO0 =OOO0O0000O000O000 .p [3 ]/O000O0OOOOOOOO0OO #line:701
            O0OO0OOO00O000O0O ,OO000O00O0O0000OO =OOO0O0000O000O000 .p [4 ]/O000O0OOOOOOOO0OO #line:702
            OO0O00OO00OOO00OO ,O0OO0O0O0O00O0OO0 =OOO0O0000O000O000 .p [5 ]/O000O0OOOOOOOO0OO #line:703
            O0O0OOO000O0OO00O =abs (O00OOO0OO00000OO0 -O00OOO0000O000OO0 )#line:706
            print ('l_foot = {}'.format (O0O0OOO000O0OO00O ))#line:707
            O00OO000OO0000OO0 =abs (OO00OOO0OOO00OOOO -OOOO0000OO000OO0O )#line:709
            print ('w_heel = {}'.format (O00OO000OO0000OO0 ))#line:710
            OO0O0O0OOOO0O0O0O =((OO0O00OO00OOO00OO -O0OO0OOO00O000O0O )**2 +(O0OO0O0O0O00O0OO0 -OO000O00O0O0000OO )**2 )**0.5 #line:712
            print ('w_foot = {}'.format (OO0O0O0OOOO0O0O0O ))#line:713
            OOO00O0OOOO000OOO =[O0OO0OOO00O000O0O ,OO000O00O0O0000OO ]#line:715
            O0OO000O0O000O0O0 =[OO0O00OO00OOO00OO ,O0OO0O0O0O00O0OO0 ]#line:716
            print ('w_point1 = [{}, {}]'.format (OOO00O0OOOO000OOO [0 ],OOO00O0OOOO000OOO [1 ]))#line:717
            print ('w_point2 = [{}, {}]'.format (O0OO000O0O000O0O0 [0 ],O0OO000O0O000O0O0 [1 ]))#line:718
            OOOOO0OOO0OOOO0OO =abs (O00OOO0OO00000OO0 -OO000O00O0O0000OO )#line:720
            O0O0OO0OO00O00OO0 =abs (O00OOO0OO00000OO0 -O0OO0O0O0O00O0OO0 )#line:721
            print ('w_level_left = {}'.format (OOOOO0OOO0OOOO0OO ))#line:722
            print ('w_level_right = {}'.format (O0O0OO0OO00O00OO0 ))#line:723
            O00O00O0000O0O0OO =abs (O000OO0O0OOO0O0O0 [0 ]-O0OO0OOO00O000O0O )#line:725
            OOO00O0OO0OO000O0 =abs (OO0O00OO00OOO00OO -O000OO0O0OOO0O0O0 [0 ])#line:726
            print ('w_len_left = {}'.format (O00O00O0000O0O0OO ))#line:727
            print ('w_len_right = {}'.format (OOO00O0OO0OO000O0 ))#line:728
        print ('\n### 確認')#line:731
        OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 =ft .down_sample (O0O000O00O000OO0O ,O00O0000000OO0O00 ,20000 )#line:733
        if test :#line:734
            ft .showc (OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 ,'xy',O0O0O0OO0OO0O0O00 ,O000OO0O0OOO0O0O0 ,OOO00O0OOOO000OOO ,O0OO000O0O000O0O0 )#line:735
        print ('\n### 足囲の取り出し')#line:748
        O00O00O0O0O0OOOO0 =deepcopy (O0O000O00O000OO0O )#line:751
        O00O0OO0OOO00OO0O =deepcopy (O00O0000000OO0O00 )#line:752
        O0O00OO0O00O00000 =math .atan2 (O0OO000O0O000O0O0 [0 ]-OOO00O0OOOO000OOO [0 ],O0OO000O0O000O0O0 [1 ]-OOO00O0OOOO000OOO [1 ])#line:755
        OOO000O00000O0OOO =math .degrees (O0O00OO0O00O00000 )#line:756
        OOOO0O0O00O000O00 =90 -OOO000O00000O0OOO #line:758
        if OOOO0O0O00O000O00 >180 :#line:760
            OOOO0O0O00O000O00 =-360 +OOOO0O0O00O000O00 #line:761
        if OOOO0O0O00O000O00 <-180 :#line:762
            OOOO0O0O00O000O00 =360 -OOOO0O0O00O000O00 #line:763
        OOO00O0OOOO000OOO =ft .rotate_2D_z (OOO00O0OOOO000OOO ,theta =OOOO0O0O00O000O00 )#line:767
        O0OO000O0O000O0O0 =ft .rotate_2D_z (O0OO000O0O000O0O0 ,theta =OOOO0O0O00O000O00 )#line:768
        O00O00O0O0O0OOOO0 =ft .rotate_3D_z (O00O00O0O0O0OOOO0 ,theta =OOOO0O0O00O000O00 )#line:769
        OOO00O0OOO0000000 =(O00O00O0O0O0OOOO0 [:,0 ]>OOO00O0OOOO000OOO [1 ]-3 )*(O00O00O0O0O0OOOO0 [:,0 ]<OOO00O0OOOO000OOO [1 ]+3 )#line:772
        O00O00O0O0O0OOOO0 =O00O00O0O0O0OOOO0 [OOO00O0OOO0000000 ]#line:773
        O00O0OO0OOO00OO0O =O00O0OO0OOO00OO0O [OOO00O0OOO0000000 ]#line:774
        OOO00O0OOOO000OOO [1 ]-=np .min (O00O00O0O0O0OOOO0 [:,0 ])#line:777
        OOO00O0OOOO000OOO [0 ]-=np .min (O00O00O0O0O0OOOO0 [:,1 ])#line:778
        O0OO000O0O000O0O0 [1 ]-=np .min (O00O00O0O0O0OOOO0 [:,0 ])#line:779
        O0OO000O0O000O0O0 [0 ]-=np .min (O00O00O0O0O0OOOO0 [:,1 ])#line:780
        O00O00O0O0O0OOOO0 [:,0 ]-=np .min (O00O00O0O0O0OOOO0 [:,0 ])#line:781
        O00O00O0O0O0OOOO0 [:,1 ]-=np .min (O00O00O0O0O0OOOO0 [:,1 ])#line:782
        if test :#line:784
            ft .showc (O00O00O0O0O0OOOO0 ,O00O0OO0OOO00OO0O ,'xy',OOO00O0OOOO000OOO ,O0OO000O0O000O0O0 )#line:785
        print ('\n### 足囲')#line:789
        try :#line:791
            O00O0OOOOOO000000 #line:792
        except NameError :#line:793
            print ('\n### ダウンサンプル')#line:795
            OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 =ft .down_sample (O00O00O0O0O0OOOO0 ,O00O0OO0OOO00OO0O ,200000 )#line:797
            print ('\n### 前処理')#line:800
            OOO0O0000O000O000 =cl_class (window_size ,dot_size ,paper_short ,paper_long ,rate1 )#line:803
            O0O0O000OO00OO00O ,O000O0OOOOOOOO0OO =OOO0O0000O000O000 .window_zoom_back (OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 ,OOO00O0OOOO000OOO [0 ],O0OO000O0O000O0O0 [0 ])#line:805
            O0O0O000OO00OO00O =OOO0O0000O000O000 .put_text (O0O0O000OO00OO00O ,['1, Connect foot circumference','2, End before reach start point'])#line:809
            cv2 .rectangle (O0O0O000OO00OO00O ,(0 ,window_size *2 //3 ),(window_size ,window_size ),(64 ,64 ,64 ),thickness =-1 )#line:811
            cv2 .putText (O0O0O000OO00OO00O ,'Click to END & AUTO connect to start point',(0 ,window_size ),cv2 .FONT_HERSHEY_PLAIN ,1.5 ,(255 ,255 ,255 ),1 )#line:812
            OO0O00000O000OOOO ='step5'#line:818
            cv2 .namedWindow (OO0O00000O000OOOO )#line:819
            OOOO0O0OOO0000O0O =200 #line:820
            OO000OOO0O0OO00OO =pl_class (OOOO0O0OOO0000O0O )#line:821
            cv2 .setMouseCallback (OO0O00000O000OOOO ,OOO0O0000O000O000 .onMouse ,[OO0O00000O000OOOO ,O0O0O000OO00OO00O ,OO000OOO0O0OO00OO ])#line:822
            cv2 .imshow (OO0O00000O000OOOO ,O0O0O000OO00OO00O )#line:823
            cv2 .waitKey ()#line:824
            print ('\n### 後処理')#line:827
            O0O00OO000O0000O0 =OOO0O0000O000O000 .p /O000O0OOOOOOOO0OO #line:830
            print (O0O00OO000O0000O0 )#line:831
            O00O0OOOOOO000000 =((O0O00OO000O0000O0 [0 ,0 ]-O0O00OO000O0000O0 [-1 ,0 ])**2 +(O0O00OO000O0000O0 [0 ,1 ]-O0O00OO000O0000O0 [-1 ,1 ])**2 )**0.5 #line:833
            for OOOO00OO0OO0OOOOO in range (1 ,len (O0O00OO000O0000O0 )):#line:836
                O00O0OOOOOO000000 +=((O0O00OO000O0000O0 [OOOO00OO0OO0OOOOO ,0 ]-O0O00OO000O0000O0 [OOOO00OO0OO0OOOOO -1 ,0 ])**2 +(O0O00OO000O0000O0 [OOOO00OO0OO0OOOOO ,1 ]-O0O00OO000O0000O0 [OOOO00OO0OO0OOOOO -1 ,1 ])**2 )**0.5 #line:837
            print ('c_foot = {}'.format (O00O0OOOOOO000000 ))#line:839
        O00O0OO00OO0000OO =O000OO0O0OOO0O0O0 [1 ]-O0O0OOO000O0OO00O #line:854
        OOO0O000O0000OO00 =O000OO0O0OOO0O0O0 [1 ]#line:855
        OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 =ft .down_sample (O0O000O00O000OO0O ,O00O0000000OO0O00 ,20000 )#line:856
        if test :#line:857
            ft .showc (OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 ,'xy',[0 ,O00O0OO00OO0000OO ],[0 ,OOO0O000O0000OO00 ])#line:858
        print ('\n### ガースポイント')#line:863
        try :#line:865
            OOO000O000OOO0000 #line:866
            OOO0OOO0OO00O0O0O #line:867
        except NameError :#line:868
            print ('\n### ダウンサンプル')#line:870
            print ('\n### 前処理')#line:875
            OOO0O0000O000O000 =cl_class (window_size ,dot_size ,paper_short ,paper_long ,rate1 )#line:878
            O0O0O000OO00OO00O ,O000O0OOOOOOOO0OO =OOO0O0000O000O000 .window_zoom_side (OOOO0O00000O0000O ,OOOOO0OOO0OO0000O ,min_face_num =80000 ,z_sort_rev =(OOOOO0OOO0OOOO0OO <O0O0OO0OO00O00OO0 ))#line:881
            OOOO0000OO000OO0O =int ((OOO0O000O0000OO00 *rate2 +O00O0OO00OO0000OO *(1 -rate2 ))*O000O0OOOOOOOO0OO )#line:885
            OO00OOO0OOO00OOOO =int ((OOO0O000O0000OO00 *rate3 +O00O0OO00OO0000OO *(1 -rate3 ))*O000O0OOOOOOOO0OO )#line:886
            cv2 .line (O0O0O000OO00OO00O ,(OOOO0000OO000OO0O ,0 ),(OOOO0000OO000OO0O ,window_size ),(255 ,255 ,0 ))#line:887
            cv2 .line (O0O0O000OO00OO00O ,(OO00OOO0OOO00OOOO ,0 ),(OO00OOO0OOO00OOOO ,window_size ),(255 ,254 ,0 ))#line:888
            O0O0O000OO00OO00O =OOO0O0000O000O000 .put_text (O0O0O000OO00OO00O ,['1, Heel girth front','2, Heel girth back','*Reversed image if right foot'])#line:893
            OO0O00000O000OOOO ='step6'#line:899
            cv2 .namedWindow (OO0O00000O000OOOO )#line:900
            OOOO0O0OOO0000O0O =1 #line:901
            OO000OOO0O0OO00OO =pl_class (OOOO0O0OOO0000O0O )#line:902
            cv2 .setMouseCallback (OO0O00000O000OOOO ,OOO0O0000O000O000 .onMouse ,[OO0O00000O000OOOO ,O0O0O000OO00OO00O ,OO000OOO0O0OO00OO ])#line:903
            cv2 .imshow (OO0O00000O000OOOO ,O0O0O000OO00OO00O )#line:904
            cv2 .waitKey ()#line:905
            print ('\n### 後処理')#line:908
            OOO000O000OOO0000 =np .array ([OOOO0000OO000OO0O ,OOO0O0000O000O000 .p [0 ,1 ]])#line:911
            OOO0OOO0OO00O0O0O =np .array ([OO00OOO0OOO00OOOO ,window_size //2 ])#line:912
            print (OOO000O000OOO0000 ,OOO0OOO0OO00O0O0O )#line:913
            OOO000O000OOO0000 [0 ]/=O000O0OOOOOOOO0OO #line:916
            OOO000O000OOO0000 [1 ]=-(OOO000O000OOO0000 [1 ]-window_size //2 )/O000O0OOOOOOOO0OO #line:917
            OOO0OOO0OO00O0O0O [0 ]/=O000O0OOOOOOOO0OO #line:918
            OOO0OOO0OO00O0O0O [1 ]=-(OOO0OOO0OO00O0O0O [1 ]-window_size //2 )/O000O0OOOOOOOO0OO #line:919
            print ('g_point1 = [{}, {}] #x,z'.format (OOO000O000OOO0000 [0 ],OOO000O000OOO0000 [1 ]))#line:920
            print ('g_point2 = [{}, {}] #x,z'.format (OOO0OOO0OO00O0O0O [0 ],OOO0OOO0OO00O0O0O [1 ]))#line:921
        O0OO000OO0O00OO00 =OOO000O000OOO0000 [1 ]#line:924
        print ('g_step_height = {}'.format (O0OO000OO0O00OO00 ))#line:925
        print ('\n### 確認')#line:928
        OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 =ft .down_sample (O0O000O00O000OO0O ,O00O0000000OO0O00 ,20000 )#line:930
        if test :#line:931
            ft .showc (OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 ,'xz',[OOO000O000OOO0000 [1 ],OOO000O000OOO0000 [0 ]],[OOO0OOO0OO00O0O0O [1 ],OOO0OOO0OO00O0O0O [0 ]])#line:932
        print ('\n### ガースの取り出し')#line:946
        O00O00O0O0O0OOOO0 =deepcopy (O0O000O00O000OO0O )#line:949
        O00O0OO0OOO00OO0O =deepcopy (O00O0000000OO0O00 )#line:950
        O0O00OO0O00O00000 =math .atan2 (OOO0OOO0OO00O0O0O [1 ]-OOO000O000OOO0000 [1 ],OOO0OOO0OO00O0O0O [0 ]-OOO000O000OOO0000 [0 ])#line:953
        OOO000O00000O0OOO =math .degrees (O0O00OO0O00O00000 )#line:954
        OO00OOO0O0OO00OO0 =90 +OOO000O00000O0OOO #line:956
        if OO00OOO0O0OO00OO0 >180 :#line:958
            OO00OOO0O0OO00OO0 =-360 +OO00OOO0O0OO00OO0 #line:959
        if OO00OOO0O0OO00OO0 <-180 :#line:960
            OO00OOO0O0OO00OO0 =360 -OO00OOO0O0OO00OO0 #line:961
        OOO000O000OOO0000 =ft .rotate_2D_z (OOO000O000OOO0000 ,theta =OO00OOO0O0OO00OO0 )#line:965
        OOO0OOO0OO00O0O0O =ft .rotate_2D_z (OOO0OOO0OO00O0O0O ,theta =OO00OOO0O0OO00OO0 )#line:966
        O00O00O0O0O0OOOO0 =ft .rotate_3D_y (O00O00O0O0O0OOOO0 ,theta =OO00OOO0O0OO00OO0 )#line:967
        OO0OO0O0O0OO0OO0O =(O00O00O0O0O0OOOO0 [:,0 ]>OOO000O000OOO0000 [0 ]-3 )*(O00O00O0O0O0OOOO0 [:,0 ]<OOO0OOO0OO00O0O0O [0 ]+3 )#line:970
        O00O00O0O0O0OOOO0 =O00O00O0O0O0OOOO0 [OO0OO0O0O0OO0OO0O ]#line:971
        O00O0OO0OOO00OO0O =O00O0OO0OOO00OO0O [OO0OO0O0O0OO0OO0O ]#line:972
        O00O00O0O0O0OOOO0 [:,2 ]-=OOO0OOO0OO00O0O0O [1 ]#line:975
        OOO000O000OOO0000 [1 ]-=OOO0OOO0OO00O0O0O [1 ]#line:976
        OOO0OOO0OO00O0O0O [1 ]-=OOO0OOO0OO00O0O0O [1 ]#line:977
        if test :#line:979
            ft .showc (O00O00O0O0O0OOOO0 ,O00O0OO0OOO00OO0O ,'xz',[OOO000O000OOO0000 [1 ],OOO000O000OOO0000 [0 ]],[OOO0OOO0OO00O0O0O [1 ],OOO0OOO0OO00O0O0O [0 ]])#line:980
            ft .showc (O00O00O0O0O0OOOO0 ,O00O0OO0OOO00OO0O ,'xy')#line:981
        print ('\n### ガース')#line:988
        try :#line:990
            OO0OO0OOOO00OOO0O #line:991
        except NameError :#line:992
            print ('\n### ダウンサンプル')#line:994
            OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 =ft .down_sample (O00O00O0O0O0OOOO0 ,O00O0OO0OOO00OO0O ,200000 )#line:996
            print ('\n### 前処理')#line:999
            OOO0O0000O000O000 =cl_class (window_size ,dot_size ,paper_short ,paper_long ,rate1 )#line:1002
            O0O0O000OO00OO00O ,O000O0OOOOOOOO0OO =OOO0O0000O000O000 .window_zoom_back (OO000O00O0O0OOOO0 ,O00O0O0O0OOO0OO00 ,0 ,0 )#line:1004
            O0O0O000OO00OO00O =OOO0O0000O000O000 .put_text (O0O0O000OO00OO00O ,['1, Connect girth','2, End before reach start point'])#line:1008
            cv2 .rectangle (O0O0O000OO00OO00O ,(0 ,window_size *2 //3 ),(window_size ,window_size ),(64 ,64 ,64 ),thickness =-1 )#line:1010
            cv2 .putText (O0O0O000OO00OO00O ,'Click to END & AUTO connect to start point',(0 ,window_size ),cv2 .FONT_HERSHEY_PLAIN ,1.5 ,(255 ,255 ,255 ),1 )#line:1011
            OO0O00000O000OOOO ='step7'#line:1017
            cv2 .namedWindow (OO0O00000O000OOOO )#line:1018
            OOOO0O0OOO0000O0O =200 #line:1019
            OO000OOO0O0OO00OO =pl_class (OOOO0O0OOO0000O0O )#line:1020
            cv2 .setMouseCallback (OO0O00000O000OOOO ,OOO0O0000O000O000 .onMouse ,[OO0O00000O000OOOO ,O0O0O000OO00OO00O ,OO000OOO0O0OO00OO ])#line:1021
            cv2 .imshow (OO0O00000O000OOOO ,O0O0O000OO00OO00O )#line:1022
            cv2 .waitKey ()#line:1023
            print ('\n### 後処理')#line:1026
            O0O00OO000O0000O0 =OOO0O0000O000O000 .p /O000O0OOOOOOOO0OO #line:1029
            print (O0O00OO000O0000O0 )#line:1030
            OO0OO0OOOO00OOO0O =((O0O00OO000O0000O0 [0 ,0 ]-O0O00OO000O0000O0 [-1 ,0 ])**2 +(O0O00OO000O0000O0 [0 ,1 ]-O0O00OO000O0000O0 [-1 ,1 ])**2 )**0.5 #line:1032
            for OOOO00OO0OO0OOOOO in range (1 ,len (O0O00OO000O0000O0 )):#line:1035
                OO0OO0OOOO00OOO0O +=((O0O00OO000O0000O0 [OOOO00OO0OO0OOOOO ,0 ]-O0O00OO000O0000O0 [OOOO00OO0OO0OOOOO -1 ,0 ])**2 +(O0O00OO000O0000O0 [OOOO00OO0OO0OOOOO ,1 ]-O0O00OO000O0000O0 [OOOO00OO0OO0OOOOO -1 ,1 ])**2 )**0.5 #line:1036
            print ('g_step = {}'.format (OO0OO0OOOO00OOO0O ))#line:1038
        O00O0OO000O00O0OO =['l_foot','w_heel','w_foot','w_len_left','w_len_right','w_len_sum','w_level_left','w_level_right','c_foot','g_step_height','g_step']#line:1052
        OOO000OO0OO00O00O =[round (O0O0OOO000O0OO00O ,1 ),round (O00OO000OO0000OO0 ,1 ),round (OO0O0O0OOOO0O0O0O ,1 ),round (O00O00O0000O0O0OO ,1 ),round (OOO00O0OO0OO000O0 ,1 ),round (O00O00O0000O0O0OO +OOO00O0OO0OO000O0 ,1 ),round (OOOOO0OOO0OOOO0OO ,1 ),round (O0O0OO0OO00O00OO0 ,1 ),round (O00O0OOOOOO000000 ,1 ),round (O0OO000OO0O00OO00 ,1 ),round (OO0OO0OOOO00OOO0O ,1 )]#line:1063
        return O00O0OO000O00O0OO ,OOO000OO0OO00O00O #line:1065
if __name__ =='__main__':#line:1080
    file ='../test/隙間検証/cagiana_20220228_L.pckl'#line:1100
    paper_long =297 #line:1103
    paper_short =210 #line:1104
    window_size =1200 #line:1106
    dot_size =1 #line:1108
    cut_height =90 #line:1110
    rate1 =0.18 #line:1112
    rate2 =0.44 #line:1114
    rate3 =0.54 #line:1115
    side =30 #line:1117
    test =1 #line:1119
    names ,values =vcfoot ().enkaku (file ,paper_long =paper_long ,paper_short =paper_short ,window_size =window_size ,dot_size =dot_size ,cut_height =cut_height ,rate1 =rate1 ,rate2 =rate2 ,rate3 =rate3 ,side =side ,test =test )#line:1130
    print (names )#line:1133
    print (values )#line:1134
