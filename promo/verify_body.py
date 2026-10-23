# -*- coding: utf-8 -*-
"""验证推文正文：豁免引用块和「」『』内的坏例提及后，是否零病灶。"""
import re

src = open('renhua').read().replace('if __name__ ==', 'if False and __name__ ==')
ns = {'__file__': 'renhua'}
exec(src, ns)

text = open('promo/article.md', encoding='utf-8').read()
t = ns['strip_quotes'](ns['strip_code_blocks'](text))
# 「」『』内的提及替换为空白（保留字数结构，行号不变）
t = re.sub('「[^」]{1,30}」', lambda m: re.sub(r'\S', ' ', m.group(0)), t)
t = re.sub('『[^』]{1,30}』', lambda m: re.sub(r'\S', ' ', m.group(0)), t)

rules = ns['load_rules']()
score, hits, n = ns['analyze'](t, rules, skip_code=False, skip_quotes=False)
print('推文正文（豁免引用块+引号提及）：', score, '分，', len(hits), '类病灶')
for h in hits:
    print(' ', h['name'], 'x%d 行%s' % (h['hits'], h['lines']))
