# Step 0: Remove items in parentheses from raw subtitles
# these are usually speaker tags that are not spoken

import pysubs2
import re

subs = pysubs2.load("nichibros1.ass", encoding="utf-8")
for line in subs:
    line.text = re.sub(r"[\(\（].+[\)\）]\s?", "", line.text)
subs.save("nichibros1.no-parens.ass")