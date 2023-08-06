'''
Created by yong.huang on 2016.11.04
'''
'''
Created by yong.huang on 2016.11.04
'''
from enum import Enum


class HFBitRateEnum(Enum):
	# 为序列值指定value值
	WAV_320 = ("wav", "320")
	DEFAULT =("mp3", "320")
	MP3_128 =("mp3", "128")
	AAC_320 =("aac", "320")

