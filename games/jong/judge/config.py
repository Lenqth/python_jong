# -*- coding:utf-8 -*-

#
# 七対子において、四枚使いを許可する。
# 日本麻雀では一般的ではありませんが、中国麻雀では認められます
#

ALLOW_FOUR_IN_7PAIRS = True

ALLOW_KNITTED = True
ALLOW_KNITTED_NORMAL = True


#すべての牌が1~9かつ枚数が4枚以内で有ることを仮定して、チェックを省略します
#高速化しますが、条件が満たされていない場合壊れる場合があります
ORTHODOX_MODE = True
