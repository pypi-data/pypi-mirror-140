import os ,math ,time ,cv2 #line:2
import numpy as np #line:4
import pickle #line:5
import urllib .request #line:6
import urllib .parse #line:7
from PIL import Image #line:8
import matplotlib .pyplot as plt #line:9
np .set_printoptions (threshold =np .inf ,precision =8 ,suppress =True ,floatmode ='maxprec')#line:11
file ='https://shoe-craft-terminal.s3.ap-northeast-1.amazonaws.com/サンプル太郎/sample.pckl'#line:15
s_quote =urllib .parse .quote (file )#line:16
print (s_quote )#line:17
class ft :#line:19
    def __init__ (OO0OOOO00O0000O0O ):#line:20
        pass #line:21
    def __del__ (O0000O00O0OO0OO00 ):#line:22
        pass #line:23
    def load_obj (O00O0000O00OOOO0O ):#line:26
        print ('file:\n{}'.format (O00O0000O00OOOO0O ))#line:27
        OOO000OOO0OO0OO0O =[]#line:29
        O0OOOOOOO00OO0OO0 =[]#line:30
        O0000OOOOOO00O00O =[]#line:31
        with open (O00O0000O00OOOO0O ,"r")as OO0OOOO00O0O0000O :#line:32
            for OOO00OOO00000000O in OO0OOOO00O0O0000O :#line:33
                O0000OO0000OO00O0 =OOO00OOO00000000O .split ()#line:34
                if len (O0000OO0000OO00O0 )==0 :#line:36
                    continue #line:37
                if O0000OO0000OO00O0 [0 ]=='v':#line:38
                    OO0OO00OOOO0O0OOO =list (map (float ,O0000OO0000OO00O0 [1 :4 ]))#line:40
                    OOO000OOO0OO0OO0O .append (OO0OO00OOOO0O0OOO )#line:41
                    if len (O0000OO0000OO00O0 )==7 :#line:42
                        O0O00O0000OO0O0O0 =list (map (float ,O0000OO0000OO00O0 [4 :7 ]))#line:44
                        O0OOOOOOO00OO0OO0 .append (O0O00O0000OO0O0O0 )#line:45
                if O0000OO0000OO00O0 [0 ]=='f':#line:46
                    O0OOO0O0O0OOO00OO =list (map (int ,O0000OO0000OO00O0 [1 :4 ]))#line:48
                    O0000OOOOOO00O00O .append (O0OOO0O0O0OOO00OO )#line:49
        OOO000OOO0OO0OO0O =np .array (OOO000OOO0OO0OO0O )#line:50
        O0OOOOOOO00OO0OO0 =np .array (O0OOOOOOO00OO0OO0 )#line:51
        O0000OOOOOO00O00O =np .array (O0000OOOOOO00O00O ,int )#line:52
        print ('vertices.shape:\n{}'.format (OOO000OOO0OO0OO0O .shape ))#line:53
        print ('vertexColors.shape:\n{}'.format (O0OOOOOOO00OO0OO0 .shape ))#line:54
        print ('faces.shape:\n{}'.format (O0000OOOOOO00O00O .shape ))#line:55
        return OOO000OOO0OO0OO0O ,O0OOOOOOO00OO0OO0 ,O0000OOOOOO00O00O #line:56
    def load_pckl (OOO0000O00000OOO0 ):#line:60
        print ('file:\n{}'.format (OOO0000O00000OOO0 ))#line:61
        with open (OOO0000O00000OOO0 ,'rb')as O0OO0OO00O0O0OOOO :#line:62
            O0O000OOOO0OO0OO0 ,OOO0OOOOO000OOO0O ,O0O00OOO000000O0O =pickle .load (O0OO0OO00O0O0OOOO )#line:63
        print ('vertices.shape:\n{}'.format (O0O000OOOO0OO0OO0 .shape ))#line:65
        print ('vertexColors.shape:\n{}'.format (OOO0OOOOO000OOO0O .shape ))#line:66
        print ('faces.shape:\n{}'.format (O0O00OOO000000O0O .shape ))#line:67
        return O0O000OOOO0OO0OO0 ,OOO0OOOOO000OOO0O ,O0O00OOO000000O0O #line:68
    def load_pckl_url (O000OOOOO0OOO0O00 ):#line:71
        print ('load from cloud')#line:72
        O0O0O00O0O0000OOO =O000OOOOO0OOO0O00 .split ('//')[1 ]#line:74
        O0O0O00O0O0000OOO =urllib .parse .quote (O0O0O00O0O0000OOO )#line:75
        O000OOOOO0OOO0O00 =O000OOOOO0OOO0O00 .split ('//')[0 ]+'//'+O0O0O00O0O0000OOO #line:76
        OO00O0O0OOOO00OO0 =urllib .request .Request (O000OOOOO0OOO0O00 )#line:78
        with urllib .request .urlopen (OO00O0O0OOOO00OO0 )as O0OO0OOOO00O00000 :#line:79
            O00OO0O00OOO0O000 ,OO0OO0OOO000O0O00 ,OO0O000O00O000OOO =pickle .load (O0OO0OOOO00O00000 )#line:80
        print ('vertices.shape:\n{}'.format (O00OO0O00OOO0O000 .shape ))#line:82
        print ('vertexColors.shape:\n{}'.format (OO0OO0OOO000O0O00 .shape ))#line:83
        print ('faces.shape:\n{}'.format (OO0O000O00O000OOO .shape ))#line:84
        return O00OO0O00OOO0O000 ,OO0OO0OOO000O0O00 ,OO0O000O00O000OOO #line:85
    def down_sample (O0O0O0O0OO00OO0O0 ,OO0OOO0OOO0O00O0O ,O0OOOO00OO0000OO0 ):#line:101
        print ('v.shape:\n{} -> '.format (O0O0O0O0OO00OO0O0 .shape ),end ='')#line:102
        if len (O0O0O0O0OO00OO0O0 )>O0OOOO00OO0000OO0 :#line:103
            O0O0O0O0OO00OO0O0 =O0O0O0O0OO00OO0O0 [::len (O0O0O0O0OO00OO0O0 )//O0OOOO00OO0000OO0 ][:O0OOOO00OO0000OO0 ]#line:104
            OO0OOO0OOO0O00O0O =OO0OOO0OOO0O00O0O [::len (OO0OOO0OOO0O00O0O )//O0OOOO00OO0000OO0 ][:O0OOOO00OO0000OO0 ]#line:105
        print ('{}'.format (O0O0O0O0OO00OO0O0 .shape ))#line:106
        return O0O0O0O0OO00OO0O0 ,OO0OOO0OOO0O00O0O #line:107
    def rotate_3D_x (O0O0OO000O0OOOOOO ,theta =0 ):#line:112
        OO0OOOOO000OOOOOO =-theta /57.2958 #line:113
        OO0OO0O00O00O0OOO =np .array ([[1 ,0 ,0 ],[0 ,np .cos (OO0OOOOO000OOOOOO ),-np .sin (OO0OOOOO000OOOOOO )],[0 ,np .sin (OO0OOOOO000OOOOOO ),np .cos (OO0OOOOO000OOOOOO )]])#line:117
        return np .dot (O0O0OO000O0OOOOOO ,OO0OO0O00O00O0OOO )#line:118
    def rotate_3D_y (O0O00OO00OO000OOO ,theta =0 ):#line:120
        OO0OO00OO0OO0O0O0 =-theta /57.2958 #line:121
        O0OOO0O00OO000OOO =np .array ([[np .cos (OO0OO00OO0OO0O0O0 ),0 ,np .sin (OO0OO00OO0OO0O0O0 )],[0 ,1 ,0 ],[-np .sin (OO0OO00OO0OO0O0O0 ),0 ,np .cos (OO0OO00OO0OO0O0O0 )]])#line:125
        return np .dot (O0O00OO00OO000OOO ,O0OOO0O00OO000OOO )#line:126
    def rotate_3D_z (O0O00OOO0OOOO0OOO ,theta =0 ):#line:128
        O00OOO00000000O00 =-theta /57.2958 #line:129
        OO0O0OO0OOO0O0OOO =np .array ([[np .cos (O00OOO00000000O00 ),-np .sin (O00OOO00000000O00 ),0 ],[np .sin (O00OOO00000000O00 ),np .cos (O00OOO00000000O00 ),0 ],[0 ,0 ,1 ]])#line:133
        return np .dot (O0O00OOO0OOOO0OOO ,OO0O0OO0OOO0O0OOO )#line:134
    def rotate_2D_z (OO0OOO000O0000OO0 ,theta =0 ):#line:137
        O0O0OO0O0O0OO0OOO =+theta /57.2958 #line:138
        OOOO00O0OO0O0O00O =np .array ([[np .cos (O0O0OO0O0O0OO0OOO ),-np .sin (O0O0OO0O0O0OO0OOO )],[np .sin (O0O0OO0O0O0OO0OOO ),np .cos (O0O0OO0O0O0OO0OOO )]])#line:141
        return np .dot (OO0OOO000O0000OO0 ,OOOO00O0OO0O0O00O )#line:142
    def show (O0O00O0O00000000O ,dim ='xy',*OO0000OO000OOO0O0 ,save =None ):#line:146
        plt .figure (figsize =(5 ,5 ))#line:147
        OO000O00O0O0OO0O0 ,OO00OO0O0O0000O0O ,O0000OO00OO0000OO =O0O00O0O00000000O [:,0 ],O0O00O0O00000000O [:,1 ],O0O00O0O00000000O [:,2 ]#line:149
        if dim =='xy':#line:150
            plt .scatter (OO000O00O0O0OO0O0 ,OO00OO0O0O0000O0O ,c ='k',s =2 )#line:151
        elif dim =='xz':#line:152
            plt .scatter (OO000O00O0O0OO0O0 ,O0000OO00OO0000OO ,c ='k',s =2 )#line:153
        elif dim =='yz':#line:154
            plt .scatter (OO00OO0O0O0000O0O ,O0000OO00OO0000OO ,c ='k',s =2 )#line:155
        plt .xlabel (dim [0 ]);plt .ylabel (dim [1 ])#line:157
        if len (OO0000OO000OOO0O0 )>0 :#line:159
            OO0000OO000OOO0O0 =np .array (OO0000OO000OOO0O0 )#line:160
            plt .plot (OO0000OO000OOO0O0 [:,0 ],OO0000OO000OOO0O0 [:,1 ],'ro',linewidth =1 )#line:161
        OO00OO0O0OOOOO0OO =np .max (np .array ([[np .max (OO000O00O0O0OO0O0 )-np .min (OO000O00O0O0OO0O0 )],[np .max (OO00OO0O0O0000O0O )-np .min (OO00OO0O0O0000O0O )],[np .max (O0000OO00OO0000OO )-np .min (O0000OO00OO0000OO )]]))#line:163
        if dim =='xy':#line:165
            plt .xlim (np .mean (OO000O00O0O0OO0O0 )-OO00OO0O0OOOOO0OO /1.8 ,np .mean (OO000O00O0O0OO0O0 )+OO00OO0O0OOOOO0OO /1.8 )#line:166
            plt .ylim (np .mean (OO00OO0O0O0000O0O )-OO00OO0O0OOOOO0OO /1.8 ,np .mean (OO00OO0O0O0000O0O )+OO00OO0O0OOOOO0OO /1.8 )#line:167
        elif dim =='xz':#line:168
            plt .xlim (np .mean (OO000O00O0O0OO0O0 )-OO00OO0O0OOOOO0OO /1.8 ,np .mean (OO000O00O0O0OO0O0 )+OO00OO0O0OOOOO0OO /1.8 )#line:169
            plt .ylim (np .mean (O0000OO00OO0000OO )-OO00OO0O0OOOOO0OO /1.8 ,np .mean (O0000OO00OO0000OO )+OO00OO0O0OOOOO0OO /1.8 )#line:170
        elif dim =='yz':#line:171
            plt .xlim (np .mean (OO00OO0O0O0000O0O )-OO00OO0O0OOOOO0OO /1.8 ,np .mean (OO00OO0O0O0000O0O )+OO00OO0O0OOOOO0OO /1.8 )#line:172
            plt .ylim (np .mean (O0000OO00OO0000OO )-OO00OO0O0OOOOO0OO /1.8 ,np .mean (O0000OO00OO0000OO )+OO00OO0O0OOOOO0OO /1.8 )#line:173
        if save !=None :#line:174
            plt .savefig (save )#line:175
        plt .show ()#line:176
        plt .close ()#line:177
    def showc (OO00O000000OO0000 ,OO0OO00O0OOO0O0O0 ,dim ='xy',*OOO000O0OO0OOO00O ,save =None ):#line:179
        plt .figure (figsize =(5 ,5 ))#line:180
        O0O0000OOO0OO00O0 ,OOOO000OOO0O00OOO ,OO0O0OO0OOO00000O =OO00O000000OO0000 [:,0 ],OO00O000000OO0000 [:,1 ],OO00O000000OO0000 [:,2 ]#line:182
        if dim =='xy':#line:183
            plt .scatter (O0O0000OOO0OO00O0 ,OOOO000OOO0O00OOO ,c =OO0OO00O0OOO0O0O0 /255.0 ,s =2 )#line:184
        elif dim =='xz':#line:185
            plt .scatter (O0O0000OOO0OO00O0 ,OO0O0OO0OOO00000O ,c =OO0OO00O0OOO0O0O0 /255.0 ,s =2 )#line:186
        elif dim =='yz':#line:187
            plt .scatter (OOOO000OOO0O00OOO ,OO0O0OO0OOO00000O ,c =OO0OO00O0OOO0O0O0 /255.0 ,s =2 )#line:188
        plt .xlabel (dim [0 ]);plt .ylabel (dim [1 ])#line:190
        if len (OOO000O0OO0OOO00O )>0 :#line:192
            OOO000O0OO0OOO00O =np .array (OOO000O0OO0OOO00O )#line:193
            plt .plot (OOO000O0OO0OOO00O [:,1 ],OOO000O0OO0OOO00O [:,0 ],'ro',linewidth =1 )#line:195
        O0OO00O00OOOO0OOO =np .max (np .array ([[np .max (O0O0000OOO0OO00O0 )-np .min (O0O0000OOO0OO00O0 )],[np .max (OOOO000OOO0O00OOO )-np .min (OOOO000OOO0O00OOO )],[np .max (OO0O0OO0OOO00000O )-np .min (OO0O0OO0OOO00000O )]]))#line:197
        if dim =='xy':#line:199
            plt .xlim (np .mean (O0O0000OOO0OO00O0 )-O0OO00O00OOOO0OOO /1.8 ,np .mean (O0O0000OOO0OO00O0 )+O0OO00O00OOOO0OOO /1.8 )#line:200
            plt .ylim (np .mean (OOOO000OOO0O00OOO )-O0OO00O00OOOO0OOO /1.8 ,np .mean (OOOO000OOO0O00OOO )+O0OO00O00OOOO0OOO /1.8 )#line:201
        elif dim =='xz':#line:202
            plt .xlim (np .mean (O0O0000OOO0OO00O0 )-O0OO00O00OOOO0OOO /1.8 ,np .mean (O0O0000OOO0OO00O0 )+O0OO00O00OOOO0OOO /1.8 )#line:203
            plt .ylim (np .mean (OO0O0OO0OOO00000O )-O0OO00O00OOOO0OOO /1.8 ,np .mean (OO0O0OO0OOO00000O )+O0OO00O00OOOO0OOO /1.8 )#line:204
        elif dim =='yz':#line:205
            plt .xlim (np .mean (OOOO000OOO0O00OOO )-O0OO00O00OOOO0OOO /1.8 ,np .mean (OOOO000OOO0O00OOO )+O0OO00O00OOOO0OOO /1.8 )#line:206
            plt .ylim (np .mean (OO0O0OO0OOO00000O )-O0OO00O00OOOO0OOO /1.8 ,np .mean (OO0O0OO0OOO00000O )+O0OO00O00OOOO0OOO /1.8 )#line:207
        if save !=None :#line:208
            plt .savefig (save )#line:209
        plt .show ()#line:210
        plt .close ()#line:211
class pl_class :#line:223
    def __init__ (OO0OOOOO0OO0O00O0 ,O0OOOO00OOO000000 ):#line:224
        OO0OOOOO0OO0O00O0 .npoints =O0OOOO00OOO000000 #line:225
        OO0OOOOO0OO0O00O0 .p =np .empty ((O0OOOO00OOO000000 ,2 ),dtype =int )#line:226
        OO0OOOOO0OO0O00O0 .count =0 #line:227
    def add (O00OO0O0O0000OO00 ,OOOO000000O0O00O0 ,O00OOOOOO000O0O0O ):#line:229
        O00OO0O0O0000OO00 .p [O00OO0O0O0000OO00 .count ,:]=[OOOO000000O0O00O0 ,O00OOOOOO000O0O0O ]#line:230
        O00OO0O0O0000OO00 .count +=1 #line:231
class cl_class :#line:234
    def __init__ (O0O0O000OO0O0OO0O ,O00O0OO0O0O00O000 ,O0O00O000O0000O0O ,OOOO0O000O0O0OO00 ,OOOOOOO0O000OOOO0 ,O0OOOO0O00O0O000O ):#line:235
        O0O0O000OO0O0OO0O .window_size =O00O0OO0O0O00O000 #line:236
        O0O0O000OO0O0OO0O .dot_size =O0O00O000O0000O0O #line:237
        O0O0O000OO0O0OO0O .h =O00O0OO0O0O00O000 #line:238
        O0O0O000OO0O0OO0O .w =O00O0OO0O0O00O000 #line:239
        O0O0O000OO0O0OO0O .paper_short =OOOO0O000O0O0OO00 #line:240
        O0O0O000OO0O0OO0O .paper_long =OOOOOOO0O000OOOO0 #line:241
        O0O0O000OO0O0OO0O .rate1 =O0OOOO0O00O0O000O #line:242
        O0O0O000OO0O0OO0O .p ='a'#line:243
        O0O0O000OO0O0OO0O .t =0 #line:244
        O0O0O000OO0O0OO0O .qqq1 =0 #line:245
        O0O0O000OO0O0OO0O .qqq2 =0 #line:246
    def __del__ (O00000O000O000OO0 ):#line:248
        pass #line:249
    def window_zoom (O00OO0O00OO0O000O ,O00OOO0OOO00OOO0O ,O0O0O0OOO0O0O0000 ,min_face_num =30000 ):#line:251
        OOO0O0O000OOO0000 =O00OOO0OOO00OOO0O [:,:,[1 ,0 ]]#line:253
        OOO0OOOO000OO000O =np .zeros ((O00OO0O00OO0O000O .window_size ,O00OO0O00OO0O000O .window_size ,3 ),'uint8')#line:254
        OOOOO00O00OOOOO0O =O00OOO0OOO00OOO0O [:,:,2 ]#line:257
        OOOOO00O00OOOOO0O =np .mean (OOOOO00O00OOOOO0O ,axis =1 )#line:258
        O000O00OOOO0000O0 =np .max (OOO0O0O000OOO0000 [:,:,0 ])#line:260
        O00O00O0OO0O00O0O =np .max (OOO0O0O000OOO0000 [:,:,1 ])#line:261
        OOOOOO00OOO00OOO0 =min (O00OO0O00OO0O000O .window_size /O000O00OOOO0000O0 ,O00OO0O00OO0O000O .window_size /O00O00O0OO0O00O0O )#line:265
        OOO0O0O000OOO0000 =(OOO0O0O000OOO0000 *OOOOOO00OOO00OOO0 ).astype (int )#line:267
        print (OOO0O0O000OOO0000 .shape )#line:268
        O000000OO0O0O00OO =np .argsort (OOOOO00O00OOOOO0O )#line:271
        OOO0O0O000OOO0000 =OOO0O0O000OOO0000 [O000000OO0O0O00OO ]#line:272
        O0O0O0OOO0O0O0000 =O0O0O0OOO0O0O0000 [O000000OO0O0O00OO ]#line:273
        OOO00OOOOOO000O00 =np .sum (np .max (OOO0O0O000OOO0000 ,axis =1 )-np .min (OOO0O0O000OOO0000 ,axis =1 ),axis =1 )#line:276
        for OO0O00O00000O00O0 in range (1 ,np .max (OOO00OOOOOO000O00 )):#line:277
            if np .sum (OOO00OOOOOO000O00 <OO0O00O00000O00O0 )>=min_face_num :#line:278
                O000O00OOO0OO0OOO =OO0O00O00000O00O0 #line:279
                break #line:280
        else :#line:281
            O000O00OOO0OO0OOO =50 #line:282
        print ('cut_size={}, face_num={}'.format (O000O00OOO0OO0OOO ,np .sum (OOO00OOOOOO000O00 <O000O00OOO0OO0OOO )))#line:283
        OOOO00000O0OO0O00 =0 #line:285
        OO0O00OOO0000OO00 =0 #line:286
        for OO0O00O00000O00O0 in range (len (OOO0O0O000OOO0000 [:])):#line:287
            O0OO00O0OOO0OOOO0 =OOO0O0O000OOO0000 [OO0O00O00000O00O0 ]#line:289
            if np .sum (np .max (O0OO00O0OOO0OOOO0 ,axis =0 )-np .min (O0OO00O0OOO0OOOO0 ,axis =0 ))>O000O00OOO0OO0OOO :#line:292
                OO0O00OOO0000OO00 +=1 #line:293
                continue #line:294
            O000OO0OOOOO0OO00 =np .mean (O0O0O0OOO0O0O0000 [OO0O00O00000O00O0 ],axis =0 )#line:296
            O000OO0OOOOO0OO00 =tuple ([int (OOOOO000OO00OOOOO )for OOOOO000OO00OOOOO in O000OO0OOOOO0OO00 ])#line:297
            cv2 .fillPoly (OOO0OOOO000OO000O ,[O0OO00O0OOO0OOOO0 ],O000OO0OOOOO0OO00 )#line:298
            OOOO00000O0OO0O00 +=1 #line:300
            if OOOO00000O0OO0O00 %10000 ==0 :#line:301
                print ('/',end ='')#line:302
            if OOOO00000O0OO0O00 >=300000 :#line:303
                break #line:304
        print ()#line:305
        print ('visible:{}, pass:{}'.format (OOOO00000O0OO0O00 ,OO0O00OOO0000OO00 ))#line:306
        OOO0OOOO000OO000O =cv2 .cvtColor (OOO0OOOO000OO000O ,cv2 .COLOR_RGB2BGR )#line:308
        cv2 .rectangle (OOO0OOOO000OO000O ,(O00OO0O00OO0O000O .window_size *19 //20 ,0 ),(O00OO0O00OO0O000O .window_size ,O00OO0O00OO0O000O .window_size //20 ),(64 ,64 ,64 ),thickness =-1 )#line:310
        cv2 .putText (OOO0OOOO000OO000O ,'Undo',(O00OO0O00OO0O000O .window_size *19 //20 ,O00OO0O00OO0O000O .window_size //20 ),cv2 .FONT_HERSHEY_PLAIN ,1.0 ,(255 ,255 ,255 ),1 )#line:311
        return OOO0OOOO000OO000O ,OOOOOO00OOO00OOO0 #line:313
    def window_zoom_back (O00O00OO0OO0000OO ,O0O00OO0O000OOOO0 ,OOOO0O00O000O00OO ,O00OO0000OOOO0000 ,O00O00OO00OOO0O0O ):#line:316
        O00O0O0O0O0O00000 ,OO000O00O00O0O000 =O0O00OO0O000OOOO0 [:,1 ],O0O00OO0O000OOOO0 [:,2 ]#line:317
        OOO0O0OOO0OO0OO0O =np .zeros ((O00O00OO0OO0000OO .window_size ,O00O00OO0OO0000OO .window_size ,3 ),int )#line:318
        O0O0O0O000000O000 =np .max (O00O0O0O0O0O00000 )#line:320
        O0OO0O000O00OOOO0 =O00O00OO0OO0000OO .window_size /O0O0O0O000000O000 #line:323
        OOO0O0000O0OO0O00 ,O00OOO000000O000O =(O00O0O0O0O0O00000 *O0OO0O000O00OOOO0 ).astype (int ),(OO000O00O00O0O000 *O0OO0O000O00OOOO0 ).astype (int )#line:324
        OO0000OOOOO0OOO0O =int (O00OO0000OOOO0000 *O0OO0O000O00OOOO0 )#line:325
        OOO0OO00OOO00O0O0 =int (O00O00OO00OOO0O0O *O0OO0O000O00OOOO0 )#line:326
        O00OOO000000O000O =(O00OOO000000O000O *-1 )+(O00O00OO0OO0000OO .window_size //2 )#line:329
        OO00000OOOOOO00O0 =O00O00OO0OO0000OO .dot_size #line:331
        for OO00O000OOOOOO0O0 in range (len (O0O00OO0O000OOOO0 )):#line:332
            if OOO0O0000O0OO0O00 [OO00O000OOOOOO0O0 ]+OO00000OOOOOO00O0 <O00O00OO0OO0000OO .window_size and O00OOO000000O000O [OO00O000OOOOOO0O0 ]+OO00000OOOOOO00O0 <O00O00OO0OO0000OO .window_size :#line:333
                OOO0O0OOO0OO0OO0O [O00OOO000000O000O [OO00O000OOOOOO0O0 ]-OO00000OOOOOO00O0 :O00OOO000000O000O [OO00O000OOOOOO0O0 ]+OO00000OOOOOO00O0 ,OOO0O0000O0OO0O00 [OO00O000OOOOOO0O0 ]-OO00000OOOOOO00O0 :OOO0O0000O0OO0O00 [OO00O000OOOOOO0O0 ]+OO00000OOOOOO00O0 ]=OOOO0O00O000O00OO [OO00O000OOOOOO0O0 ]#line:334
        OOO0O0OOO0OO0OO0O [:,OO0000OOOOO0OOO0O ,:]=[0 ,255 ,255 ]#line:337
        OOO0O0OOO0OO0OO0O [:,OOO0OO00OOO00O0O0 ,:]=[0 ,255 ,255 ]#line:338
        O00O00O00OO0OOOOO =Image .fromarray (OOO0O0OOO0OO0OO0O .astype (np .uint8 ))#line:341
        O00O00O00OO0OOOOO =np .array (O00O00O00OO0OOOOO ,dtype =np .uint8 )#line:343
        O00O00O00OO0OOOOO =cv2 .cvtColor (O00O00O00OO0OOOOO ,cv2 .COLOR_RGB2BGR )#line:344
        cv2 .rectangle (O00O00O00OO0OOOOO ,(O00O00OO0OO0000OO .window_size *19 //20 ,0 ),(O00O00OO0OO0000OO .window_size ,O00O00OO0OO0000OO .window_size //20 ),(64 ,64 ,64 ),thickness =-1 )#line:347
        cv2 .putText (O00O00O00OO0OOOOO ,'Undo',(O00O00OO0OO0000OO .window_size *19 //20 ,O00O00OO0OO0000OO .window_size //20 ),cv2 .FONT_HERSHEY_PLAIN ,1.0 ,(255 ,255 ,255 ),1 )#line:348
        return O00O00O00OO0OOOOO ,O0OO0O000O00OOOO0 #line:350
    def window_zoom_side (OOOO0OO00O0OO0O0O ,O0000OOO0000O00O0 ,OO000OOOO0O0O0OOO ,min_face_num =30000 ,z_sort_rev =False ):#line:353
        O000OOO000OOO000O =O0000OOO0000O00O0 [:,:,[0 ,2 ]]#line:355
        OOO000O000O00O0OO =np .zeros ((OOOO0OO00O0OO0O0O .window_size ,OOOO0OO00O0OO0O0O .window_size ,3 ),'uint8')#line:356
        O00O0O00O0OO0OO0O =O0000OOO0000O00O0 [:,:,1 ]#line:359
        O00O0O00O0OO0OO0O =np .mean (O00O0O00O0OO0OO0O ,axis =1 )#line:360
        O0OOOOO000OO0OOOO =np .max (O000OOO000OOO000O [:,:,0 ])#line:362
        OO0OOOO0OOO00O000 =OOOO0OO00O0OO0O0O .window_size /O0OOOOO000OO0OOOO #line:365
        O000OOO000OOO000O =(O000OOO000OOO000O *OO0OOOO0OOO00O000 ).astype (int )#line:367
        print (O000OOO000OOO000O .shape )#line:368
        O000OOO000OOO000O [:,:,1 ]=(O000OOO000OOO000O [:,:,1 ]*-1 )+(OOOO0OO00O0OO0O0O .window_size //2 )#line:371
        O000000O000OO000O =np .argsort (O00O0O00O0OO0OO0O )#line:374
        if z_sort_rev :#line:375
            O000OOO000OOO000O =O000OOO000OOO000O [O000000O000OO000O [::-1 ]]#line:376
            OO000OOOO0O0O0OOO =OO000OOOO0O0O0OOO [O000000O000OO000O [::-1 ]]#line:377
        else :#line:378
            O000OOO000OOO000O =O000OOO000OOO000O [O000000O000OO000O ]#line:379
            OO000OOOO0O0O0OOO =OO000OOOO0O0O0OOO [O000000O000OO000O ]#line:380
        O00OO000O0O0OO0O0 =np .sum (np .max (O000OOO000OOO000O ,axis =1 )-np .min (O000OOO000OOO000O ,axis =1 ),axis =1 )#line:383
        for OO00OOO0OOOO00O00 in range (1 ,np .max (O00OO000O0O0OO0O0 )):#line:384
            if np .sum (O00OO000O0O0OO0O0 <OO00OOO0OOOO00O00 )>=min_face_num :#line:385
                O000000000OOO000O =OO00OOO0OOOO00O00 #line:386
                break #line:387
        else :#line:388
            O000000000OOO000O =9999 #line:389
        print ('cut_size={}, face_num={}'.format (O000000000OOO000O ,np .sum (O00OO000O0O0OO0O0 <O000000000OOO000O )))#line:390
        OO00O0000O00O0O0O =0 #line:392
        O0OO000OOO0O00O0O =0 #line:393
        for OO00OOO0OOOO00O00 in range (len (O000OOO000OOO000O [:])):#line:394
            O0O0O000OO0OO00OO =O000OOO000OOO000O [OO00OOO0OOOO00O00 ]#line:396
            if np .sum (np .max (O0O0O000OO0OO00OO ,axis =0 )-np .min (O0O0O000OO0OO00OO ,axis =0 ))>O000000000OOO000O :#line:399
                continue #line:400
            O0000O0000O0OOOO0 =np .mean (OO000OOOO0O0O0OOO [OO00OOO0OOOO00O00 ],axis =0 )#line:402
            O0000O0000O0OOOO0 =tuple ([int (OOOO0OOO0OO0OOO0O )for OOOO0OOO0OO0OOO0O in O0000O0000O0OOOO0 ])#line:403
            cv2 .fillPoly (OOO000O000O00O0OO ,[O0O0O000OO0OO00OO ],O0000O0000O0OOOO0 )#line:404
            OO00O0000O00O0O0O +=1 #line:406
            if OO00O0000O00O0O0O %10000 ==0 :#line:407
                print ('/',end ='')#line:408
            if OO00O0000O00O0O0O >=300000 :#line:409
                break #line:410
        print ()#line:411
        print ('visible:{}, pass:{}'.format (OO00O0000O00O0O0O ,O0OO000OOO0O00O0O ))#line:412
        OOO000O000O00O0OO =cv2 .cvtColor (OOO000O000O00O0OO ,cv2 .COLOR_RGB2BGR )#line:414
        cv2 .rectangle (OOO000O000O00O0OO ,(OOOO0OO00O0OO0O0O .window_size *19 //20 ,0 ),(OOOO0OO00O0OO0O0O .window_size ,OOOO0OO00O0OO0O0O .window_size //20 ),(64 ,64 ,64 ),thickness =-1 )#line:416
        cv2 .putText (OOO000O000O00O0OO ,'Undo',(OOOO0OO00O0OO0O0O .window_size *19 //20 ,OOOO0OO00O0OO0O0O .window_size //20 ),cv2 .FONT_HERSHEY_PLAIN ,1.0 ,(255 ,255 ,255 ),1 )#line:417
        return OOO000O000O00O0OO ,OO0OOOO0OOO00O000 #line:419
    def put_text (OOO00OOO00OO0000O ,OOOO00OOOOO00000O ,OOOO00O00OOO0O00O ,right =False ):#line:422
        OOO00000O0OO000O0 =20 #line:423
        for O0O0000O0000OOO0O in range (len (OOOO00O00OOO0O00O )):#line:424
            if right :#line:425
                O0OOOOO00O0000O00 =int (OOOO00OOOOO00000O .shape [1 ]/10 *7.5 )#line:426
                cv2 .putText (OOOO00OOOOO00000O ,OOOO00O00OOO0O00O [O0O0000O0000OOO0O ],(O0OOOOO00O0000O00 ,OOO00000O0OO000O0 ),cv2 .FONT_HERSHEY_PLAIN ,1.0 ,(255 ,255 ,0 ),1 )#line:427
            else :#line:428
                cv2 .putText (OOOO00OOOOO00000O ,OOOO00O00OOO0O00O [O0O0000O0000OOO0O ],(5 ,OOO00000O0OO000O0 ),cv2 .FONT_HERSHEY_PLAIN ,1.0 ,(255 ,255 ,0 ),1 )#line:429
            OOO00000O0OO000O0 +=20 #line:430
        return OOOO00OOOOO00000O #line:431
    def gcross (OO00O00OOOOOOO000 ,O0000OOOOO0000000 ,O0O000000OOO0000O ,OOOOO00OO00O00OO0 ):#line:437
        cv2 .line (O0000OOOOO0000000 ,(O0O000000OOO0000O ,0 ),(O0O000000OOO0000O ,OO00O00OOOOOOO000 .h -1 ),(255 ,255 ,0 ))#line:438
        cv2 .line (O0000OOOOO0000000 ,(0 ,OOOOO00OO00O00OO0 ),(OO00O00OOOOOOO000 .w -1 ,OOOOO00OO00O00OO0 ),(255 ,255 ,0 ))#line:439
    def gsquare (O000OO0O000OOO0OO ,O0OOO0O000O00OO00 ,O000O00O0OOOO00OO ,O00OOOO00000O0OOO ,OOO0O0OOO0OO0O0O0 ):#line:441
        OO0O0OOOOOOO0OO0O ,OOOOO0O0O0OO000OO =OOO0O0OOO0OO0O0O0 #line:442
        O00O00OO0OOO0O0O0 =max (abs (O000O00O0OOOO00OO -OO0O0OOOOOOO0OO0O ),abs (O00OOOO00000O0OOO -OOOOO0O0O0OO000OO ))#line:443
        cv2 .rectangle (O0OOO0O000O00OO00 ,(OO0O0OOOOOOO0OO0O -O00O00OO0OOO0O0O0 ,OOOOO0O0O0OO000OO -O00O00OO0OOO0O0O0 ),(OO0O0OOOOOOO0OO0O +O00O00OO0OOO0O0O0 ,OOOOO0O0O0OO000OO +O00O00OO0OOO0O0O0 ),(255 ,255 ,0 ))#line:444
    def gcircle (OO000OOOOO0OOOOO0 ,O0O00OOOOO00O0000 ,OO0O00OO00OOO0O0O ,O00OO0OOO00O00O00 ):#line:446
        cv2 .circle (O0O00OOOOO00O0000 ,(OO0O00OO00OOO0O0O ,O00OO0OOO00O00O00 ),8 ,(255 ,255 ,0 ),1 )#line:447
    def gline (O000000OOOOOOO0O0 ,O0OOOO0OO00O0O0OO ,O00O00OOO0O0OO0OO ,O0OO00OOOO0OOOO0O ,OOO0O0OO0000O0O0O ):#line:449
        cv2 .line (O0OOOO0OO00O0O0OO ,tuple (OOO0O0OO0000O0O0O ),(O00O00OOO0O0OO0OO ,O0OO00OOOO0OOOO0O ),(255 ,255 ,0 ))#line:450
    def ghline (OO0O00O0OO0000O00 ,O0OOOOO0O00O0O000 ,OO000000O0OO0O00O ,OO0000OO00O000O0O ):#line:452
        cv2 .line (O0OOOOO0O00O0O000 ,(0 ,OO0000OO00O000O0O ),(OO0O00O0OO0000O00 .w -1 ,OO0000OO00O000O0O ),(255 ,255 ,0 ))#line:453
    def g_heelhline (OO00OOOOOO0000O00 ,O000OO00O0O0OO0OO ,O0000O0O000OOO0OO ,OO0O0000O00OO000O ,OO00O0O00OOOO0O0O ,O000O0000OO0000O0 ):#line:455
        OOOOOO0OO0OO0O0OO =int (OO00O0O00OOOO0O0O [1 ]*OO00OOOOOO0000O00 .rate1 +O000O0000OO0000O0 [1 ]*(1 -OO00OOOOOO0000O00 .rate1 ))#line:456
        cv2 .line (O000OO00O0O0OO0OO ,(0 ,OOOOOO0OO0OO0O0OO ),(OO00OOOOOO0000O00 .w -1 ,OOOOOO0OO0OO0O0OO ),(255 ,255 ,0 ))#line:457
    def gvline (O00O0O0OOO0O0OOOO ,O0OOOOO0OO0OO0O00 ,O00O000000O00O0OO ,O00O00O0OO0OOO0O0 ):#line:459
        cv2 .line (O0OOOOO0OO0OO0O00 ,(O00O000000O00O0OO ,0 ),(O00O000000O00O0OO ,O00O0O0OOO0O0OOOO .h -1 ),(255 ,255 ,0 ))#line:460
    def gdiagonal (O00O0000OOOO0O0O0 ,OO00O00O0O0OOO00O ,O0O0O0OOO00OO0OOO ,OO0O0OO00OOO0O000 ,O0OOO0O00OO0OOOOO ):#line:462
        O0O000OO000OOOO00 ,OO0O00O0O000000O0 =O0OOO0O00OO0OOOOO #line:463
        O0O0O0OOO00OO0OOO ,OO0O0OO00OOO0O000 =OO0O0OO00OOO0O000 ,O0O0O0OOO00OO0OOO #line:464
        OOOO0O0000OO0OOO0 =math .atan2 (O0O0O0OOO00OO0OOO -OO0O00O0O000000O0 ,OO0O0OO00OOO0O000 -O0O000OO000OOOO00 )#line:467
        OOOOOO0OO0OOO0O0O =math .degrees (OOOO0O0000OO0OOO0 )#line:469
        OO000OOO00OOO0O00 =math .atan2 (O00O0000OOOO0O0O0 .paper_short -0 ,O00O0000OOOO0O0O0 .paper_long -0 )#line:473
        OOOO0OOO0O0OOOO0O =math .degrees (OO000OOO00OOO0O00 )#line:475
        OOO000OO00O0000OO =OOOOOO0OO0OOO0O0O +OOOO0OOO0O0OOOO0O #line:479
        if OOO000OO00O0000OO >180 :#line:480
            OOO000OO00O0000OO =-360 +OOO000OO00O0000OO #line:481
        O00OOOO00OOO0OO00 =math .radians (OOO000OO00O0000OO )#line:484
        O00OOO00OO0O00000 =((O0O0O0OOO00OO0OOO -OO0O00O0O000000O0 )**2 +(OO0O0OO00OOO0O000 -O0O000OO000OOOO00 )**2 )**0.5 #line:487
        O00O0O0O0O00000O0 =(O00O0000OOOO0O0O0 .paper_long **2 +O00O0000OOOO0O0O0 .paper_short **2 )**0.5 #line:488
        OO00O0O0O0OO0O0O0 =O00O0000OOOO0O0O0 .paper_long *(O00OOO00OO0O00000 /O00O0O0O0O00000O0 )#line:490
        OOOO00OO0OOOO0OO0 =O0O000OO000OOOO00 +np .cos (O00OOOO00OOO0OO00 )*OO00O0O0O0OO0O0O0 #line:492
        O000O00OO000OO0O0 =OO0O00O0O000000O0 +np .sin (O00OOOO00OOO0OO00 )*OO00O0O0O0OO0O0O0 #line:493
        cv2 .circle (OO00O00O0O0OOO00O ,(int (OOOO00OO0OOOO0OO0 ),int (O000O00OO000OO0O0 )),8 ,(255 ,255 ,0 ),1 )#line:496
        cv2 .circle (OO00O00O0O0OOO00O ,(OO0O0OO00OOO0O000 -int (OOOO00OO0OOOO0OO0 -O0O000OO000OOOO00 ),O0O0O0OOO00OO0OOO -int (O000O00OO000OO0O0 -OO0O00O0O000000O0 )),8 ,(255 ,255 ,0 ),1 )#line:497
    def onMouse (O000000O0O000OOO0 ,O0OO0000000000000 ,O00OO000000O0000O ,O000OOO0OO0OO00OO ,O0O0OOOO0OOO0000O ,OOO000O00O0O00O0O ):#line:500
        O0O000OO0000O00OO ,OO0OOO00O0O0OOO00 ,OOOO0OO0O0O0O0O0O =OOO000O00O0O00O0O #line:501
        if O0OO0000000000000 ==cv2 .EVENT_MOUSEMOVE :#line:504
            OOO000OOOOOO0000O =np .copy (OO0OOO00O0O0OOO00 )#line:505
            if O0O000OO0000O00OO =='step1':#line:507
                if OOOO0OO0O0O0O0O0O .count ==0 :#line:508
                    O000000O0O000OOO0 .gcross (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO )#line:509
                if OOOO0OO0O0O0O0O0O .count ==1 :#line:510
                    cv2 .circle (OOO000OOOOOO0000O ,tuple (OOOO0OO0O0O0O0O0O .p [0 ]),8 ,(0 ,0 ,255 ),1 )#line:511
                    O000000O0O000OOO0 .gsquare (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO ,OOOO0OO0O0O0O0O0O .p [0 ])#line:512
            if O0O000OO0000O00OO =='step2':#line:514
                if OOOO0OO0O0O0O0O0O .count ==0 :#line:515
                    O000000O0O000OOO0 .gcross (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO )#line:516
                if OOOO0OO0O0O0O0O0O .count ==1 :#line:517
                    cv2 .circle (OOO000OOOOOO0000O ,tuple (OOOO0OO0O0O0O0O0O .p [0 ]),8 ,(0 ,0 ,255 ),1 )#line:518
                    O000000O0O000OOO0 .gcircle (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO )#line:519
                    O000000O0O000OOO0 .gdiagonal (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO ,OOOO0OO0O0O0O0O0O .p [0 ])#line:520
            if O0O000OO0000O00OO =='step3':#line:522
                if OOOO0OO0O0O0O0O0O .count ==0 :#line:523
                    O000000O0O000OOO0 .gcross (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO )#line:524
                if OOOO0OO0O0O0O0O0O .count ==1 :#line:525
                    cv2 .circle (OOO000OOOOOO0000O ,tuple (OOOO0OO0O0O0O0O0O .p [0 ]),8 ,(0 ,0 ,255 ),1 )#line:526
                    O000000O0O000OOO0 .gline (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO ,OOOO0OO0O0O0O0O0O .p [0 ])#line:527
            if O0O000OO0000O00OO =='step4':#line:529
                if OOOO0OO0O0O0O0O0O .count ==0 :#line:530
                    O000000O0O000OOO0 .ghline (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO )#line:531
                if OOOO0OO0O0O0O0O0O .count ==1 :#line:532
                    cv2 .line (OOO000OOOOOO0000O ,(0 ,OOOO0OO0O0O0O0O0O .p [0 ,1 ]),(O000000O0O000OOO0 .w -1 ,OOOO0OO0O0O0O0O0O .p [0 ,1 ]),(0 ,0 ,255 ))#line:533
                    O000000O0O000OOO0 .ghline (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO )#line:534
                if OOOO0OO0O0O0O0O0O .count ==2 :#line:535
                    cv2 .line (OOO000OOOOOO0000O ,(0 ,OOOO0OO0O0O0O0O0O .p [0 ,1 ]),(O000000O0O000OOO0 .w -1 ,OOOO0OO0O0O0O0O0O .p [0 ,1 ]),(0 ,0 ,255 ))#line:536
                    cv2 .line (OOO000OOOOOO0000O ,(0 ,OOOO0OO0O0O0O0O0O .p [1 ,1 ]),(O000000O0O000OOO0 .w -1 ,OOOO0OO0O0O0O0O0O .p [1 ,1 ]),(0 ,0 ,255 ))#line:537
                    O000000O0O000OOO0 .g_heelhline (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO ,OOOO0OO0O0O0O0O0O .p [0 ],OOOO0OO0O0O0O0O0O .p [1 ])#line:538
                    O000000O0O000OOO0 .gvline (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO )#line:539
                if OOOO0OO0O0O0O0O0O .count ==3 :#line:540
                    cv2 .line (OOO000OOOOOO0000O ,(0 ,OOOO0OO0O0O0O0O0O .p [0 ,1 ]),(O000000O0O000OOO0 .w -1 ,OOOO0OO0O0O0O0O0O .p [0 ,1 ]),(0 ,0 ,255 ))#line:541
                    cv2 .line (OOO000OOOOOO0000O ,(0 ,OOOO0OO0O0O0O0O0O .p [1 ,1 ]),(O000000O0O000OOO0 .w -1 ,OOOO0OO0O0O0O0O0O .p [1 ,1 ]),(0 ,0 ,255 ))#line:542
                    O0OO00O0O0OOO0000 =int (OOOO0OO0O0O0O0O0O .p [0 ,1 ]*O000000O0O000OOO0 .rate1 +OOOO0OO0O0O0O0O0O .p [1 ,1 ]*(1 -O000000O0O000OOO0 .rate1 ))#line:543
                    cv2 .circle (OOO000OOOOOO0000O ,tuple ((OOOO0OO0O0O0O0O0O .p [2 ,0 ],O0OO00O0O0OOO0000 )),8 ,(0 ,0 ,255 ),1 )#line:544
                    O000000O0O000OOO0 .g_heelhline (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO ,OOOO0OO0O0O0O0O0O .p [0 ],OOOO0OO0O0O0O0O0O .p [1 ])#line:545
                    O000000O0O000OOO0 .gvline (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO )#line:546
                if OOOO0OO0O0O0O0O0O .count ==4 :#line:547
                    cv2 .line (OOO000OOOOOO0000O ,(0 ,OOOO0OO0O0O0O0O0O .p [0 ,1 ]),(O000000O0O000OOO0 .w -1 ,OOOO0OO0O0O0O0O0O .p [0 ,1 ]),(0 ,0 ,255 ))#line:548
                    cv2 .line (OOO000OOOOOO0000O ,(0 ,OOOO0OO0O0O0O0O0O .p [1 ,1 ]),(O000000O0O000OOO0 .w -1 ,OOOO0OO0O0O0O0O0O .p [1 ,1 ]),(0 ,0 ,255 ))#line:549
                    O0OO00O0O0OOO0000 =int (OOOO0OO0O0O0O0O0O .p [0 ,1 ]*O000000O0O000OOO0 .rate1 +OOOO0OO0O0O0O0O0O .p [1 ,1 ]*(1 -O000000O0O000OOO0 .rate1 ))#line:550
                    cv2 .circle (OOO000OOOOOO0000O ,tuple ((OOOO0OO0O0O0O0O0O .p [2 ,0 ],O0OO00O0O0OOO0000 )),8 ,(0 ,0 ,255 ),1 )#line:551
                    cv2 .circle (OOO000OOOOOO0000O ,tuple ((OOOO0OO0O0O0O0O0O .p [3 ,0 ],O0OO00O0O0OOO0000 )),8 ,(0 ,0 ,255 ),1 )#line:552
                    cv2 .line (OOO000OOOOOO0000O ,(OOOO0OO0O0O0O0O0O .p [2 ,0 ],O0OO00O0O0OOO0000 ),(OOOO0OO0O0O0O0O0O .p [3 ,0 ],O0OO00O0O0OOO0000 ),(0 ,0 ,255 ))#line:553
                    O000000O0O000OOO0 .gcross (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO )#line:554
                if OOOO0OO0O0O0O0O0O .count ==5 :#line:555
                    cv2 .line (OOO000OOOOOO0000O ,(0 ,OOOO0OO0O0O0O0O0O .p [0 ,1 ]),(O000000O0O000OOO0 .w -1 ,OOOO0OO0O0O0O0O0O .p [0 ,1 ]),(0 ,0 ,255 ))#line:556
                    cv2 .line (OOO000OOOOOO0000O ,(0 ,OOOO0OO0O0O0O0O0O .p [1 ,1 ]),(O000000O0O000OOO0 .w -1 ,OOOO0OO0O0O0O0O0O .p [1 ,1 ]),(0 ,0 ,255 ))#line:557
                    O0OO00O0O0OOO0000 =int (OOOO0OO0O0O0O0O0O .p [0 ,1 ]*O000000O0O000OOO0 .rate1 +OOOO0OO0O0O0O0O0O .p [1 ,1 ]*(1 -O000000O0O000OOO0 .rate1 ))#line:558
                    cv2 .circle (OOO000OOOOOO0000O ,tuple ((OOOO0OO0O0O0O0O0O .p [2 ,0 ],O0OO00O0O0OOO0000 )),8 ,(0 ,0 ,255 ),1 )#line:559
                    cv2 .circle (OOO000OOOOOO0000O ,tuple ((OOOO0OO0O0O0O0O0O .p [3 ,0 ],O0OO00O0O0OOO0000 )),8 ,(0 ,0 ,255 ),1 )#line:560
                    cv2 .line (OOO000OOOOOO0000O ,(OOOO0OO0O0O0O0O0O .p [2 ,0 ],O0OO00O0O0OOO0000 ),(OOOO0OO0O0O0O0O0O .p [3 ,0 ],O0OO00O0O0OOO0000 ),(0 ,0 ,255 ))#line:561
                    cv2 .circle (OOO000OOOOOO0000O ,tuple (OOOO0OO0O0O0O0O0O .p [4 ]),8 ,(0 ,0 ,255 ),1 )#line:562
                    O000000O0O000OOO0 .gline (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO ,OOOO0OO0O0O0O0O0O .p [4 ])#line:563
            if O0O000OO0000O00OO in ['step5','step7']:#line:566
                cv2 .line (OOO000OOOOOO0000O ,(0 ,O000000O0O000OOO0 .window_size //2 ),(O000000O0O000OOO0 .w -1 ,O000000O0O000OOO0 .window_size //2 ),(255 ,255 ,0 ))#line:567
                if O000000O0O000OOO0 .t >0 :#line:569
                    cv2 .line (OOO000OOOOOO0000O ,tuple (OOOO0OO0O0O0O0O0O .p [0 ]),tuple (OOOO0OO0O0O0O0O0O .p [OOOO0OO0O0O0O0O0O .count -2 ]),(0 ,0 ,255 ))#line:570
                    OOOO0OO0O0O0O0O0O .npoints =OOOO0OO0O0O0O0O0O .count #line:571
                    time .sleep (1 )#line:572
                elif OOOO0OO0O0O0O0O0O .count >0 and O000OOO0OO0OO00OO <=(O000000O0O000OOO0 .window_size *2 //3 ):#line:574
                    cv2 .circle (OOO000OOOOOO0000O ,tuple (OOOO0OO0O0O0O0O0O .p [0 ]),8 ,(0 ,0 ,255 ),1 )#line:575
                    for O00O000000OOO00O0 in range (1 ,OOOO0OO0O0O0O0O0O .count ):#line:576
                        cv2 .line (OOO000OOOOOO0000O ,tuple (OOOO0OO0O0O0O0O0O .p [O00O000000OOO00O0 -1 ]),tuple (OOOO0OO0O0O0O0O0O .p [O00O000000OOO00O0 ]),(0 ,0 ,255 ))#line:577
                    O000000O0O000OOO0 .gline (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO ,OOOO0OO0O0O0O0O0O .p [OOOO0OO0O0O0O0O0O .count -1 ])#line:578
                elif OOOO0OO0O0O0O0O0O .count >0 and O000OOO0OO0OO00OO >(O000000O0O000OOO0 .window_size *2 //3 ):#line:580
                    cv2 .circle (OOO000OOOOOO0000O ,tuple (OOOO0OO0O0O0O0O0O .p [0 ]),8 ,(0 ,0 ,255 ),1 )#line:581
                    for O00O000000OOO00O0 in range (1 ,OOOO0OO0O0O0O0O0O .count ):#line:582
                        cv2 .line (OOO000OOOOOO0000O ,tuple (OOOO0OO0O0O0O0O0O .p [O00O000000OOO00O0 -1 ]),tuple (OOOO0OO0O0O0O0O0O .p [O00O000000OOO00O0 ]),(0 ,0 ,255 ))#line:583
                    cv2 .line (OOO000OOOOOO0000O ,tuple (OOOO0OO0O0O0O0O0O .p [OOOO0OO0O0O0O0O0O .count -1 ]),tuple (OOOO0OO0O0O0O0O0O .p [0 ]),(255 ,255 ,0 ))#line:584
            if O0O000OO0000O00OO =='step6':#line:586
                if O000000O0O000OOO0 .qqq1 ==0 :#line:587
                    for O00O000000OOO00O0 in range (O000000O0O000OOO0 .w ):#line:589
                        if np .sum (np .abs (OO0OOO00O0O0OOO00 [O000OOO0OO0OO00OO ,O00O000000OOO00O0 ]-np .array ([255 ,255 ,0 ],int )))==0 :#line:590
                            O000000O0O000OOO0 .qqq1 =O00O000000OOO00O0 #line:591
                            break #line:592
                    for O00O000000OOO00O0 in range (O000000O0O000OOO0 .w ):#line:593
                        if np .sum (np .abs (OO0OOO00O0O0OOO00 [O000OOO0OO0OO00OO ,O00O000000OOO00O0 ]-np .array ([255 ,254 ,0 ],int )))==0 :#line:594
                            O000000O0O000OOO0 .qqq2 =O00O000000OOO00O0 #line:595
                            break #line:596
                O000000O0O000OOO0 .ghline (OOO000OOOOOO0000O ,O00OO000000O0000O ,O000OOO0OO0OO00OO )#line:598
                cv2 .line (OOO000OOOOOO0000O ,(O000000O0O000OOO0 .qqq1 ,O000OOO0OO0OO00OO ),(O000000O0O000OOO0 .qqq2 ,O000000O0O000OOO0 .window_size //2 ),(255 ,255 ,0 ))#line:599
            cv2 .imshow (O0O000OO0000O00OO ,OOO000OOOOOO0000O )#line:601
        if O0OO0000000000000 ==cv2 .EVENT_LBUTTONDOWN :#line:604
            if O000000O0O000OOO0 .window_size *19 //20 <O00OO000000O0000O <O000000O0O000OOO0 .window_size and 0 <O000OOO0OO0OO00OO <O000000O0O000OOO0 .window_size //20 :#line:607
                if OOOO0OO0O0O0O0O0O .count ==0 :#line:608
                    pass #line:609
                else :#line:610
                    OOOO0OO0O0O0O0O0O .count -=1 #line:611
                    OOOO0OO0O0O0O0O0O .p [OOOO0OO0O0O0O0O0O .count ,:]==np .empty (2 ,dtype =int )#line:612
            else :#line:616
                OOOO0OO0O0O0O0O0O .add (O00OO000000O0000O ,O000OOO0OO0OO00OO )#line:618
                print ('pointlist[{}] = ({}, {})'.format (OOOO0OO0O0O0O0O0O .count -1 ,O00OO000000O0000O ,O000OOO0OO0OO00OO ))#line:619
                if O0O000OO0000O00OO in ['step5','step7']:#line:621
                    if O000OOO0OO0OO00OO >(O000000O0O000OOO0 .window_size *2 //3 ):#line:622
                        O000000O0O000OOO0 .t =time .time ()#line:624
        if OOOO0OO0O0O0O0O0O .count ==OOOO0OO0O0O0O0O0O .npoints :#line:629
            cv2 .destroyWindow (O0O000OO0000O00OO )#line:630
            if O0O000OO0000O00OO in ['step5','step7']:#line:631
                O000000O0O000OOO0 .p =OOOO0OO0O0O0O0O0O .p [:OOOO0OO0O0O0O0O0O .count -1 ]#line:632
            else :#line:633
                O000000O0O000OOO0 .p =OOOO0OO0O0O0O0O0O .p #line:634
if __name__ =='__main__':#line:638
    pass #line:639
